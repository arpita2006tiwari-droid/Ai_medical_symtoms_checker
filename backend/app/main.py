from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import health, prediction, followup, providers, chat
from app.services.medical_info_service import medical_info_service
from app.services.nlp_service import nlp_service
from app.services.followup_service import followup_service
from app.services.safety_service import safety_service
from app.services.specialist_service import specialist_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load data on startup
    medical_info_service.load_data()
    nlp_service.load_data()
    followup_service.load_data()
    safety_service.load_data()
    specialist_service.load_data()
    yield
    # Clean up on shutdown if needed

app = FastAPI(
    title="AI Medical Symptom Checker API",
    description="API for providing condition predictions based on symptoms.",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for potential frontend integrations
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(followup.router)
app.include_router(providers.router)
app.include_router(chat.router)
