from pydantic import BaseModel, Field, field_validator, EmailStr, model_validator
from typing import List, Optional, Any
from datetime import datetime, timezone, date

class SymptomPredictionRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of symptoms")
    age: Optional[int] = Field(None, description="Age of the patient")
    age_unit: Optional[str] = Field(None, description="Unit for age (years, months, weeks, days)")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    patient_type: Optional[str] = Field(None, description="Type of patient, e.g., general, newborn")
    
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

    @model_validator(mode='after')
    def validate_newborn_requirements(self) -> 'SymptomPredictionRequest':
        if self.patient_type == 'newborn' and self.age is None:
            raise ValueError("Age is required for newborn patient type")
        return self

class SymptomExtractionRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Natural language text containing symptoms")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")
        return cleaned

class RecognizedSymptom(BaseModel):
    canonical: str
    original_phrase: str
    category: str
    source: str
    is_model_supported: bool

class SymptomExtractionResponse(BaseModel):
    input_text: str
    recognized_symptoms: List[str]
    detailed_symptoms: List[RecognizedSymptom] = []
    symptom_count: int

class NaturalLanguageAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Natural language text describing symptoms")
    age: Optional[int] = Field(None, description="Age of the patient")
    age_unit: Optional[str] = Field(None, description="Unit for age (years, months, weeks, days)")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    patient_type: Optional[str] = Field(None, description="Type of patient, e.g., general, newborn")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")
        return cleaned

    @model_validator(mode='after')
    def validate_newborn_requirements(self) -> 'NaturalLanguageAnalysisRequest':
        if self.patient_type == 'newborn' and self.age is None:
            raise ValueError("Age is required for newborn patient type")
        return self

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
    recommended_tips: List[str] = []
    when_to_seek_care: List[str] = []

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
    conversation_id: Optional[str] = Field(default=None, description="Optional ID to continue an existing conversation")
    age: Optional[int] = Field(None, description="Age of the patient")
    age_unit: Optional[str] = Field(None, description="Unit for age (years, months, weeks, days)")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    patient_type: Optional[str] = Field(None, description="Type of patient, e.g., general, newborn")

    @model_validator(mode='after')
    def validate_newborn_requirements(self) -> 'ChatRequest':
        if self.patient_type == 'newborn' and self.age is None:
            raise ValueError("Age is required for newborn patient type")
        return self

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

