import uuid
from pathlib import Path

from app.services.rag.chunking import TextChunker
from app.services.rag.document_loader import DocumentLoader
from app.services.rag.embeddings import EmbeddingService
from app.services.rag.vector_store import VectorStore


class RAGPipeline:
    def __init__(self) -> None:
        self.loader = DocumentLoader()
        self.chunker = TextChunker()
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStore()

    def ingest(
        self,
        file_path: Path,
        document_id: str,
        filename: str,
    ) -> int:
        text = self.loader.load(file_path)
        chunks = self.chunker.split(text)

        if not chunks:
            raise ValueError("No text could be extracted from the document")

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
    ) -> list[dict]:
        query_vector = self.embeddings.embed_query(query)

        results = self.vector_store.search(
            query_embedding=query_vector,
            limit=limit,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "content": document,
                "metadata": metadata,
                "score": 1 - distance,
            }
            for document, metadata, distance in zip(
                documents,
                metadatas,
                distances,
                strict=False,
            )
        ]