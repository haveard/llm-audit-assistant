/*
 * LLM Audit Assistant - Secrets Manager Module
 * 
 * This module creates AWS Secrets Manager resources for storing sensitive
 * information such as API keys, credentials, and other secrets.
 */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "minio_root_user" {
  description = "Root username for MinIO"
  type        = string
  sensitive   = true
}

variable "minio_root_password" {
  description = "Root password for MinIO"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "API key for OpenAI (if using OpenAI provider)"
  type        = string
  sensitive   = true
}

# Generate random values for various credentials
resource "random_password" "minio_access_key" {
  length  = 16
  special = false
}

resource "random_password" "minio_secret_key" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "random_password" "grafana_admin_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store MinIO credentials in AWS Secrets Manager
resource "aws_secretsmanager_secret" "minio_credentials" {
  name        = "${var.project_name}-minio-credentials-${var.environment}"
  description = "MinIO credentials for ${var.project_name} in ${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-minio-credentials-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "minio_credentials" {
  secret_id = aws_secretsmanager_secret.minio_credentials.id
  secret_string = jsonencode({
    root_user     = var.minio_root_user
    root_password = var.minio_root_password
    access_key    = random_password.minio_access_key.result
    secret_key    = random_password.minio_secret_key.result
  })
}

# Store OpenAI API key in AWS Secrets Manager (if provided)
resource "aws_secretsmanager_secret" "openai_api_key" {
  count       = var.openai_api_key != "" ? 1 : 0
  name        = "${var.project_name}-openai-api-key-${var.environment}"
  description = "OpenAI API key for ${var.project_name} in ${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-openai-api-key-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  count      = var.openai_api_key != "" ? 1 : 0
  secret_id  = aws_secretsmanager_secret.openai_api_key[0].id
  secret_string = jsonencode({
    api_key = var.openai_api_key
  })
}

# Store Grafana admin password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "grafana_admin_password" {
  name        = "${var.project_name}-grafana-admin-password-${var.environment}"
  description = "Grafana admin password for ${var.project_name} in ${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-grafana-admin-password-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "grafana_admin_password" {
  secret_id = aws_secretsmanager_secret.grafana_admin_password.id
  secret_string = jsonencode({
    admin_password = random_password.grafana_admin_password.result
  })
}

# Outputs
output "minio_credentials_arn" {
  description = "The ARN of the MinIO credentials secret"
  value       = aws_secretsmanager_secret.minio_credentials.arn
}

output "openai_api_key_arn" {
  description = "The ARN of the OpenAI API key secret"
  value       = var.openai_api_key != "" ? aws_secretsmanager_secret.openai_api_key[0].arn : null
}

output "grafana_admin_password_arn" {
  description = "The ARN of the Grafana admin password secret"
  value       = aws_secretsmanager_secret.grafana_admin_password.arn
}

output "minio_access_key" {
  description = "Generated MinIO access key"
  value       = random_password.minio_access_key.result
  sensitive   = true
}

output "minio_secret_key" {
  description = "Generated MinIO secret key"
  value       = random_password.minio_secret_key.result
  sensitive   = true
}

output "grafana_admin_password" {
  description = "Generated Grafana admin password"
  value       = random_password.grafana_admin_password.result
  sensitive   = true
}

output "secret_arns" {
  description = "A list of all secret ARNs"
  value = concat(
    [aws_secretsmanager_secret.minio_credentials.arn, aws_secretsmanager_secret.grafana_admin_password.arn],
    var.openai_api_key != "" ? [aws_secretsmanager_secret.openai_api_key[0].arn] : []
  )
}
