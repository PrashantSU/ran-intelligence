"""Tests for the RAG API service and endpoint."""

import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

from ran_intelligence.api.app import create_app
from ran_intelligence.api.services import RAGService


class FakeModel:
    def encode(self, texts, **kwargs):
        return np.array([[1.0, 0.0]], dtype=np.float32)


class FakeVectorIndex:
    ntotal = 1
    d = 2


class FakeBM25:
    pass


def create_index_files(path):
    path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "model_name": "test-model",
        "document_count": 1,
        "embedding_dimension": 2,
        "retrieval_method": "FAISS + BM25 + Reciprocal Rank Fusion",
    }

    documents = [{
        "chunk_id": "chunk-001",
        "text": "Physical downlink shared channel in 5G NR.",
        "metadata": {
            "source": "3gpp-ts-38-211.pdf",
            "title": "Physical channels and modulation",
            "page": 42,
            "total_pages": 171,
            "chunk_index": 10,
        },
    }]

    (path / "manifest.json").write_text(json.dumps(manifest))
    (path / "documents.json").write_text(json.dumps(documents))
    (path / "faiss.index").write_bytes(b"fake-faiss")
    (path / "bm25.pkl").write_bytes(b"fake-bm25")


def test_rag_service_loads_index_once(tmp_path, monkeypatch):
    import faiss
    from sentence_transformers import SentenceTransformer

    create_index_files(tmp_path)
    import pickle
    monkeypatch.setattr(pickle, "load", lambda file: FakeBM25())

    monkeypatch.setattr(
        faiss,
        "read_index",
        lambda path: FakeVectorIndex(),
    )

    model_calls = []
    monkeypatch.setattr(
        SentenceTransformer,
        "__new__",
        lambda cls, model_name: (
            model_calls.append(model_name) or FakeModel()
        ),
    )

    service = RAGService(tmp_path)

    first = service.load()
    second = service.load()

    assert first is second
    assert len(model_calls) == 1
    assert first["document_count"] == 1
    assert first["documents"][0]["chunk_id"] == "chunk-001"


def test_rag_service_rejects_manifest_document_mismatch(
    tmp_path, monkeypatch
):
    import faiss
    from sentence_transformers import SentenceTransformer

    create_index_files(tmp_path)
    import pickle
    monkeypatch.setattr(pickle, "load", lambda file: FakeBM25())

    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["document_count"] = 2
    manifest_path.write_text(json.dumps(manifest))

    monkeypatch.setattr(
        faiss,
        "read_index",
        lambda path: FakeVectorIndex(),
    )
    monkeypatch.setattr(
        SentenceTransformer,
        "__new__",
        lambda cls, model_name: FakeModel(),
    )

    service = RAGService(tmp_path)

    with pytest.raises(ValueError, match="document count"):
        service.load()


def test_rag_service_rejects_faiss_dimension_mismatch(
    tmp_path, monkeypatch
):
    import faiss
    from sentence_transformers import SentenceTransformer

    create_index_files(tmp_path)
    import pickle
    monkeypatch.setattr(pickle, "load", lambda file: FakeBM25())

    class WrongDimensionIndex(FakeVectorIndex):
        d = 3

    monkeypatch.setattr(
        faiss,
        "read_index",
        lambda path: WrongDimensionIndex(),
    )
    monkeypatch.setattr(
        SentenceTransformer,
        "__new__",
        lambda cls, model_name: FakeModel(),
    )

    service = RAGService(tmp_path)

    with pytest.raises(ValueError, match="dimension"):
        service.load()


def test_rag_service_search_returns_source_metadata(
    tmp_path, monkeypatch
):
    import faiss
    from sentence_transformers import SentenceTransformer

    from ran_intelligence.rag import indexing

    create_index_files(tmp_path)
    import pickle
    monkeypatch.setattr(pickle, "load", lambda file: FakeBM25())

    monkeypatch.setattr(
        faiss,
        "read_index",
        lambda path: FakeVectorIndex(),
    )
    monkeypatch.setattr(
        SentenceTransformer,
        "__new__",
        lambda cls, model_name: FakeModel(),
    )

    monkeypatch.setattr(
        indexing,
        "hybrid_search",
        lambda **kwargs: [{
            "chunk_id": "chunk-001",
            "text": "Physical downlink shared channel in 5G NR.",
            "metadata": {
                "source": "3gpp-ts-38-211.pdf",
                "title": "Physical channels and modulation",
                "page": 42,
                "total_pages": 171,
                "chunk_index": 10,
            },
            "rrf_score": 0.03,
            "vector_rank": 1,
            "bm25_rank": 2,
        }],
    )

    service = RAGService(tmp_path)
    result = service.search("What is PDSCH?")

    assert result["result_count"] == 1
    assert result["index_document_count"] == 1

    chunk = result["results"][0]
    assert chunk["source"] == "3gpp-ts-38-211.pdf"
    assert chunk["page"] == 42
    assert chunk["chunk_id"] == "chunk-001"
    assert chunk["vector_rank"] == 1
    assert chunk["bm25_rank"] == 2


def test_rag_api_search_endpoint(monkeypatch):

    app = create_app()

    class FakeRAGService:
        def __init__(self, index_path):
            self.index_path = index_path

        def search(self, query, top_k, candidate_k, rrf_k):
            return {
                "query": query,
                "result_count": 1,
                "index_document_count": 3168,
                "retrieval_method": "FAISS + BM25 + Reciprocal Rank Fusion",
                "results": [{
                    "rank": 1,
                    "chunk_id": "chunk-001",
                    "text": "5G NR physical channels.",
                    "source": "3gpp-ts-38-211.pdf",
                    "title": "Physical channels",
                    "page": 42,
                    "total_pages": 171,
                    "chunk_index": 10,
                    "rrf_score": 0.03,
                    "vector_rank": 1,
                    "bm25_rank": 1,
                }],
            }

    import importlib
    api_module = importlib.import_module("ran_intelligence.api.app")
    monkeypatch.setattr(api_module, "RAGService", FakeRAGService)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/rag/search",
            json={"query": "What is PDSCH?", "top_k": 5},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result_count"] == 1
    assert payload["results"][0]["page"] == 42


def test_rag_api_rejects_short_query():
    app = create_app()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/rag/search",
            json={"query": "x"},
        )

    assert response.status_code == 422


def test_rag_service_reports_missing_index(tmp_path):
    service = RAGService(tmp_path)

    with pytest.raises(FileNotFoundError, match="RAG index files missing"):
        service.load()
