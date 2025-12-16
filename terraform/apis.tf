# Habilitar APIs necesarias para el proyecto
# Vertex AI, Cloud Run, Secret Manager, Artifact Registry, etc.

resource "google_project_service" "apis" {
  for_each = toset([
    "aiplatform.googleapis.com",       # Vertex AI (Gemini)
    "run.googleapis.com",              # Cloud Run (Agentes)
    "secretmanager.googleapis.com",    # Secret Manager (Credenciales)
    "cloudbuild.googleapis.com",       # Cloud Build (CI/CD)
    "artifactregistry.googleapis.com", # Artifact Registry (Docker Images)
    "iam.googleapis.com",              # Identity and Access Management
    "logging.googleapis.com",          # Cloud Logging
    "monitoring.googleapis.com"        # Cloud Monitoring
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false # No deshabilitar APIs si destruimos Terraform (seguridad)
}
