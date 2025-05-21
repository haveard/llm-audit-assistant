import pytest
from unittest.mock import patch, MagicMock
import io

# Patch Minio client before importing app modules
minio_patch = patch("app.api.routes.Minio", MagicMock())
minio_patch.start()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_status_endpoint():
    resp = client.get("/status")
    assert resp.status_code == 200
    assert "documents_loaded" in resp.json()

def test_upload_endpoint_mock(monkeypatch):
    # Mock the file processing and storage
    class DummyFile:
        filename = "test.txt"
        content_type = "text/plain"
        async def read(self):
            return b"hello world"

    def dummy_load_document(path):
        return ("hello world", {"filename": "test.txt", "filetype": ".txt", "size": 11, "date": "2025-05-21T00:00:00"})

    # Patch MinIO client
    class DummyMinioObj:
        def read(self):
            return b"hello world"
    class DummyMinioClient:
        def put_object(self, *a, **kw):
            pass
        def get_object(self, *a, **kw):
            return DummyMinioObj()
        def bucket_exists(self, *a, **kw):
            return True
        def make_bucket(self, *a, **kw):
            pass
    monkeypatch.setattr("app.api.routes.get_minio_client", lambda: DummyMinioClient())

    monkeypatch.setattr("app.api.routes.load_document", dummy_load_document)
    monkeypatch.setattr("app.api.routes.preprocess_document", lambda text, metadata=None: [{"text": text, "metadata": metadata or {}}])
    monkeypatch.setattr("app.api.routes.rag", type("DummyRag", (), {"add_documents": lambda self, chunks: None})())

    response = client.post("/upload", files={"file": ("test.txt", b"hello world")})
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"


def test_query_endpoint_mock(monkeypatch):
    class DummyRequest:
        pass

    dummy_sources = [{"text": "chunk1"}]
    monkeypatch.setattr("app.api.routes.sanitize_input", lambda x: x)
    monkeypatch.setattr("app.api.routes.scan_prompt_injection", lambda x: False)
    monkeypatch.setattr("app.api.routes.rag", type("DummyRag", (), {
        "retrieve": lambda self, q, top_k=3: dummy_sources,
        "query": lambda self, q, top_k=3: {"answer": "42", "sources": dummy_sources}
    })())
    monkeypatch.setattr("app.api.routes.sanitize_output", lambda x: x)
    async def dummy_log_request(*a, **kw):
        return None
    monkeypatch.setattr("app.api.routes.log_request", dummy_log_request)

    response = client.post("/query", json={"question": "What is the answer?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "42"
    assert response.json()["sources"] == dummy_sources

def teardown_module(module):
    minio_patch.stop()
