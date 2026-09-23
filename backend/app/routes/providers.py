from fastapi import APIRouter
from app.schemas import ProviderInfoResponse
from app.services.provider_service import provider_service

router = APIRouter()

@router.post("/api/providers/info", response_model=ProviderInfoResponse)
def get_providers_info():
    """
    Phase 2F provider-search information endpoint.
    Returns informational structure about future integrations, actively avoiding generating fake data.
    """
    return provider_service.get_provider_info()
