-- Migration: Gateway Schema Alignment
-- Description: Adds missing columns and RPCs required by the Gateway
-- Date: 2025-12-15
-- Fixes: Codex analysis issues (title, updated_at, user_create_conversation RPC)

-- =============================================================================
-- ALTER: conversations table - Add missing columns
-- =============================================================================

-- Add title column (optional, for conversation naming)
ALTER TABLE public.conversations
ADD COLUMN IF NOT EXISTS title text;

-- Add updated_at column with default
ALTER TABLE public.conversations
ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();

-- Add aggregation columns for conversation stats
ALTER TABLE public.conversations
ADD COLUMN IF NOT EXISTS message_count integer DEFAULT 0;

ALTER TABLE public.conversations
ADD COLUMN IF NOT EXISTS total_tokens integer DEFAULT 0;

ALTER TABLE public.conversations
ADD COLUMN IF NOT EXISTS total_cost_usd numeric(10,6) DEFAULT 0;

-- Create index for updated_at ordering (used in list queries)
CREATE INDEX IF NOT EXISTS idx_conversations_updated
ON public.conversations(user_id, updated_at DESC);

-- =============================================================================
-- FUNCTION: Auto-update updated_at on conversations
-- =============================================================================

CREATE OR REPLACE FUNCTION public.update_conversation_timestamp()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE public.conversations
    SET updated_at = now()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$;

-- Create trigger to update conversation timestamp when messages are added
DROP TRIGGER IF EXISTS trg_update_conversation_timestamp ON public.messages;
CREATE TRIGGER trg_update_conversation_timestamp
    AFTER INSERT ON public.messages
    FOR EACH ROW
    EXECUTE FUNCTION public.update_conversation_timestamp();

-- =============================================================================
-- FUNCTION: Update conversation stats on message insert
-- =============================================================================

CREATE OR REPLACE FUNCTION public.update_conversation_stats()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE public.conversations
    SET
        message_count = message_count + 1,
        total_tokens = total_tokens + COALESCE(NEW.tokens_used, 0),
        total_cost_usd = total_cost_usd + COALESCE(NEW.cost_usd, 0)
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$;

-- Create trigger to update conversation stats
DROP TRIGGER IF EXISTS trg_update_conversation_stats ON public.messages;
CREATE TRIGGER trg_update_conversation_stats
    AFTER INSERT ON public.messages
    FOR EACH ROW
    EXECUTE FUNCTION public.update_conversation_stats();

-- =============================================================================
-- RPC: user_create_conversation
-- =============================================================================

