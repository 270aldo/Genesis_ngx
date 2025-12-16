variable "project_id" {
  description = "El ID del proyecto de Google Cloud"
  type        = string
}

variable "region" {
  description = "La región de GCP para los recursos (ej. us-central1)"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Entorno de despliegue (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "github_org" {
  description = "GitHub organization name for Workload Identity Federation"
  type        = string
  default     = "genesis-ngx"
}

variable "github_repo" {
  description = "GitHub repository name for Workload Identity Federation"
  type        = string
  default     = "genesis_ngx"
}

variable "billing_account_id" {
  description = "GCP Billing Account ID for budget alerts"
  type        = string
}

variable "monthly_budget_usd" {
  description = "Monthly budget in USD for the project"
  type        = number
  default     = 50
}
