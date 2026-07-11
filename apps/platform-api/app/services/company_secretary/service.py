from app.services.ai.gateway import AIGateway
from app.services.rag.pipeline import RAGPipeline


class CompanySecretaryService:
    def __init__(self) -> None:
        self.ai_gateway = AIGateway()
        self.rag_pipeline = RAGPipeline()

    async def analyze_compliance(
        self,
        document_text: str,
    ) -> str:
        prompt = f"""
Analyze the following corporate document.

Identify:
1. Document purpose
2. Key governance matters
3. Obligations and responsibilities
4. Important dates or deadlines explicitly stated
5. Compliance risks
6. Required actions
7. Items requiring professional or regulatory verification

Do not invent laws, deadlines, obligations, or regulatory requirements
that are not supported by the supplied document.

Document:
{document_text}
"""

        return await self.ai_gateway.generate(
            prompt=prompt,
            system_instruction=(
                "You are Sagesai's corporate governance analysis assistant. "
                "Analyze supplied information carefully and distinguish document "
                "facts from recommendations. Do not present uncertain legal or "
                "regulatory conclusions as established facts."
            ),
        )

    async def ask_governance_question(
        self,
        question: str,
        limit: int,
    ) -> tuple[str, list[dict]]:
        sources = self.rag_pipeline.search(
            query=question,
            limit=limit,
        )

        if not sources:
            return (
                "The available documents do not contain enough information.",
                [],
            )

        context = "\n\n".join(
            f"[Source {index + 1}]\n{source['content']}"
            for index, source in enumerate(sources)
        )

        prompt = f"""
Answer the governance question using only the retrieved context.

Context:
{context}

Question:
{question}

Clearly state when the supplied context is insufficient.
"""

        answer = await self.ai_gateway.generate(
            prompt=prompt,
            system_instruction=(
                "You are Sagesai's corporate governance information assistant. "
                "Ground every answer in the supplied context."
            ),
        )

        return answer, sources