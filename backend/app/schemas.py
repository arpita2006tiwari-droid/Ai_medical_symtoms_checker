from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class SymptomPredictionRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of symptoms")
    
    @field_validator('symptoms')
    @classmethod
    def validate_symptoms(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Symptom list cannot be empty")
        
        # Remove duplicates and trim whitespace
        seen = set()
        cleaned_symptoms = []
        for sym in v:
            sym_clean = sym.strip()
            if sym_clean and sym_clean not in seen:
                seen.add(sym_clean)
                cleaned_symptoms.append(sym_clean)
        
        if not cleaned_symptoms:
            raise ValueError("Must provide at least one valid symptom string")
            
        return cleaned_symptoms

class SymptomExtractionRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Natural language text containing symptoms")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")
        return cleaned

class SymptomExtractionResponse(BaseModel):
    input_text: str
    recognized_symptoms: List[str]
    symptom_count: int

class NaturalLanguageAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Natural language text describing symptoms")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")
        return cleaned

class FollowUpQuestion(BaseModel):
    id: str
    type: str
    text: str

class FollowUpStartRequest(BaseModel):
    symptoms: List[str] = Field(..., description="List of recognized symptoms")

class FollowUpState(BaseModel):
    recognized_symptoms: List[str]
    asked_questions: List[str] = []
    answers: dict = {}
    follow_up_count: int = 0

class FollowUpResponse(BaseModel):
    state: FollowUpState
    question: Optional[FollowUpQuestion] = None
    complete: bool

class FollowUpAnswerRequest(BaseModel):
    state: FollowUpState
    question_id: str
    answer: str

class PredictionItem(BaseModel):
    condition: str
    model_probability: float
    description: Optional[str] = None
    precautions: List[str] = []

class SafetyRuleMatch(BaseModel):
    rule_id: str
    reason: str

class UrgencyAssessment(BaseModel):
    level: str
    message: str
    matched_rules: List[SafetyRuleMatch]

class SpecialistRecommendation(BaseModel):
    specialist: str
    reason: str
    basis: str
    condition: Optional[str] = None

class ProviderInfoResponse(BaseModel):
    available: bool
    message: str

class SymptomSeverity(BaseModel):
    symptom: str
    severity: int

class PredictionResponse(BaseModel):
    success: bool
    input: dict
    recognized_symptoms: List[str]
    unknown_symptoms: List[str]
    predictions: List[PredictionItem]
    symptom_severity: List[SymptomSeverity] = []
    urgency: Optional[UrgencyAssessment] = None
    specialist_recommendation: Optional[SpecialistRecommendation] = None
    disclaimer: str = "This tool provides preliminary information only and is not a medical diagnosis."

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, description="User conversational input")

class ChatResponse(PredictionResponse):
    response: str = Field(..., description="Natural language conversational response from the LLM")

class HealthResponse(BaseModel):
    status: str
    service: str
    model_loaded: bool

class RootResponse(BaseModel):
    message: str
    version: str
    status: str
