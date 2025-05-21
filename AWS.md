# AWS Equivalents for LLM Audit Assistant Services

This document maps the services defined in our docker-compose.yml file to their equivalent AWS managed services for cloud deployment.

## Service Mapping

| Docker Compose Service | AWS Service | Description |
|--------------------------|-------------|-------------|
| **app** (FastAPI Backend) | **AWS ECS/Fargate** or **AWS App Runner** | Runs the FastAPI backend as containers on ECS or as a serverless service on App Runner |
| **ui** (Streamlit Frontend) | **AWS ECS/Fargate** or **AWS Amplify** | Runs the Streamlit UI as containers on ECS or as a web application on Amplify |
| **weaviate** (Vector Database) | **Amazon OpenSearch Service** | Provides vector search capabilities, replacing Weaviate's functionality |
| **minio** (Object Storage) | **Amazon S3** | Native object storage service that provides similar functionality to MinIO |
| **minio-client** (Setup) | **AWS Lambda** or **Custom Init in ECS** | Initialization tasks can be handled by Lambda functions or as part of ECS container startup |
| **loki** (Log Aggregator) | **Amazon CloudWatch Logs** | Centralized log storage and query system |
| **promtail** (Log Shipper) | **CloudWatch Agent** or **FireLens** | Collects and forwards logs to CloudWatch |
| **grafana** (Monitoring) | **Amazon Managed Grafana** or **CloudWatch Dashboards** | Visualization and monitoring of metrics and logs |

## Additional Required AWS Services

These AWS services don't directly map to our docker-compose services but are necessary for a complete infrastructure:

| Service | Purpose |
|---------|---------|
| **Amazon ECR** | Store Docker images for our application containers |
| **Amazon RDS** | Managed relational database service if needed for application state |
| **Amazon ElastiCache** | In-memory caching for improved performance |
| **AWS Secrets Manager** | Securely store and manage secrets like API keys and credentials |
| **Amazon API Gateway** | Manage API endpoints, authentication, and throttling |
| **Amazon CloudFront** | Content delivery network for UI assets |
| **AWS IAM** | Identity and access management for service permissions |
| **AWS VPC** | Networking infrastructure for security and isolation |

## Architecture Differences

When migrating from a Docker Compose setup to AWS, consider these key differences:

1. **Networking**: Services that communicate directly in Docker Compose will need properly configured security groups and VPC settings in AWS

2. **State Management**: Docker volumes will be replaced by:
   - S3 for object storage
   - EFS for file system storage needs
   - RDS for database storage

3. **Service Discovery**: Docker Compose service names won't resolve in AWS; use AWS service discovery or direct endpoint configuration

4. **Logging**: The Loki/Promtail stack will be replaced by CloudWatch, which requires different configuration

5. **Scaling**: AWS services can be configured to auto-scale, unlike the fixed configurations in docker-compose

## Terraform Configuration

The terraform directory in this project contains modules that implement this architecture:

- `modules/ecs_cluster`: Runs the app and ui containers
- `modules/s3`: Replaces MinIO for object storage
- `modules/rds`: Provides database capabilities if needed
- `modules/ecr`: Stores Docker images
- `modules/alb`: Handles incoming traffic and routing
- `modules/networking`: Sets up VPC, subnets, and security groups
- `modules/elasticache`: Provides Redis caching capabilities
- `modules/secrets`: Manages sensitive information securely

For a complete cloud deployment, the following modules would need to be added:

1. `modules/opensearch`: For vector search capabilities (replacing Weaviate)
2. `modules/managed_grafana`: For monitoring and visualization
3. `modules/cloudwatch`: For centralized logging (replacing Loki/Promtail)

## Environment Variables Mapping

| Docker Compose Env Var | AWS Equivalent |
|------------------------|----------------|
| `OLLAMA_URL` | N/A (Use AWS service or hosted Ollama) |
| `OPENAI_API_KEY` | Stored in AWS Secrets Manager |
| `LLM_PROVIDER` | Stored as ECS environment variable |
| `LLM_MODEL` | Stored as ECS environment variable |
| `MINIO_ENDPOINT` | Replace with S3 endpoint |
| `MINIO_ACCESS_KEY` | Replace with IAM role or AWS access key |
| `MINIO_SECRET_KEY` | Replace with IAM role or AWS secret key |
| `MINIO_BUCKET` | Replace with S3 bucket name |
| `GF_SECURITY_ADMIN_PASSWORD` | Managed by Amazon Managed Grafana |
