from fastapi import APIRouter

from backend.common.identity.model.identity import IdentityContext
from backend.services.identity.model.common import IdentityRequest, TenantRequest, RegisterRequest, RegisterVO
from backend.services.identity.model.tenant import TenantDTO
from backend.services.identity.runtime import get_identity_service

router = APIRouter(prefix="/identity",tags=["identity"])

@router.post("/verify")
async def verify_identity(
    request: IdentityRequest
) -> IdentityContext | None:
    return await get_identity_service().authenticate_credentials(request.username, request.password,request.tenant_id)


@router.post("/create_tenant")
async def create_tenant(request: TenantRequest) -> TenantDTO | None:
    return await get_identity_service().create_tenant(request)


@router.post("/register")
async def register(request: RegisterRequest) -> RegisterVO | None:
    return await get_identity_service().register(request)