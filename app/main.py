import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.llm.client import LLMClient
from app.llm.rag import RAGPipeline
from app.utils.security import RateLimiterMiddleware

# Configure root logger for the backend
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("llm_audit_assistant")

rag_pipeline = RAGPipeline(LLMClient())


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if rag_pipeline.weaviate is not None:
        rag_pipeline.weaviate.close()


app = FastAPI(title="LLM Audit Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware, max_requests=20, window_seconds=60)


@app.get("/")
def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}


app.include_router(router)

# Optionally add startup/shutdown events, CORS, etc.

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
