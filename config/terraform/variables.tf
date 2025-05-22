/*
 * LLM Audit Assistant - Variables Definition
 *
 * This file contains the variable definitions for the LLM Audit Assistant project.
 * Common variables that are used across all environments are defined here.
 */

variable "aws_region" {
  description = "The AWS region to deploy resources to"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "llm-audit-assistant"
}

# LLM Configuration Variables
variable "llm_provider" {
  description = "Provider for LLM (openai, azure, ollama)"
  type        = string
  default     = "ollama"
}

variable "llm_model" {
  description = "Model to use for LLM"
  type        = string
  default     = "llama3"
}

variable "openai_api_key" {
  description = "API key for OpenAI (if using OpenAI provider)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "ollama_url" {
  description = "URL for Ollama API (if using Ollama provider)"
  type        = string
  default     = "http://localhost:11434"
}

# MinIO Configuration Variables
variable "minio_root_user" {
  description = "Root username for MinIO"
  type        = string
  default     = "minioadmin"
  sensitive   = true
}

variable "minio_root_password" {
  description = "Root password for MinIO"
  type        = string
  default     = ""
  sensitive   = true
}

variable "minio_access_key" {
  description = "Access key for MinIO"
  type        = string
  default     = "minioaccess"
  sensitive   = true
}

variable "minio_secret_key" {
  description = "Secret key for MinIO"
  type        = string
  default     = ""
  sensitive   = true
}

# Grafana Configuration Variables
variable "grafana_admin_password" {
  description = "Admin password for Grafana"
  type        = string
  default     = ""
  sensitive   = true
}
