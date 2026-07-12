from app.services.engineering.tools.base import BaseTool
from app.services.rag.pipeline import RAGPipeline


class DocumentSearchTool(BaseTool):
    name = "document_search"
    description = (
        "Search enterprise knowledge documents using "
        "the Sagesai RAG semantic search pipeline."
    )

    def __init__(self) -> None:
        self.rag_pipeline = RAGPipeline()

    async def execute(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict:
        results = self.rag_pipeline.search(
            query=query,
            limit=max_results,
        )

        return {
            "tool": self.name,
            "query": query,
            "matches": results,
            "match_count": len(results),
        }