CREATE OR REPLACE FUNCTION rpc.user_create_conversation(
    p_user_id uuid,
    p_title text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_conversation_id uuid;
    v_caller_id uuid;
BEGIN
    -- Get the calling user's ID
    v_caller_id := auth.uid();

    -- If called with service_role, allow any user_id
    -- If called with user JWT, ensure they can only create for themselves
    IF v_caller_id IS NOT NULL AND v_caller_id <> p_user_id THEN
        RAISE EXCEPTION 'Forbidden: cannot create conversation for another user';
    END IF;

    -- Create the conversation
    INSERT INTO public.conversations (
        user_id,
        title,
        status,
        created_at,
        updated_at
    ) VALUES (
        p_user_id,
        p_title,
        'active',
        now(),
        now()
    ) RETURNING id INTO v_conversation_id;

    RETURN v_conversation_id;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.user_create_conversation(uuid, text) TO authenticated;
GRANT EXECUTE ON FUNCTION rpc.user_create_conversation(uuid, text) TO service_role;

-- =============================================================================
-- RPC: user_archive_conversation
-- =============================================================================

CREATE OR REPLACE FUNCTION rpc.user_archive_conversation(
    p_conversation_id uuid
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_owner_id uuid;
BEGIN
    -- Get conversation owner
    SELECT user_id INTO v_owner_id
    FROM public.conversations
    WHERE id = p_conversation_id;

    IF v_owner_id IS NULL THEN
        RAISE EXCEPTION 'Conversation not found';
    END IF;

    -- Check ownership (if called with user JWT)
    IF auth.uid() IS NOT NULL AND auth.uid() <> v_owner_id THEN
        RAISE EXCEPTION 'Forbidden: not conversation owner';
    END IF;

    -- Archive the conversation
    UPDATE public.conversations
    SET
        status = 'archived',
        updated_at = now()
    WHERE id = p_conversation_id;

    RETURN true;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.user_archive_conversation(uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION rpc.user_archive_conversation(uuid) TO service_role;

-- =============================================================================
-- UPDATE: Modify agent_append_message to work with service_role
-- =============================================================================

-- The existing RPC requires agent_role claim which won't exist with service_role.
-- Create an alternative for gateway that uses service_role authentication.

CREATE OR REPLACE FUNCTION rpc.gateway_append_agent_message(
    p_conversation_id uuid,
    p_user_id uuid,
    p_agent_type text,
    p_content text,
    p_tokens_used integer DEFAULT NULL,
    p_cost_usd numeric(10,6) DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_owner uuid;
    v_message_id uuid;
BEGIN
    -- Verify conversation exists and belongs to user
    SELECT user_id INTO v_owner
    FROM public.conversations
    WHERE id = p_conversation_id;

    IF v_owner IS NULL THEN
        RAISE EXCEPTION 'Conversation not found';
    END IF;

    IF v_owner <> p_user_id THEN
        RAISE EXCEPTION 'Forbidden: conversation does not belong to user';
    END IF;

    -- Insert the message with role='agent'
    INSERT INTO public.messages (
        conversation_id,
        role,
        agent_type,
        content,
        tokens_used,
        cost_usd
    ) VALUES (
        p_conversation_id,
        'agent',  -- Use 'agent' not 'assistant' to match constraint
        p_agent_type,
        p_content,
        p_tokens_used,
        p_cost_usd
    ) RETURNING id INTO v_message_id;

    -- Log the event
    INSERT INTO public.agent_events (
        user_id,
        agent_type,
        event_type,
        payload
    ) VALUES (
        v_owner,
        p_agent_type,
        'message_appended',
        jsonb_build_object(
            'message_id', v_message_id,
            'tokens_used', p_tokens_used,
            'cost_usd', p_cost_usd,
            'via', 'gateway'
        )
    );

    RETURN v_message_id;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.gateway_append_agent_message(uuid, uuid, text, text, integer, numeric) TO service_role;

-- =============================================================================
-- UPDATE: Modify user_append_message to work with service_role
-- =============================================================================

CREATE OR REPLACE FUNCTION rpc.gateway_append_user_message(
    p_conversation_id uuid,
    p_user_id uuid,
    p_content text
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_owner uuid;
    v_message_id uuid;
BEGIN
    -- Verify conversation exists and belongs to user
    SELECT user_id INTO v_owner
    FROM public.conversations
    WHERE id = p_conversation_id;

    IF v_owner IS NULL THEN
        RAISE EXCEPTION 'Conversation not found';
    END IF;

    IF v_owner <> p_user_id THEN
        RAISE EXCEPTION 'Forbidden: conversation does not belong to user';
    END IF;

    -- Insert the message
    INSERT INTO public.messages (
        conversation_id,
        role,
        content
    ) VALUES (
        p_conversation_id,
        'user',
        p_content
    ) RETURNING id INTO v_message_id;

    RETURN v_message_id;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.gateway_append_user_message(uuid, uuid, text) TO service_role;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON COLUMN public.conversations.title IS 'Optional user-defined title for the conversation';
COMMENT ON COLUMN public.conversations.updated_at IS 'Last update timestamp, auto-updated on message insert';
COMMENT ON COLUMN public.conversations.message_count IS 'Total number of messages in conversation';
COMMENT ON COLUMN public.conversations.total_tokens IS 'Total tokens used across all messages';
COMMENT ON COLUMN public.conversations.total_cost_usd IS 'Total cost in USD across all messages';

COMMENT ON FUNCTION rpc.user_create_conversation IS 'Create a new conversation for a user';
COMMENT ON FUNCTION rpc.user_archive_conversation IS 'Archive (soft-delete) a conversation';
COMMENT ON FUNCTION rpc.gateway_append_agent_message IS 'Append agent message via gateway (service_role)';
COMMENT ON FUNCTION rpc.gateway_append_user_message IS 'Append user message via gateway (service_role)';
