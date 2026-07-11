from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.company_secretary import (
    ComplianceAnalysisRequest,
    ComplianceAnalysisResponse,
    GovernanceQueryRequest,
    GovernanceQueryResponse,
)
from app.services.company_secretary.service import CompanySecretaryService

router = APIRouter(
    prefix="/company-secretary",
    tags=["Company Secretary"],
)


@router.post(
    "/analyze",
    response_model=ComplianceAnalysisResponse,
)
async def analyze_corporate_document(
    payload: ComplianceAnalysisRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.COMPLIANCE_OFFICER,
        )
    ),
) -> ComplianceAnalysisResponse:
    service = CompanySecretaryService()

    analysis = await service.analyze_compliance(
        document_text=payload.document_text,
    )

    return ComplianceAnalysisResponse(analysis=analysis)


@router.post(
    "/ask",
    response_model=GovernanceQueryResponse,
)
async def ask_governance_question(
    payload: GovernanceQueryRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.COMPLIANCE_OFFICER,
        )
    ),
) -> GovernanceQueryResponse:
    service = CompanySecretaryService()

    answer, sources = await service.ask_governance_question(
        question=payload.question,
        limit=payload.limit,
    )

    return GovernanceQueryResponse(
        question=payload.question,
        answer=answer,
        sources=sources,
    )