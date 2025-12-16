# =============================================================================
# Service Accounts Module
# =============================================================================
# Creates and configures service accounts for Genesis NGX services.
#
# Service Accounts:
# - gateway: For Cloud Run gateway service
# - agents: For Vertex AI Agent Engine agents
# =============================================================================

locals {
  env_suffix = var.environment == "prod" ? "" : "-${var.environment}"
}

# =============================================================================
# Gateway Service Account
# =============================================================================

resource "google_service_account" "gateway" {
  project      = var.project_id
  account_id   = "genesis-gateway${local.env_suffix}"
  display_name = "Genesis NGX Gateway (${var.environment})"
  description  = "Service account for the Genesis NGX API Gateway on Cloud Run"
}

# Gateway needs to invoke Vertex AI Agent Engine
resource "google_project_iam_member" "gateway_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.gateway.email}"
}

# Gateway needs to access secrets
resource "google_project_iam_member" "gateway_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.gateway.email}"
}

# Gateway needs to write logs
resource "google_project_iam_member" "gateway_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gateway.email}"
}

# Gateway needs to write metrics
resource "google_project_iam_member" "gateway_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gateway.email}"
}

# Gateway needs to create trace spans
resource "google_project_iam_member" "gateway_trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.gateway.email}"
}

# =============================================================================
# Agents Service Account
# =============================================================================

resource "google_service_account" "agents" {
  project      = var.project_id
  account_id   = "genesis-agents${local.env_suffix}"
  display_name = "Genesis NGX Agents (${var.environment})"
  description  = "Service account for Genesis NGX agents on Vertex AI Agent Engine"
}

# Agents need full Vertex AI access for Gemini models
resource "google_project_iam_member" "agents_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agents.email}"
}

# Agents need to access secrets (for Supabase credentials)
resource "google_project_iam_member" "agents_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.agents.email}"
}

# Agents need to write logs
resource "google_project_iam_member" "agents_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.agents.email}"
}
