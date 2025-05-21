# Vector search + prompt injection guard

from app.llm.client import LLMClient
from app.utils.security import scan_prompt_injection
from langchain_openai import OpenAIEmbeddings
from app.llm.prompt_template import PROMPT_TEMPLATE
import os
from typing import List, Dict, Any
import weaviate

class RAGPipeline:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        self.weaviate = weaviate.WeaviateClient(
            connection_params=weaviate.connect.ConnectionParams.from_url(self.weaviate_url, grpc_port=50051)
        )
        self.weaviate.connect()
        self.embeddings = OpenAIEmbeddings()
        self.index_name = os.getenv("WEAVIATE_INDEX", "DocumentChunk")
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        # v4: Use collections API
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

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
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

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
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

    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        if scan_prompt_injection(question):
            return {"answer": "Potential prompt injection detected.", "sources": [], "prompt": None}
        docs = self.retrieve(question, top_k=top_k)
        context = "\n".join([d["text"] for d in docs])
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        answer = self.llm.generate(prompt)
        return {
            "answer": answer,
            "sources": docs,
            "prompt": prompt
        }
