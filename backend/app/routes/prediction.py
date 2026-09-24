from fastapi import APIRouter, HTTPException
from app.schemas import (
    SymptomPredictionRequest, 
    PredictionResponse,
    SymptomExtractionRequest,
    SymptomExtractionResponse,
    NaturalLanguageAnalysisRequest
)
from app.services.ml_service import ml_service
from app.services.medical_info_service import medical_info_service
from app.services.nlp_service import nlp_service
from app.services.safety_service import safety_service
from app.services.specialist_service import specialist_service
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.analysis import Analysis
from app.services.auth_service import get_optional_current_user

router = APIRouter()

def _build_prediction_response(symptoms_list: list[str], input_dict: dict, db: Session = None, current_user: User = None, source: str = None) -> PredictionResponse:
    if not ml_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail=f"ML Service is not available: {getattr(ml_service, 'load_error', 'Unknown error')}"
        )
        
    try:
        result = ml_service.predict(symptoms_list)
        
        # Enrich predictions with descriptions and precautions
        enriched_predictions = []
        for pred in result["predictions"]:
            condition = pred["condition"]
            desc = medical_info_service.get_description(condition)
            precs = medical_info_service.get_precautions(condition)
            
            enriched_predictions.append({
                "condition": condition,
                "model_probability": pred["model_probability"],
                "description": desc,
                "precautions": precs
            })
            
        # Get severities for recognized symptoms
        symptom_severities = []
        for sym in result["recognized_symptoms"]:
            sev = medical_info_service.get_severity(sym)
            if sev is not None:
                symptom_severities.append({
                    "symptom": sym,
                    "severity": sev
                })
                
        # Perform Safety Assessment
        urgency = safety_service.assess(result["recognized_symptoms"])
        
        # Determine Specialist Recommendation based on top prediction
        
        # Determine Specialist Recommendation based on top prediction
        top_condition = None
        if enriched_predictions:
            # Predictions are already sorted by model_probability descending
            top_condition = enriched_predictions[0]["condition"]
            
        specialist_rec = specialist_service.recommend(top_condition)
        
        disclaimer_text = "This tool provides preliminary information only and is not a medical diagnosis."
        
        # Save to DB if authenticated
        if current_user and db:
            analysis_record = Analysis(
                user_id=current_user.id,
                input_text=input_dict.get("text") or input_dict.get("message") or ", ".join(input_dict.get("symptoms", [])),
                recognized_symptoms=result["recognized_symptoms"],
                unknown_symptoms=result["unknown_symptoms"],
                predictions=enriched_predictions,
                symptom_severity=symptom_severities,
                urgency=urgency.model_dump() if hasattr(urgency, "model_dump") else (urgency if isinstance(urgency, dict) else None),
                specialist_recommendation=specialist_rec.model_dump() if hasattr(specialist_rec, "model_dump") else (specialist_rec if isinstance(specialist_rec, dict) else None),
                disclaimer=disclaimer_text,
                analysis_source=source
            )
            db.add(analysis_record)
            db.commit()
            
        return PredictionResponse(
            success=True,
            input=input_dict,
            recognized_symptoms=result["recognized_symptoms"],
            unknown_symptoms=result["unknown_symptoms"],
            predictions=enriched_predictions,
            symptom_severity=symptom_severities,
            urgency=urgency,
            specialist_recommendation=specialist_rec,
            disclaimer=disclaimer_text
        )
    except Exception as e:
        print(f"Error in predict: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction")

@router.post("/api/predict", response_model=PredictionResponse)
def predict_symptoms(request: SymptomPredictionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_optional_current_user)):
    """Phase 2A structured prediction endpoint"""
    return _build_prediction_response(request.symptoms, {"symptoms": request.symptoms}, db, current_user, "predict")

@router.post("/api/extract-symptoms", response_model=SymptomExtractionResponse)
def extract_symptoms_nlp(request: SymptomExtractionRequest):
    """Phase 2C NLP extraction testing endpoint"""
    extracted = nlp_service.extract_symptoms(request.text)
    return SymptomExtractionResponse(
        input_text=request.text,
        recognized_symptoms=extracted,
        symptom_count=len(extracted)
    )

@router.post("/api/analyze", response_model=PredictionResponse)
def analyze_natural_language(request: NaturalLanguageAnalysisRequest, db: Session = Depends(get_db), current_user: User = Depends(get_optional_current_user)):
    """Phase 2C end-to-end natural language analysis endpoint"""
    extracted = nlp_service.extract_symptoms(request.text)
    
    if not extracted:
        raise HTTPException(
            status_code=422,
            detail="No recognized symptoms found in the text. Please provide valid symptoms."
        )
        
    return _build_prediction_response(extracted, {"text": request.text}, db, current_user, "analyze")
