/*
 * LLM Audit Assistant - RDS Module
 * 
 * This module creates a managed RDS database instance for storing
 * application data, user information, and metadata.
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

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "auditassistant"
}

variable "db_username" {
  description = "The username for the database"
  type        = string
  default     = "dbadmin"
}

variable "instance_class" {
  description = "The instance class for the database"
  type        = string
  default     = "db.t3.medium"
}

# DB subnet group for RDS instances
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "${var.project_name}-db-subnet-${var.environment}"
  subnet_ids = var.subnet_ids

  tags = {
    Name        = "${var.project_name}-db-subnet-${var.environment}"
    Environment = var.environment
  }
}

# Security group for RDS instances
resource "aws_security_group" "db_sg" {
  name        = "${var.project_name}-db-sg-${var.environment}"
  description = "Security group for database instances"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Only allow connections from within the VPC
    description = "Allow PostgreSQL access within VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-db-sg-${var.environment}"
    Environment = var.environment
  }
}

# Generate a random password for the RDS instance (store in AWS Secrets Manager)
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store the database credentials in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.project_name}-db-credentials-${var.environment}"
  description = "Database credentials for ${var.project_name} in ${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-db-credentials-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    dbname   = var.db_name
    host     = aws_db_instance.db.address
    port     = aws_db_instance.db.port
  })
}

# Create an RDS instance
resource "aws_db_instance" "db" {
  identifier              = "${var.project_name}-db-${var.environment}"
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = var.instance_class
  allocated_storage       = 20
  max_allocated_storage   = 100
  storage_type            = "gp3"
  db_name                 = var.db_name
  username                = var.db_username
  password                = random_password.db_password.result
  db_subnet_group_name    = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids  = [aws_security_group.db_sg.id]
  backup_retention_period = var.environment == "prod" ? 7 : 1
  skip_final_snapshot     = var.environment != "prod"
  deletion_protection     = var.environment == "prod" ? true : false
  storage_encrypted       = true
  multi_az                = var.environment == "prod" ? true : false
  
  tags = {
    Name        = "${var.project_name}-db-${var.environment}"
    Environment = var.environment
  }
}

# Outputs
output "db_endpoint" {
  description = "The endpoint of the database"
  value       = aws_db_instance.db.endpoint
}

output "db_name" {
  description = "The name of the database"
  value       = var.db_name
}

output "db_credentials_secret_arn" {
  description = "The ARN of the secret containing database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}
