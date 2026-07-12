from pathlib import Path

from app.services.rag.chunking import TextChunker
from app.services.rag.document_loader import DocumentLoader
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.reranker import RAGReranker
from app.services.rag.vector_store import VectorStore


class RAGPipeline:
    def __init__(self) -> None:
        self.loader = DocumentLoader()
        self.chunker = TextChunker()
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStore()
        self.reranker = RAGReranker()

    def ingest(
        self,
        file_path: Path,
        document_id: str,
        filename: str,
    ) -> int:
        text = self.loader.load(file_path)
        chunks = self.chunker.split(text)

        if not chunks:
            raise ValueError(
                "No text could be extracted from the document"
            )

        vectors = self.embeddings.embed_documents(chunks)

        ids = [
            f"{document_id}-{index}"
            for index in range(len(chunks))
        ]

        metadatas = [
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
            }
            for index in range(len(chunks))
        ]

        self.vector_store.add(
            ids=ids,
            documents=chunks,
            embeddings=vectors,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.2,
    ) -> list[dict]:
        query_vector = self.embeddings.embed_query(query)

        candidate_limit = min(limit * 3, 30)

        results = self.vector_store.search(
            query_embedding=query_vector,
            limit=candidate_limit,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        candidates = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
            strict=False,
        ):
            semantic_score = 1 - float(distance)

            if semantic_score < min_score:
                continue

            candidates.append(
                {
                    "content": document,
                    "metadata": metadata,
                    "score": semantic_score,
                }
            )

        return self.reranker.rerank(
            query=query,
            results=candidates,
            limit=limit,
        )