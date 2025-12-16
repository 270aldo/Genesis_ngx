# =============================================================================
# Service Accounts Module - Outputs
# =============================================================================

output "gateway_sa_email" {
  description = "Gateway service account email"
  value       = google_service_account.gateway.email
}

output "gateway_sa_name" {
  description = "Gateway service account full name"
  value       = google_service_account.gateway.name
}

output "agents_sa_email" {
  description = "Agents service account email"
  value       = google_service_account.agents.email
}

output "agents_sa_name" {
  description = "Agents service account full name"
  value       = google_service_account.agents.name
}
