# =============================================================================
# Terraform Backend Configuration
# =============================================================================
# Remote state storage in Google Cloud Storage for team collaboration
# and state locking via GCS object versioning.
#
# IMPORTANT: Before first use, create the bucket manually:
#   gsutil mb -p ${PROJECT_ID} -l us-central1 gs://${PROJECT_ID}-terraform-state
#   gsutil versioning set on gs://${PROJECT_ID}-terraform-state
# =============================================================================

terraform {
  backend "gcs" {
    # Bucket name is set via -backend-config during init
    # Example: terraform init -backend-config="bucket=ngx-genesis-prod-terraform-state"
    prefix = "genesis-ngx/state"
  }
}

# =============================================================================
# Backend Configuration by Environment
# =============================================================================
#
# Development:
#   terraform init -backend-config="bucket=ngx-genesis-dev-terraform-state"
#
# Staging:
#   terraform init -backend-config="bucket=ngx-genesis-staging-terraform-state"
#
# Production:
#   terraform init -backend-config="bucket=ngx-genesis-prod-terraform-state"
#
# =============================================================================
