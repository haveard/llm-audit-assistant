/*
 * LLM Audit Assistant - ElastiCache Module
 * 
 * This module creates an ElastiCache Redis cluster for caching responses,
 * session data, and improving application performance.
 */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "The IDs of the private subnets"
  type        = list(string)
}

variable "node_type" {
  description = "The node type for the ElastiCache cluster"
  type        = string
  default     = "cache.t3.medium"
}

# ElastiCache subnet group
resource "aws_elasticache_subnet_group" "cache_subnet_group" {
  name       = "${var.project_name}-cache-subnet-${var.environment}"
  subnet_ids = var.subnet_ids
  
  tags = {
    Name        = "${var.project_name}-cache-subnet-${var.environment}"
    Environment = var.environment
  }
}

# Security group for ElastiCache
resource "aws_security_group" "cache_sg" {
  name        = "${var.project_name}-cache-sg-${var.environment}"
  description = "Security group for ElastiCache"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Only allow connections from within the VPC
    description = "Allow Redis access within VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-cache-sg-${var.environment}"
    Environment = var.environment
  }
}

# Parameter group for ElastiCache
resource "aws_elasticache_parameter_group" "cache_params" {
  name   = "${var.project_name}-cache-params-${var.environment}"
  family = "redis7"
  
  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"
  }
  
  tags = {
    Name        = "${var.project_name}-cache-params-${var.environment}"
    Environment = var.environment
  }
}

# ElastiCache Redis cluster
resource "aws_elasticache_cluster" "cache" {
  cluster_id           = "${var.project_name}-cache-${var.environment}"
  engine               = "redis"
  node_type            = var.node_type
  num_cache_nodes      = 1
  parameter_group_name = aws_elasticache_parameter_group.cache_params.name
  engine_version       = "7.0"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.cache_subnet_group.name
  security_group_ids   = [aws_security_group.cache_sg.id]
  
  # Set a maintenance window during off-peak hours
  maintenance_window = "sun:05:00-sun:07:00"
  
  tags = {
    Name        = "${var.project_name}-cache-${var.environment}"
    Environment = var.environment
  }
}

# Store the ElastiCache endpoint in AWS Secrets Manager
resource "aws_secretsmanager_secret" "cache_endpoint" {
  name        = "${var.project_name}-cache-endpoint-${var.environment}"
  description = "ElastiCache Redis endpoint for ${var.project_name} in ${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-cache-endpoint-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "cache_endpoint" {
  secret_id = aws_secretsmanager_secret.cache_endpoint.id
  secret_string = jsonencode({
    endpoint = aws_elasticache_cluster.cache.cache_nodes[0].address
    port     = aws_elasticache_cluster.cache.cache_nodes[0].port
  })
}

# Outputs
output "cache_endpoint" {
  description = "The endpoint of the ElastiCache cluster"
  value       = aws_elasticache_cluster.cache.cache_nodes[0].address
}

output "cache_port" {
  description = "The port of the ElastiCache cluster"
  value       = aws_elasticache_cluster.cache.cache_nodes[0].port
}

output "cache_endpoint_secret_arn" {
  description = "The ARN of the secret containing cache endpoint"
  value       = aws_secretsmanager_secret.cache_endpoint.arn
}
