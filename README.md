# LLM Audit Assistant

LLM Audit Assistant is a self-hosted proof-of-concept platform designed for teams to analyze internal documents using large language models (LLMs). It enables secure document ingestion, preprocessing, and contextual retrieval-augmented generation (RAG) to provide relevant, AI-powered insights from enterprise data. The system features a custom evaluation harness for LLM outputs, prompt injection protection for enhanced security, and an admin UI for internal management. Built with FastAPI, LangChain, and Streamlit, it leverages Weaviate as a vector store for efficient document retrieval. The application is containerized with Docker and orchestrated via Docker Compose, ensuring easy deployment and service isolation. The UI and backend communicate seamlessly within Docker Compose using environment variables, and the backend is designed to be rebuilt for code changes. LLM Audit Assistant supports both local LLMs (via Ollama) and OpenAI models, making it flexible for various enterprise and research use cases.

## Features
- Document ingestion & preprocessing
- Contextual RAG (retrieval-augmented generation)
- Custom evaluation harness
- Security hardening (prompt injection protection)
- Admin UI for internal use

## Quickstart

1. Clone the repo
2. Set up your `.env` file.
3. Build and start all services:
   ```sh
   docker compose up --build
   ```
4. Access the API at [http://localhost:8000/docs](http://localhost:8000/docs) and the UI at [http://localhost:8501](http://localhost:8501)

**Note:**
- The UI and backend communicate via Docker Compose networking. The UI uses the `BACKEND_URL` environment variable, which defaults to `http://app:8000` inside Docker Compose. No manual changes are needed for connectivity.
- For local development (not in Docker), set `BACKEND_URL` to `http://localhost:8000` in your environment or `.env` file for the UI.

## Running Tests

The project includes a comprehensive test suite that covers unit tests, integration tests, and API endpoint tests. Different test types have different requirements:

### Unit Tests

To run the basic unit tests (which use mocking and don't require services):

```sh
# Ensure you're in the project root
cd /path/to/llm-audit-assistant

# Install testing dependencies
pip install pytest pytest-cov

# Run all unit tests
PYTHONPATH=. pytest tests/test_loader.py tests/test_prompt_injection.py

# With coverage report
PYTHONPATH=. pytest --cov=app tests/test_loader.py tests/test_prompt_injection.py
```

### API Endpoint Tests

API endpoint tests use FastAPI's TestClient and mock external dependencies:

```sh
PYTHONPATH=. pytest tests/test_api_endpoints.py
```

### Integration Tests

Some tests require services to be running:

- `test_rag_eval.py` - Requires LLM services (OpenAI or Ollama)
- `test_minio_integration.py` - Requires MinIO service when not using mocks

To run integration tests with services:

```sh
# First ensure your services are running via Docker Compose
docker compose up -d

# Then run the integration tests
PYTHONPATH=. pytest tests/test_rag_eval.py tests/test_minio_integration.py
```

### Environment for Testing

Create a `.env.test` file with test-specific configuration:

```bash
# Test environment settings
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=test-uploads
WEAVIATE_URL=http://localhost:8080
LLM_PROVIDER=openai  # or ollama for local testing
LLM_MODEL=o4-mini    # or mistral for local testing
```

### Running All Tests

To run all tests with services available:

```sh
# Ensure services are running
docker compose up -d

# Run all tests
PYTHONPATH=. pytest
```

To skip integration tests that require external services:

```sh
PYTHONPATH=. pytest -k "not test_minio_integration and not test_rag_eval[qa_pair0]"
```

## Tech Stack
- Python (FastAPI, LangChain, Pydantic)
- Weaviate (vector store)
- Streamlit (UI)
- Docker
- MinIO (S3-compatible object storage)
- Grafana Loki (log aggregation)
- Promtail (log shipping)
- Grafana (log visualization)

## Observability & Logging
- Logs from all containers are aggregated using Grafana Loki and Promtail.
- To view logs, access Grafana at [http://localhost:3000](http://localhost:3000) (default password: admin).
- Add Loki as a data source in Grafana (URL: `http://loki:3100`).
- Explore and search logs from all your containers in the Grafana UI.

### .env example additions for local LLM via Ollama
```bash
LLM_PROVIDER=ollama
LLM_MODEL=mistral
OLLAMA_URL=http://localhost:11434
```
### For OpenAI, use:
```bash
LLM_PROVIDER=openai
LLM_MODEL=o4-mini
OPENAI_API_KEY=sk-...
```

## Infrastructure Deployment with Terraform

This project includes Terraform configurations for deploying the infrastructure required to run LLM Audit Assistant in cloud environments. This infrastructure-as-code approach ensures consistent deployments across environments.

### Prerequisites

1. [Terraform](https://www.terraform.io/downloads.html) installed (v1.0.0 or newer)
2. AWS CLI configured with appropriate credentials
3. Docker installed (for local image building)

### Getting Started with Terraform

1. Navigate to the Terraform directory:
   ```sh
   cd terraform
   ```

2. Copy the example variables file and customize it:
   ```sh
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Initialize Terraform:
   ```sh
   terraform init
   ```

4. Review the execution plan:
   ```sh
   terraform plan
   ```

5. Apply the configuration:
   ```sh
   terraform apply
   ```

6. After deployment, Terraform will output the endpoints for all services.

### Environment Configurations

The Terraform setup includes configurations for multiple environments:

- **dev**: Minimal infrastructure for development and testing
- **staging**: Pre-production environment with production-like resources
- **prod**: Full production environment with high availability

Each environment can be selected by modifying the `environment` variable in your `terraform.tfvars` file.

### Modules

The Terraform configuration is organized into modules:

- **ECR**: Elastic Container Registry for storing Docker images
- **ECS Cluster**: For running containerized applications
- **Networking**: VPC, subnets, and security groups
- **S3**: Object storage for documents and application data

### Remote State Management

For team collaboration, it's recommended to configure remote state with the S3 backend. Uncomment and configure the backend block in `main.tf` to enable this feature.
