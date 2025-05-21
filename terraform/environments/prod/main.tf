/*
 * LLM Audit Assistant - Production Environment Module
 *
 * This module defines resources specific to the production environment.
 * For production environments, we emphasize high availability, security, and scaling.
 */

# Define variables for this module
variable "aws_region" {
  description = "The AWS region to deploy resources to"
  type        = string
}

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

variable "llm_provider" {
  description = "Provider for LLM (openai, azure, ollama)"
  type        = string
}

variable "llm_model" {
  description = "Model to use for LLM"
  type        = string
}

# Include the modules for each resource component
module "ecr" {
  source = "../modules/ecr"
  
  project_name = var.project_name
  environment  = var.environment
}

module "ecs_cluster" {
  source = "../modules/ecs_cluster"
  
  project_name = var.project_name
  environment  = var.environment
}

module "networking" {
  source = "../modules/networking"
  
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region
}

module "s3" {
  source = "../modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
}

module "rds" {
  source = "../modules/rds"
  
  project_name   = var.project_name
  environment    = var.environment
  vpc_id         = module.networking.vpc_id
  subnet_ids     = module.networking.private_subnet_ids
  db_name        = "auditassistant"
  db_username    = "dbadmin"
  # Password should be provided via AWS Secrets Manager in production
}

module "elasticache" {
  source = "../modules/elasticache"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.networking.vpc_id
  subnet_ids   = module.networking.private_subnet_ids
}

module "alb" {
  source = "../modules/alb"
  
  project_name  = var.project_name
  environment   = var.environment
  vpc_id        = module.networking.vpc_id
  subnet_ids    = module.networking.public_subnet_ids
}

module "secrets" {
  source = "../modules/secrets"
  
  project_name        = var.project_name
  environment         = var.environment
  minio_root_user     = var.minio_root_user
  minio_root_password = var.minio_root_password
  openai_api_key      = var.openai_api_key
}

# IAM Role for ECS task execution with access to Secrets Manager
resource "aws_iam_role_policy" "secrets_access" {
  name = "${var.project_name}-secrets-access-${var.environment}"
  role = module.ecs_cluster.task_execution_role_arn
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = module.secrets.secret_arns
      }
    ]
  })
}

# Define the outputs that will be passed back to the root module
output "app_endpoint" {
  description = "The endpoint URL for the main application"
  value       = module.alb.app_endpoint
}

output "ui_endpoint" {
  description = "The endpoint URL for the UI component"
  value       = module.alb.ui_endpoint
}

output "grafana_endpoint" {
  description = "The endpoint URL for Grafana"
  value       = module.alb.grafana_endpoint
}

output "minio_endpoint" {
  description = "The endpoint URL for MinIO"
  value       = module.alb.minio_endpoint
}

output "minio_console_endpoint" {
  description = "The endpoint URL for MinIO console"
  value       = module.alb.minio_console_endpoint
}
