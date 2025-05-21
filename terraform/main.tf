/*
 * LLM Audit Assistant - Main Terraform Configuration
 *
 * This file contains the main Terraform configuration for the LLM Audit Assistant project.
 * It defines providers and common variables for all environments.
 */

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
  
  # Uncomment the backend block and configure it when you're ready to use remote state
  # backend "s3" {
  #   bucket         = "llm-audit-assistant-tfstate"
  #   key            = "terraform.tfstate"
  #   region         = "us-west-2"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "LLM Audit Assistant"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "docker" {
  # Uses default Docker socket configuration
  # For remote Docker hosts, you'd configure host and other parameters here
}

# Include the environment-specific configuration
module "environment" {
  source = "./environments/${var.environment}"
  
  # Common variables passed to the environment module
  aws_region           = var.aws_region
  project_name         = var.project_name
  environment          = var.environment
  minio_root_user      = var.minio_root_user
  minio_root_password  = var.minio_root_password
  openai_api_key       = var.openai_api_key
  llm_provider         = var.llm_provider
  llm_model            = var.llm_model
}
