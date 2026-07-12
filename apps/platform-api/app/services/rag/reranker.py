from sentence_transformers import CrossEncoder


class RAGReranker:
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: list[dict],
        limit: int = 5,
    ) -> list[dict]:
        if not results:
            return []

        pairs = [
            [query, result["content"]]
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked = []

        for result, score in zip(
            results,
            scores,
            strict=False,
        ):
            item = result.copy()
            item["rerank_score"] = float(score)
            reranked.append(item)

        reranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return reranked[:limit]