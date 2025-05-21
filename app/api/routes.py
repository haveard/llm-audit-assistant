# REST endpoints

import os
import logging

from fastapi import APIRouter, UploadFile, File, Request

from app.api.schema import QueryRequest, LLMResponse
from app.ingest.loader import load_document
from app.ingest.preprocessor import preprocess_document
from app.llm.client import LLMClient
from app.llm.rag import RAGPipeline
from app.utils.security import sanitize_input, sanitize_output, scan_prompt_injection, log_request

router = APIRouter()
llm_client = LLMClient(
    provider=os.getenv("LLM_PROVIDER", "openai"),
    model=os.getenv("LLM_MODEL", "o4-mini"),
    ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434")
)
rag = RAGPipeline(llm_client)

documents = []  # In-memory store for demo

logger = logging.getLogger("llm_audit_assistant.api")


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Received upload for file: {file.filename}")
    try:
        content = await file.read()
        tmp_path = f"/tmp/{file.filename}"
        with open(tmp_path, "wb") as f:
            f.write(content)
        text, meta = load_document(tmp_path)
        logger.info(f"Loaded document: {meta}")
        chunks = preprocess_document(text, metadata=meta)
        rag.add_documents(chunks)
        documents.extend(chunks)
        logger.info(f"Ingested {len(chunks)} chunks from {file.filename}")
        return {"chunks": len(chunks), "filename": file.filename, "size": len(content)}
    except Exception as e:
        logger.error(f"Error during upload: {e}", exc_info=True)
        raise


@router.post("/query", response_model=LLMResponse)
async def query_llm(request: Request, query: QueryRequest):
    user_question = sanitize_input(query.question)
    logger.info(f"Received query: {user_question}")
    if scan_prompt_injection(user_question):
        answer = "Potential prompt injection detected."
        sources = None
        logger.warning("Prompt injection detected in user query.")
    else:
        top_chunks = rag.retrieve(user_question, top_k=query.top_k or 3)
        result = rag.query(user_question, top_k=query.top_k or 3)
        answer_val = result.get("answer", "") if isinstance(result, dict) else result
        if isinstance(answer_val, dict):
            answer_val = answer_val.get("answer", "")
        answer = sanitize_output(str(answer_val))
        sources = top_chunks
        logger.info(f"Query answered. Answer length: {len(answer)}")
    await log_request(request, user_question, answer, sources)
    return LLMResponse(answer=answer, sources=sources, tokens_used=None, latency_ms=None)


@router.get("/status")
def status():
    logger.info(f"Status endpoint called. Documents loaded: {len(documents)}")
    return {"documents_loaded": len(documents)}
