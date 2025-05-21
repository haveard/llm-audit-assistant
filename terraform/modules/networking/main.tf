/*
 * LLM Audit Assistant - Networking Module
 * 
 * This module creates the networking infrastructure for the LLM Audit Assistant,
 * including VPC, subnets, security groups, and related components.
 */

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

locals {
  availability_zones = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
}

# VPC for the application
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.project_name}-vpc-${var.environment}"
    Environment = var.environment
  }
}

# Public subnets for load balancers and NAT gateways
resource "aws_subnet" "public" {
  count                   = length(local.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = local.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-public-subnet-${count.index}-${var.environment}"
    Environment = var.environment
  }
}

# Private subnets for application components
resource "aws_subnet" "private" {
  count                   = length(local.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 100}.0/24"
  availability_zone       = local.availability_zones[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name        = "${var.project_name}-private-subnet-${count.index}-${var.environment}"
    Environment = var.environment
  }
}

# Internet Gateway for public subnets
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project_name}-igw-${var.environment}"
    Environment = var.environment
  }
}

# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name        = "${var.project_name}-public-rt-${var.environment}"
    Environment = var.environment
  }
}

# Route table associations for public subnets
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway for private subnets
resource "aws_eip" "nat" {
  domain = "vpc"
  
  tags = {
    Name        = "${var.project_name}-nat-eip-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name        = "${var.project_name}-nat-${var.environment}"
    Environment = var.environment
  }

  depends_on = [aws_internet_gateway.igw]
}

# Route table for private subnets
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name        = "${var.project_name}-private-rt-${var.environment}"
    Environment = var.environment
  }
}

# Route table associations for private subnets
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Security group for application
resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg-${var.environment}"
  description = "Security group for LLM Audit Assistant app"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP access to the application"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-app-sg-${var.environment}"
    Environment = var.environment
  }
}

# Security group for UI
resource "aws_security_group" "ui" {
  name        = "${var.project_name}-ui-sg-${var.environment}"
  description = "Security group for LLM Audit Assistant UI"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP access to the UI"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-ui-sg-${var.environment}"
    Environment = var.environment
  }
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "The IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "The IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "app_security_group_id" {
  description = "The ID of the app security group"
  value       = aws_security_group.app.id
}

output "ui_security_group_id" {
  description = "The ID of the UI security group"
  value       = aws_security_group.ui.id
}
