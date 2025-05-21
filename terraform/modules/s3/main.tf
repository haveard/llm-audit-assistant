/*
 * LLM Audit Assistant - S3 Module
 * 
 * This module creates S3 buckets for storing documents, files, and
 * application data needed by the LLM Audit Assistant.
 */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

# Create an S3 bucket for document storage
resource "aws_s3_bucket" "documents" {
  bucket = "${var.project_name}-documents-${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-documents-${var.environment}"
    Environment = var.environment
  }
}

# Enable versioning for the documents bucket
resource "aws_s3_bucket_versioning" "documents_versioning" {
  bucket = aws_s3_bucket.documents.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure server-side encryption for the documents bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "documents_encryption" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Create an S3 bucket for application logs
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-logs-${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-logs-${var.environment}"
    Environment = var.environment
  }
}

# Configure lifecycle rules for the logs bucket
resource "aws_s3_bucket_lifecycle_configuration" "logs_lifecycle" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "expire_old_logs"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

# Create S3 bucket for terraform state backup
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.project_name}-terraform-state-${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-terraform-state-${var.environment}"
    Environment = var.environment
  }
}

# Enable versioning for the terraform state bucket
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure server-side encryption for the terraform state bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Outputs
output "documents_bucket_name" {
  description = "The name of the documents S3 bucket"
  value       = aws_s3_bucket.documents.id
}

output "documents_bucket_arn" {
  description = "The ARN of the documents S3 bucket"
  value       = aws_s3_bucket.documents.arn
}

output "logs_bucket_name" {
  description = "The name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "The ARN of the logs S3 bucket"
  value       = aws_s3_bucket.logs.arn
}

output "terraform_state_bucket_name" {
  description = "The name of the terraform state S3 bucket"
  value       = aws_s3_bucket.terraform_state.id
}
