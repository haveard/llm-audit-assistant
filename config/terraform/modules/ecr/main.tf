/*
 * LLM Audit Assistant - ECR Module
 * 
 * This module creates Amazon Elastic Container Registry repositories
 * to store Docker images for the LLM Audit Assistant components.
 */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

# Create ECR repositories for the application containers
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-app-${var.environment}"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    Name        = "${var.project_name}-app-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_ecr_repository" "ui" {
  name                 = "${var.project_name}-ui-${var.environment}"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    Name        = "${var.project_name}-ui-${var.environment}"
    Environment = var.environment
  }
}

# Add lifecycle policy to limit the number of images kept
resource "aws_ecr_lifecycle_policy" "app_policy" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "ui_policy" {
  repository = aws_ecr_repository.ui.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Outputs
output "app_repository_url" {
  description = "The URL of the ECR repository for the app component"
  value       = aws_ecr_repository.app.repository_url
}

output "ui_repository_url" {
  description = "The URL of the ECR repository for the UI component"
  value       = aws_ecr_repository.ui.repository_url
}
