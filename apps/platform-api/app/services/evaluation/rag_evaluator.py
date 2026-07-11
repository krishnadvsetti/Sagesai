import json

from app.services.ai.gateway import AIGateway


class RAGEvaluator:
    def __init__(self) -> None:
        self.ai_gateway = AIGateway()

    async def evaluate(
        self,
        question: str,
        answer: str,
        contexts: list[str],
    ) -> dict:
        context_text = "\n\n".join(
            f"[Context {index + 1}]\n{context}"
            for index, context in enumerate(contexts)
        )

        prompt = f"""
Evaluate this RAG response.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context_text}

GENERATED ANSWER:
{answer}

Score each metric from 0.0 to 1.0:

1. groundedness:
How well is the answer supported by the retrieved context?

2. answer_relevance:
How directly does the answer address the question?

3. context_relevance:
How relevant is the retrieved context to the question?

Return ONLY valid JSON in exactly this format:

{{
  "groundedness": 0.0,
  "answer_relevance": 0.0,
  "context_relevance": 0.0,
  "evaluation": "brief explanation"
}}
"""

        raw_result = await self.ai_gateway.generate(
            prompt=prompt,
            system_instruction=(
                "You are an LLM evaluation system. "
                "Evaluate RAG outputs consistently and conservatively. "
                "Return valid JSON only."
            ),
        )

        cleaned = (
            raw_result
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(cleaned)

        groundedness = self._normalize_score(
            result["groundedness"]
        )
        answer_relevance = self._normalize_score(
            result["answer_relevance"]
        )
        context_relevance = self._normalize_score(
            result["context_relevance"]
        )

        overall_score = round(
            (
                groundedness
                + answer_relevance
                + context_relevance
            )
            / 3,
            4,
        )

        return {
            "groundedness": groundedness,
            "answer_relevance": answer_relevance,
            "context_relevance": context_relevance,
            "overall_score": overall_score,
            "evaluation": result["evaluation"],
        }

    @staticmethod
    def _normalize_score(value: float) -> float:
        return round(
            max(0.0, min(1.0, float(value))),
            4,
        )