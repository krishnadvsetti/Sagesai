from pathlib import Path
from unittest.mock import Mock

import pytest

from app.services.rag.pipeline import RAGPipeline


def build_pipeline() -> RAGPipeline:
    pipeline = RAGPipeline.__new__(RAGPipeline)

    pipeline.loader = Mock()
    pipeline.chunker = Mock()
    pipeline.embeddings = Mock()
    pipeline.vector_store = Mock()
    pipeline.reranker = Mock()

    return pipeline


def test_rag_ingest_creates_chunks_and_vectors():
    pipeline = build_pipeline()

    pipeline.loader.load.return_value = "Enterprise AI platform"
    pipeline.chunker.split.return_value = [
        "Enterprise AI",
        "platform architecture",
    ]
    pipeline.embeddings.embed_documents.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    result = pipeline.ingest(
        file_path=Path("document.txt"),
        document_id="doc-123",
        filename="document.txt",
    )

    assert result == 2

    pipeline.vector_store.add.assert_called_once()

    call = pipeline.vector_store.add.call_args.kwargs

    assert call["ids"] == [
        "doc-123-0",
        "doc-123-1",
    ]

    assert call["metadatas"][0]["document_id"] == "doc-123"


def test_rag_ingest_rejects_empty_document():
    pipeline = build_pipeline()

    pipeline.loader.load.return_value = ""
    pipeline.chunker.split.return_value = []

    with pytest.raises(
        ValueError,
        match="No text could be extracted",
    ):
        pipeline.ingest(
            file_path=Path("empty.txt"),
            document_id="doc-empty",
            filename="empty.txt",
        )


def test_rag_search_filters_low_scores_and_reranks():
    pipeline = build_pipeline()

    pipeline.embeddings.embed_query.return_value = [0.1, 0.2]

    pipeline.vector_store.search.return_value = {
        "documents": [[
            "Highly relevant result",
            "Low relevance result",
        ]],
        "metadatas": [[
            {"document_id": "1"},
            {"document_id": "2"},
        ]],
        "distances": [[
            0.1,
            0.95,
        ]],
    }

    pipeline.reranker.rerank.return_value = [
        {
            "content": "Highly relevant result",
            "metadata": {"document_id": "1"},
            "score": 0.9,
            "rerank_score": 5.0,
        }
    ]

    results = pipeline.search(
        query="enterprise architecture",
        limit=5,
        min_score=0.2,
    )

    assert len(results) == 1
    assert results[0]["content"] == "Highly relevant result"

    candidates = (
        pipeline.reranker.rerank.call_args.kwargs["results"]
    )

    assert len(candidates) == 1
    assert candidates[0]["score"] == pytest.approx(0.9)