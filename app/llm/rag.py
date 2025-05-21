# Vector search + prompt injection guard

import os
import logging
from typing import List, Dict, Any

import weaviate
from langchain_openai import OpenAIEmbeddings

from app.llm.client import LLMClient
from app.llm.prompt_template import PROMPT_TEMPLATE
from app.utils.security import scan_prompt_injection

# Add logger
logger = logging.getLogger("llm_audit_assistant.rag")


class RAGPipeline:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        self.index_name = os.getenv("WEAVIATE_INDEX", "DocumentChunk")
        
        # Initialize Weaviate with error handling
        try:
            self.weaviate = weaviate.WeaviateClient(
                connection_params=weaviate.connect.ConnectionParams.from_url(
                    self.weaviate_url, 
                    grpc_port=50051
                )
            )
            self.weaviate.connect()
            logger.info(f"Connected to Weaviate at {self.weaviate_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            # Fall back to a dummy implementation that won't crash
            self.weaviate = None
            raise RuntimeError(f"Failed to initialize Weaviate: {e}")
        
        # Initialize embeddings with error handling
        try:
            self.embeddings = OpenAIEmbeddings()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {e}")
            raise RuntimeError(f"Failed to initialize OpenAI embeddings: {e}")
            
        # Ensure schema exists
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        if self.weaviate is None:
            return
            
        # v4: Use collections API
        try:
            from weaviate.collections.classes.config import Property, DataType
            collections = self.weaviate.collections.list_all()
            if self.index_name not in collections:
                self.weaviate.collections.create(
                    name=self.index_name,
                    properties=[
                        Property(name="text", data_type=DataType.TEXT),
                        Property(name="metadata", data_type=DataType.TEXT),
                    ]
                )
                logger.info(f"Created Weaviate collection: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create Weaviate schema: {e}")
            raise RuntimeError(f"Failed to create Weaviate schema: {e}")

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        if not chunks or self.weaviate is None:
            return
            
        try:
            collection = self.weaviate.collections.get(self.index_name)
            for chunk in chunks:
                embedding = self.embeddings.embed_query(chunk["text"])
                collection.data.insert(
                    properties={
                        "text": chunk["text"],
                        "metadata": str(chunk.get("metadata", {}))
                    },
                    vector=embedding
                )
            logger.info(f"Added {len(chunks)} documents to Weaviate collection {self.index_name}")
        except Exception as e:
            logger.error(f"Error adding documents to Weaviate: {e}")
            # Don't re-raise to ensure the API remains functional even if vector DB fails

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if self.weaviate is None:
            logger.warning("Weaviate is not available, returning empty results")
            return []
            
        try:
            collection = self.weaviate.collections.get(self.index_name)
            query_vec = self.embeddings.embed_query(query)
            results = collection.query.near_vector(query_vec, limit=top_k)
            docs: List[Dict[str, Any]] = []
            for res in results.objects:
                docs.append({
                    "text": res.properties["text"],
                    "metadata": res.properties.get("metadata", "")
                })
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents from Weaviate: {e}")
            return []  # Return empty list on error to maintain API stability

    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        if scan_prompt_injection(question):
            return {"answer": "Potential prompt injection detected.", "sources": [], "prompt": None}
            
        docs = self.retrieve(question, top_k=top_k)
        context = "\n".join([d["text"] for d in docs])
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        try:
            answer = self.llm.generate(prompt)
            return {
                "answer": answer,
                "sources": docs,
                "prompt": prompt
            }
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return {
                "answer": "Sorry, I encountered an error while processing your question.",
                "sources": docs,
                "prompt": prompt
            }
