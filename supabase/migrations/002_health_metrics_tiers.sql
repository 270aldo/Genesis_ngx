-- Migration: Health Metrics Tiers System
-- Description: Implements tiered consent system for health data per ADR-008
-- Date: 2025-12-14

-- =============================================================================
-- ENUM: Metric Types (Tier 1 + Tier 2)
-- =============================================================================

-- Create enum for allowed metric types
-- This ensures only approved metric types can be stored
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'metric_type_enum') THEN
        CREATE TYPE metric_type_enum AS ENUM (
            -- Tier 1: Habilitado por defecto
            'weight_kg',
            'height_cm',
            'steps_daily',
            'active_minutes',
            'calories_burned',
            'water_ml',
            'sleep_hours',
            -- Tier 2: Requiere consentimiento adicional
            'body_fat_percentage',
            'muscle_mass_kg',
            'resting_hr_bpm',
            'sleep_quality_score'
        );
    END IF;
END$$;

-- =============================================================================
-- TABLE: Metric Type Configuration
-- =============================================================================

-- Reference table for metric type metadata
CREATE TABLE IF NOT EXISTS public.metric_type_config (
    metric_type text PRIMARY KEY,
    tier integer NOT NULL CHECK (tier IN (1, 2)),
    display_name_es text NOT NULL,
    display_name_en text NOT NULL,
    unit text NOT NULL,
    description_es text,
    min_value numeric,
    max_value numeric,
    created_at timestamptz DEFAULT now()
);

-- Insert Tier 1 metrics (enabled by default)
INSERT INTO public.metric_type_config (metric_type, tier, display_name_es, display_name_en, unit, description_es, min_value, max_value) VALUES
    ('weight_kg', 1, 'Peso', 'Weight', 'kg', 'Peso corporal en kilogramos', 20, 300),
    ('height_cm', 1, 'Altura', 'Height', 'cm', 'Altura en centímetros', 50, 250),
    ('steps_daily', 1, 'Pasos diarios', 'Daily Steps', 'count', 'Número de pasos en el día', 0, 100000),
    ('active_minutes', 1, 'Minutos activos', 'Active Minutes', 'min', 'Minutos de actividad física', 0, 1440),
    ('calories_burned', 1, 'Calorías quemadas', 'Calories Burned', 'kcal', 'Calorías quemadas por actividad', 0, 10000),
    ('water_ml', 1, 'Hidratación', 'Hydration', 'ml', 'Consumo de agua en mililitros', 0, 10000),
    ('sleep_hours', 1, 'Horas de sueño', 'Sleep Hours', 'hours', 'Horas de sueño', 0, 24)
ON CONFLICT (metric_type) DO NOTHING;

-- Insert Tier 2 metrics (require additional consent)
INSERT INTO public.metric_type_config (metric_type, tier, display_name_es, display_name_en, unit, description_es, min_value, max_value) VALUES
    ('body_fat_percentage', 2, 'Grasa corporal', 'Body Fat', '%', 'Porcentaje de grasa corporal', 1, 70),
    ('muscle_mass_kg', 2, 'Masa muscular', 'Muscle Mass', 'kg', 'Masa muscular en kilogramos', 10, 100),
    ('resting_hr_bpm', 2, 'FC en reposo', 'Resting HR', 'bpm', 'Frecuencia cardíaca en reposo', 30, 200),
    ('sleep_quality_score', 2, 'Calidad de sueño', 'Sleep Quality', 'score', 'Puntuación de calidad de sueño (1-100)', 1, 100)
ON CONFLICT (metric_type) DO NOTHING;

-- =============================================================================
-- TABLE: User Consents
-- =============================================================================

-- Track user consent for different data tiers
CREATE TABLE IF NOT EXISTS public.user_consents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    consent_type text NOT NULL CHECK (consent_type IN ('privacy_policy', 'tier2_health_data', 'marketing')),
    consent_version text NOT NULL,
    granted boolean NOT NULL DEFAULT false,
    granted_at timestamptz,
    revoked_at timestamptz,
    ip_address inet,
    user_agent text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE (user_id, consent_type)
);

CREATE INDEX IF NOT EXISTS idx_user_consents_user ON public.user_consents(user_id);

-- =============================================================================
-- MODIFY: health_metrics table
-- =============================================================================

-- Add constraint to ensure only allowed metric types are stored
-- First, check if constraint exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'health_metrics_metric_type_check'
    ) THEN
        ALTER TABLE public.health_metrics
        ADD CONSTRAINT health_metrics_metric_type_check
        CHECK (metric_type IN (
            'weight_kg', 'height_cm', 'steps_daily', 'active_minutes',
            'calories_burned', 'water_ml', 'sleep_hours',
            'body_fat_percentage', 'muscle_mass_kg', 'resting_hr_bpm', 'sleep_quality_score'
        ));
    END IF;
