import time

from app.services.evaluation.datasets.rag_cases import (
    RAG_EVALUATION_CASES,
)
from app.services.evaluation.rag_evaluator import RAGEvaluator


MIN_GROUNDEDNESS = 0.70
MIN_ANSWER_RELEVANCE = 0.70
MIN_CONTEXT_RELEVANCE = 0.70
MIN_OVERALL_SCORE = 0.70


class RAGEvaluationRunner:
    def __init__(self) -> None:
        self.evaluator = RAGEvaluator()

    async def run(self) -> dict:
        results = []

        for case in RAG_EVALUATION_CASES:
            started_at = time.perf_counter()

            evaluation = await self.evaluator.evaluate(
                question=case["question"],
                answer=case["answer"],
                contexts=case["contexts"],
            )

            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            results.append(
                {
                    "name": case["name"],
                    **evaluation,
                    "latency_ms": latency_ms,
                }
            )

        case_count = len(results)

        average_groundedness = round(
            sum(
                result["groundedness"]
                for result in results
            )
            / case_count,
            4,
        )

        average_answer_relevance = round(
            sum(
                result["answer_relevance"]
                for result in results
            )
            / case_count,
            4,
        )

        average_context_relevance = round(
            sum(
                result["context_relevance"]
                for result in results
            )
            / case_count,
            4,
        )

        average_overall_score = round(
            sum(
                result["overall_score"]
                for result in results
            )
            / case_count,
            4,
        )

        average_latency_ms = round(
            sum(
                result["latency_ms"]
                for result in results
            )
            / case_count,
            2,
        )

        passed = (
            average_groundedness >= MIN_GROUNDEDNESS
            and average_answer_relevance
            >= MIN_ANSWER_RELEVANCE
            and average_context_relevance
            >= MIN_CONTEXT_RELEVANCE
            and average_overall_score >= MIN_OVERALL_SCORE
        )

        benchmark_status = (
            "passed" if passed else "failed"
        )

        return {
            "case_count": case_count,
            "average_groundedness": average_groundedness,
            "average_answer_relevance": (
                average_answer_relevance
            ),
            "average_context_relevance": (
                average_context_relevance
            ),
            "average_overall_score": average_overall_score,
            "average_latency_ms": average_latency_ms,
            "benchmark_status": benchmark_status,
            "passed": passed,
            "results": results,
        }