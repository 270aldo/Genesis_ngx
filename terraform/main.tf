# =============================================================================
# Genesis NGX - Main Terraform Configuration
# =============================================================================
# This file orchestrates all infrastructure for Genesis NGX on GCP.
#
# Resources managed:
# - Google Cloud APIs (via apis.tf)
# - Workload Identity Federation (for GitHub Actions)
# - Service Accounts (gateway, agents)
# - Secret Manager secrets
# - Budget alerts
# - Cloud Run service (gateway)
# =============================================================================

# =============================================================================
# Local Variables
# =============================================================================

locals {
  # Common labels for all resources
  common_labels = {
    project     = "genesis-ngx"
    environment = var.environment
    managed_by  = "terraform"
  }

  # Service account emails
  gateway_sa_email = module.service_accounts.gateway_sa_email
}

# =============================================================================
# Workload Identity Federation (GitHub Actions → GCP)
# =============================================================================

module "workload_identity" {
  source = "./modules/workload-identity"

  project_id      = var.project_id
  pool_id         = "github-actions-pool"
  provider_id     = "github-actions-provider"
  github_org      = var.github_org
  github_repo     = var.github_repo
  service_account = local.gateway_sa_email

  depends_on = [google_project_service.apis]
}

# =============================================================================
# Service Accounts
# =============================================================================

module "service_accounts" {
  source = "./modules/service-accounts"

  project_id  = var.project_id
  environment = var.environment

  depends_on = [google_project_service.apis]
}

# =============================================================================
# Secret Manager
# =============================================================================

resource "google_secret_manager_secret" "supabase_url" {
  project   = var.project_id
  secret_id = "supabase-url"

  labels = local.common_labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "supabase_anon_key" {
  project   = var.project_id
  secret_id = "supabase-anon-key"

  labels = local.common_labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "supabase_service_role_key" {
  project   = var.project_id
  secret_id = "supabase-service-role-key"

  labels = local.common_labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "supabase_jwt_secret" {
  project   = var.project_id
  secret_id = "supabase-jwt-secret"

  labels = local.common_labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

# Grant gateway service account access to secrets
resource "google_secret_manager_secret_iam_member" "gateway_supabase_url" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.supabase_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.gateway_sa_email}"
}

resource "google_secret_manager_secret_iam_member" "gateway_supabase_anon_key" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.supabase_anon_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.gateway_sa_email}"
}

resource "google_secret_manager_secret_iam_member" "gateway_supabase_service_role" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.supabase_service_role_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.gateway_sa_email}"
}

resource "google_secret_manager_secret_iam_member" "gateway_supabase_jwt" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.supabase_jwt_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.gateway_sa_email}"
}

# =============================================================================
# Budget Alerts
# =============================================================================

resource "google_billing_budget" "genesis_ngx" {
  billing_account = var.billing_account_id
  display_name    = "Genesis NGX ${var.environment} Budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget_usd
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.8
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = []
    disable_default_iam_recipients   = false
  }
}

# =============================================================================
# Outputs
# =============================================================================

output "workload_identity_provider" {
  description = "Workload Identity Provider for GitHub Actions"
  value       = module.workload_identity.provider_name
}

output "gateway_service_account" {
  description = "Gateway service account email"
  value       = local.gateway_sa_email
}

output "secret_ids" {
  description = "Secret Manager secret IDs"
  value = {
    supabase_url              = google_secret_manager_secret.supabase_url.secret_id
    supabase_anon_key         = google_secret_manager_secret.supabase_anon_key.secret_id
    supabase_service_role_key = google_secret_manager_secret.supabase_service_role_key.secret_id
    supabase_jwt_secret       = google_secret_manager_secret.supabase_jwt_secret.secret_id
  }
}
