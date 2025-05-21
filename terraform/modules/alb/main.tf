/*
 * LLM Audit Assistant - ALB Module
 * 
 * This module creates Application Load Balancers for directing traffic 
 * to the various application components.
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
  description = "The IDs of the subnets for the ALB"
  type        = list(string)
}

# Security group for the ALB
resource "aws_security_group" "alb_sg" {
  name        = "${var.project_name}-alb-sg-${var.environment}"
  description = "Security group for application load balancer"
  vpc_id      = var.vpc_id

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP access"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS access"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-alb-sg-${var.environment}"
    Environment = var.environment
  }
}

# Application Load Balancer for the main app
resource "aws_lb" "app_alb" {
  name               = "${var.project_name}-app-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.project_name}-app-alb-${var.environment}"
    Environment = var.environment
  }
}

# Target Group for the main app
resource "aws_lb_target_group" "app_tg" {
  name     = "${var.project_name}-app-tg-${var.environment}"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name        = "${var.project_name}-app-tg-${var.environment}"
    Environment = var.environment
  }
}

# ALB Listener for the main app (HTTP)
resource "aws_lb_listener" "app_http" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# Application Load Balancer for the UI
resource "aws_lb" "ui_alb" {
  name               = "${var.project_name}-ui-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.project_name}-ui-alb-${var.environment}"
    Environment = var.environment
  }
}

# Target Group for the UI
resource "aws_lb_target_group" "ui_tg" {
  name     = "${var.project_name}-ui-tg-${var.environment}"
  port     = 8501
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    path                = "/"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name        = "${var.project_name}-ui-tg-${var.environment}"
    Environment = var.environment
  }
}

# ALB Listener for the UI (HTTP)
resource "aws_lb_listener" "ui_http" {
  load_balancer_arn = aws_lb.ui_alb.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui_tg.arn
  }
}

# Application Load Balancer for Grafana
resource "aws_lb" "grafana_alb" {
  name               = "${var.project_name}-grafana-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.project_name}-grafana-alb-${var.environment}"
    Environment = var.environment
  }
}

# Target Group for Grafana
resource "aws_lb_target_group" "grafana_tg" {
  name     = "${var.project_name}-grafana-tg-${var.environment}"
  port     = 3000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    path                = "/login"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name        = "${var.project_name}-grafana-tg-${var.environment}"
    Environment = var.environment
  }
}

# ALB Listener for Grafana (HTTP)
resource "aws_lb_listener" "grafana_http" {
  load_balancer_arn = aws_lb.grafana_alb.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.grafana_tg.arn
  }
}

# Application Load Balancer for MinIO
resource "aws_lb" "minio_alb" {
  name               = "${var.project_name}-minio-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids

  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.project_name}-minio-alb-${var.environment}"
    Environment = var.environment
  }
}

# Target Group for MinIO API
resource "aws_lb_target_group" "minio_api_tg" {
  name     = "${var.project_name}-minio-api-tg-${var.environment}"
  port     = 9000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    path                = "/minio/health/live"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name        = "${var.project_name}-minio-api-tg-${var.environment}"
    Environment = var.environment
  }
}

# Target Group for MinIO Console
resource "aws_lb_target_group" "minio_console_tg" {
  name     = "${var.project_name}-minio-console-tg-${var.environment}"
  port     = 9001
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    path                = "/minio/health/ready"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = {
    Name        = "${var.project_name}-minio-console-tg-${var.environment}"
    Environment = var.environment
  }
}

# ALB Listener for MinIO API (HTTP)
resource "aws_lb_listener" "minio_api_http" {
  load_balancer_arn = aws_lb.minio_alb.arn
  port              = 9000
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.minio_api_tg.arn
  }
}

# ALB Listener for MinIO Console (HTTP)
resource "aws_lb_listener" "minio_console_http" {
  load_balancer_arn = aws_lb.minio_alb.arn
  port              = 9001
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.minio_console_tg.arn
  }
}

# Outputs
output "app_endpoint" {
  description = "The endpoint URL for the main application"
  value       = "http://${aws_lb.app_alb.dns_name}"
}

output "ui_endpoint" {
  description = "The endpoint URL for the UI component"
  value       = "http://${aws_lb.ui_alb.dns_name}"
}

output "grafana_endpoint" {
  description = "The endpoint URL for Grafana"
  value       = "http://${aws_lb.grafana_alb.dns_name}"
}

output "minio_endpoint" {
  description = "The endpoint URL for MinIO API"
  value       = "http://${aws_lb.minio_alb.dns_name}:9000"
}

output "minio_console_endpoint" {
  description = "The endpoint URL for MinIO console"
  value       = "http://${aws_lb.minio_alb.dns_name}:9001"
}
