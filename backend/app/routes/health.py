from fastapi import APIRouter
from app.schemas import HealthResponse, RootResponse
from app.services.ml_service import ml_service

router = APIRouter()

@router.get("/", response_model=RootResponse)
def get_root():
    return RootResponse(
        message="AI Medical Symptom Checker API",
        version="0.1.0",
        status="running"
    )

@router.get("/api/health", response_model=HealthResponse)
def get_health():
    return HealthResponse(
        status="ok",
        service="AI Medical Symptom Checker API",
        model_loaded=ml_service.is_loaded
    )
