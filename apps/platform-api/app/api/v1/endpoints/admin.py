from fastapi import APIRouter, Depends

from app.api.dependencies.auth import require_roles
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
) -> dict[str, str]:
    return {
        "message": "Welcome to the Sagesai administration dashboard",
        "user": current_user.email,
        "role": current_user.role.value,
    }