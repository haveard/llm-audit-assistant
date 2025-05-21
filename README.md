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
2. Build and start all services:
   ```sh
   docker compose up --build
   ```
3. Access the API at [http://localhost:8000/docs](http://localhost:8000/docs) and the UI at [http://localhost:8501](http://localhost:8501)

**Note:**
- The UI and backend communicate via Docker Compose networking. The UI uses the `BACKEND_URL` environment variable, which defaults to `http://app:8000` inside Docker Compose. No manual changes are needed for connectivity.
- The backend service no longer mounts the local `./app` directory as a volume. All code is copied into the image at build time. If you make code changes, re-run `docker compose up --build` to rebuild the containers.
- For local development (not in Docker), set `BACKEND_URL` to `http://localhost:8000` in your environment or `.env` file for the UI.

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