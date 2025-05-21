# LLM Audit Assistant

A self-hosted system for teams to analyze internal documents using LLMs. Warning, this is a proof of concept and not for production use. 

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