END$$;

-- =============================================================================
-- RLS: User Consents
-- =============================================================================

ALTER TABLE public.user_consents ENABLE ROW LEVEL SECURITY;

-- Users can read their own consents
DROP POLICY IF EXISTS "Users read own consents" ON public.user_consents;
CREATE POLICY "Users read own consents" ON public.user_consents
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own consents
DROP POLICY IF EXISTS "Users insert own consents" ON public.user_consents;
CREATE POLICY "Users insert own consents" ON public.user_consents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own consents (revoke)
DROP POLICY IF EXISTS "Users update own consents" ON public.user_consents;
CREATE POLICY "Users update own consents" ON public.user_consents
    FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- =============================================================================
-- FUNCTION: Check if user has Tier 2 consent
-- =============================================================================

CREATE OR REPLACE FUNCTION public.user_has_tier2_consent(p_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.user_consents
        WHERE user_id = p_user_id
        AND consent_type = 'tier2_health_data'
        AND granted = true
        AND revoked_at IS NULL
    );
$$;

-- =============================================================================
-- FUNCTION: Validate metric insert based on tier consent
-- =============================================================================

CREATE OR REPLACE FUNCTION public.validate_health_metric_tier()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_tier integer;
    v_has_consent boolean;
BEGIN
    -- Get the tier for this metric type
    SELECT tier INTO v_tier
    FROM public.metric_type_config
    WHERE metric_type = NEW.metric_type;

    -- If metric type not found, reject
    IF v_tier IS NULL THEN
        RAISE EXCEPTION 'Invalid metric_type: %', NEW.metric_type;
    END IF;

    -- Tier 1 metrics are always allowed
    IF v_tier = 1 THEN
        RETURN NEW;
    END IF;

    -- Tier 2 metrics require consent
    v_has_consent := public.user_has_tier2_consent(NEW.user_id);

    IF NOT v_has_consent THEN
        RAISE EXCEPTION 'User has not consented to Tier 2 health data collection';
    END IF;

    RETURN NEW;
END;
$$;

-- Create trigger for health_metrics inserts
DROP TRIGGER IF EXISTS trg_validate_health_metric_tier ON public.health_metrics;
CREATE TRIGGER trg_validate_health_metric_tier
    BEFORE INSERT ON public.health_metrics
    FOR EACH ROW
    EXECUTE FUNCTION public.validate_health_metric_tier();

-- =============================================================================
-- RPC: Grant consent
-- =============================================================================

CREATE OR REPLACE FUNCTION rpc.grant_consent(
    p_consent_type text,
    p_consent_version text,
    p_ip_address text DEFAULT NULL,
    p_user_agent text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_user_id uuid;
    v_consent_id uuid;
BEGIN
    v_user_id := auth.uid();

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Unauthorized';
    END IF;

    INSERT INTO public.user_consents (
        user_id,
        consent_type,
        consent_version,
        granted,
        granted_at,
        ip_address,
        user_agent
    ) VALUES (
        v_user_id,
        p_consent_type,
        p_consent_version,
        true,
        now(),
        p_ip_address::inet,
        p_user_agent
    )
    ON CONFLICT (user_id, consent_type)
    DO UPDATE SET
        consent_version = EXCLUDED.consent_version,
        granted = true,
        granted_at = now(),
        revoked_at = NULL,
        ip_address = EXCLUDED.ip_address,
        user_agent = EXCLUDED.user_agent,
        updated_at = now()
    RETURNING id INTO v_consent_id;

    RETURN v_consent_id;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.grant_consent(text, text, text, text) TO authenticated;

-- =============================================================================
-- RPC: Revoke consent
-- =============================================================================

CREATE OR REPLACE FUNCTION rpc.revoke_consent(
    p_consent_type text
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_user_id uuid;
BEGIN
    v_user_id := auth.uid();

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Unauthorized';
    END IF;

    UPDATE public.user_consents
    SET
        granted = false,
        revoked_at = now(),
        updated_at = now()
    WHERE user_id = v_user_id
    AND consent_type = p_consent_type;

    RETURN FOUND;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.revoke_consent(text) TO authenticated;

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE public.metric_type_config IS 'Reference table for allowed health metric types with tier classification';
COMMENT ON TABLE public.user_consents IS 'Tracks user consent for different data collection tiers';
COMMENT ON FUNCTION public.user_has_tier2_consent IS 'Checks if user has active Tier 2 health data consent';
COMMENT ON FUNCTION public.validate_health_metric_tier IS 'Trigger function to validate metric tier consent before insert';
COMMENT ON FUNCTION rpc.grant_consent IS 'RPC to grant consent for a specific type';
COMMENT ON FUNCTION rpc.revoke_consent IS 'RPC to revoke consent for a specific type';
