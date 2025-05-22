# LLM Audit Assistant Terraform Infrastructure

This directory contains Terraform configurations for deploying the LLM Audit Assistant infrastructure to cloud environments. The infrastructure is defined as code, allowing for consistent, repeatable deployments across multiple environments.

## Overview

The Terraform configuration is organized into modules and environments:

```
terraform/
├── environments/         # Environment-specific configurations
│   ├── dev/             # Development environment
│   ├── staging/         # Staging/pre-production environment
│   └── prod/            # Production environment
├── modules/             # Reusable infrastructure modules
│   ├── alb/             # Application Load Balancer resources
│   ├── ecr/             # Elastic Container Registry resources
│   ├── ecs_cluster/     # ECS Cluster resources
│   ├── elasticache/     # ElastiCache (Redis) resources
│   ├── networking/      # VPC, subnets, security groups
│   ├── rds/             # RDS database resources
│   └── s3/              # S3 bucket resources
│   └── secrets/         # AWS Secrets Manager resources
├── main.tf              # Main configuration file
├── variables.tf         # Variable definitions
├── outputs.tf           # Output definitions
└── terraform.tfvars.example  # Example variables file
```

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) v1.0.0 or newer
- AWS CLI configured with appropriate credentials
- Access to an AWS account with permissions to create the required resources

## Getting Started

1. Clone the repository and navigate to the Terraform directory:

```bash
cd terraform
```

2. Copy the example variables file and customize it with your settings:

```bash
cp terraform.tfvars.example terraform.tfvars
```

3. Edit `terraform.tfvars` with your preferred text editor to set the required variables

4. Initialize Terraform:

```bash
terraform init
```

5. Plan and apply the configuration:

```bash
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

## Environments

The infrastructure can be deployed to multiple environments by changing the `environment` variable:

- **dev**: Development environment with minimal resources
- **staging**: Pre-production environment with production-like resources but lower capacity
- **prod**: Production environment with high availability and redundancy

Example:
```bash
terraform apply -var="environment=prod"
```

## Modules

### Networking

Creates the VPC, subnets, security groups, and related networking components.

### ECR

Creates Elastic Container Registry repositories for storing Docker images of the application components.

### ECS Cluster

Creates an ECS cluster for running containerized applications with appropriate IAM roles.

### ALB

Creates Application Load Balancers for distributing traffic to the application components.

### RDS

Creates an RDS PostgreSQL database for storing application data.

### ElastiCache

Creates a Redis ElastiCache cluster for caching and session storage.

### S3

Creates S3 buckets for document storage and other application data.

### Secrets

Manages sensitive information like API keys and credentials in AWS Secrets Manager.

## Using with Makefile

For convenience, you can use the included Makefile to run common Terraform commands:

```bash
# Initialize
make tf-init

# Plan for dev environment
make tf-plan ENV=dev

# Apply for prod environment
make tf-apply ENV=prod

# Destroy staging environment
make tf-destroy ENV=staging
```

## Remote State

By default, the Terraform state is stored locally. For team collaboration, it's recommended to use remote state with the S3 backend. Uncomment and configure the backend block in `main.tf` to enable this feature.

## Security Considerations

- All sensitive variables are marked as sensitive in Terraform and stored securely
- Production environments use encryption for data at rest and in transit
- Networking is configured with security best practices
- Secrets are stored in AWS Secrets Manager

## Monitoring and Logging

The infrastructure includes CloudWatch for monitoring and logging of application components.

## Disaster Recovery

For production environments, backups are enabled for databases and critical data is stored in durable S3 storage.

## Cost Management

Different environment configurations use appropriately sized resources to manage costs:
- Development uses minimal, cost-effective resources
- Staging uses moderate resources
- Production uses properly sized resources for performance and reliability

## Contributing

When making changes to the Terraform configurations:
1. Create a new branch
2. Make your changes
3. Run `terraform validate` and `terraform fmt` to ensure correctness and consistent formatting
4. Create a pull request for review