# Phase 4 DB Schemas

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(..., min_length=8, description="Must be at least 8 characters")

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    age: Optional[int] = None
    age_unit: Optional[str] = None
    gender: Optional[str] = None
    patient_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('created_at', 'updated_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    age_unit: Optional[str] = None
    gender: Optional[str] = None
    patient_type: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AnalysisResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    input_text: Optional[str] = None
    recognized_symptoms: List[str] = []
    unknown_symptoms: List[str] = []
    predictions: List[PredictionItem] = []
    symptom_severity: List[SymptomSeverity] = []
    urgency: Optional[UrgencyAssessment] = None
    specialist_recommendation: Optional[SpecialistRecommendation] = None
    disclaimer: str
    analysis_source: Optional[str] = None
    demographics: Optional[dict] = None

    model_config = {"from_attributes": True}

    @field_validator('created_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class ConversationMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('created_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessageResponse] = []

    model_config = {"from_attributes": True}

    @field_validator('created_at', 'updated_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class ModelMetadataResponse(BaseModel):
    model_version: str
    total_features: int
    total_conditions: int
    supported_features: List[str]
    supported_conditions: List[str]

class PainAssessmentRequest(BaseModel):
    body_region: str = Field(..., description="Body region where pain is located")
    pain_type: str = Field(..., description="Type of pain")
    severity: int = Field(..., ge=0, le=10, description="Pain severity on 0-10 scale")
    onset_duration: str = Field(..., description="When it started and how long it lasts")
    frequency: str = Field(..., description="Constant, intermittent, etc.")
    trend: str = Field(..., description="Improving, worsening, unchanged")
    associated_symptoms: List[str] = Field(default_factory=list, description="Other symptoms")
    notes: Optional[str] = Field(None, description="Optional notes")

    # Demographics integration
    age: Optional[int] = Field(None, description="Age of the patient")
    age_unit: Optional[str] = Field(None, description="Unit for age (years, months, weeks, days)")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    patient_type: Optional[str] = Field(None, description="Type of patient, e.g., general, newborn")

    @model_validator(mode='after')
    def validate_newborn_requirements(self) -> 'PainAssessmentRequest':
        if self.patient_type == 'newborn' and self.age is None:
            raise ValueError("Age is required for newborn patient type")
        return self

class PainAssessmentResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    body_region: str
    pain_type: str
    severity: int
    onset_duration: str
    frequency: str
    trend: str
    associated_symptoms: List[str]
    notes: Optional[str] = None
    analysis_id: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator('created_at', 'updated_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class MenstruationPreferenceRequest(BaseModel):
    reminders_enabled: bool = False
    reminder_days_before: int = Field(2, ge=1, le=7)

class MenstruationPreferenceResponse(MenstruationPreferenceRequest):
    user_id: str

    model_config = {"from_attributes": True}

class MenstrualCycleRequest(BaseModel):
    start_date: date = Field(..., description="Start date of period")
    end_date: Optional[date] = Field(None, description="End date of period")
    cycle_length: Optional[int] = Field(None, ge=15, le=100, description="Cycle length in days")
    flow_level: str = Field(..., description="light, medium, heavy, unknown")
    cramps_severity: int = Field(0, ge=0, le=10, description="0-10 severity")
    associated_symptoms: List[str] = Field(default_factory=list, description="Other symptoms")
    notes: Optional[str] = Field(None, description="Optional notes")

    # Demographics integration
    age: Optional[int] = Field(None, description="Age of the patient")
    age_unit: Optional[str] = Field(None, description="Unit for age (years, months, weeks, days)")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    patient_type: Optional[str] = Field(None, description="Type of patient, e.g., general, newborn")

    @model_validator(mode='after')
    def validate_dates(self) -> 'MenstrualCycleRequest':
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        if self.patient_type == 'newborn':
            raise ValueError("Newborn/infant patient type cannot track menstruation.")
        return self

class MenstrualCycleResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    start_date: date
    end_date: Optional[date]
    cycle_length: Optional[int]
    flow_level: str
    cramps_severity: int
    associated_symptoms: List[str]
    notes: Optional[str] = None
    analysis_id: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator('created_at', 'updated_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class MoodCheckinRequest(BaseModel):
    mood: str = Field(..., description="very low, low, neutral, good, very good")
    intensity: int = Field(..., ge=1, le=10, description="1-10 intensity")
    emotions: List[str] = Field(default_factory=list, description="anxious, sad, stressed, etc.")
    energy_level: Optional[str] = Field(None, description="low, medium, high")
    sleep_quality: Optional[str] = Field(None, description="poor, fair, good, excellent")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")
    cycle_id: Optional[str] = Field(None, description="Optional associated menstrual cycle ID")

class MoodCheckinResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    mood: str
    intensity: int
    emotions: List[str]
    energy_level: Optional[str]
    sleep_quality: Optional[str]
    notes: Optional[str]
    cycle_id: Optional[str]
    analysis_id: Optional[str]

    model_config = {"from_attributes": True}

    @field_validator('created_at', 'updated_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class MedicalImageResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('created_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class ImageObservationResponse(BaseModel):
    observations: str
    disclaimer: str = "These are AI-generated visual observations only and do not constitute a medical diagnosis. The model may incorrectly identify or miss visual features."

class MedicalReportResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str
    extracted_text: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('created_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class ReportSummaryResponse(BaseModel):
    summary: str
    disclaimer: str = "This AI summary uses only information present in the report. It may contain errors and does not constitute a medical diagnosis."

# Phase 9G - Consultation Preparation
class ConsultationPreparationRequest(BaseModel):
    main_concern: str = Field(..., description="Main reason for the visit")
    symptoms: Optional[str] = Field(None, description="Current symptoms")
    questions: Optional[str] = Field(None, description="Questions for the doctor")
    current_medicines: Optional[str] = Field(None, description="Current medications")
    allergies: Optional[str] = Field(None, description="Known allergies")

class ConsultationPreparationResponse(ConsultationPreparationRequest):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('created_at', 'updated_at', mode='after')
    @classmethod
    def set_timezone(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
