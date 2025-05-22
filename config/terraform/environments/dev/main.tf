/*
 * LLM Audit Assistant - Development Environment Module
 *
 * This module defines resources specific to the development environment.
 * For dev environments, we typically use local resources or minimal cloud resources.
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

# Define the outputs that will be passed back to the root module
output "app_endpoint" {
  description = "The endpoint URL for the main application"
  value       = "http://localhost:8000"  # For dev environment, assume local deployment
}

output "ui_endpoint" {
  description = "The endpoint URL for the UI component"
  value       = "http://localhost:8501"
}

output "grafana_endpoint" {
  description = "The endpoint URL for Grafana"
  value       = "http://localhost:3000"
}

output "minio_endpoint" {
  description = "The endpoint URL for MinIO"
  value       = "http://localhost:9000"
}

output "minio_console_endpoint" {
  description = "The endpoint URL for MinIO console"
  value       = "http://localhost:9001"
}
