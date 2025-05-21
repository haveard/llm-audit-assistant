/*
 * LLM Audit Assistant - Output Definitions
 *
 * This file contains the output definitions for the LLM Audit Assistant project.
 * Outputs are used to expose certain values after Terraform has provisioned the resources.
 */

output "environment" {
  description = "The environment that was deployed"
  value       = var.environment
}

# Expose outputs from the environment module
output "app_endpoint" {
  description = "The endpoint URL for the main application"
  value       = module.environment.app_endpoint
}

output "ui_endpoint" {
  description = "The endpoint URL for the UI component"
  value       = module.environment.ui_endpoint
}

output "grafana_endpoint" {
  description = "The endpoint URL for Grafana"
  value       = module.environment.grafana_endpoint
}

output "minio_endpoint" {
  description = "The endpoint URL for MinIO"
  value       = module.environment.minio_endpoint
}

output "minio_console_endpoint" {
  description = "The endpoint URL for MinIO console"
  value       = module.environment.minio_console_endpoint
}
