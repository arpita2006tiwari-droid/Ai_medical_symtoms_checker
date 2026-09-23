# AI Medical Symptom Checker - Backend (Phase 2A)

This directory contains the FastAPI backend for the AI Medical Symptom Checker. The backend provides a RESTful API that loads the pre-trained Random Forest ML model and preprocessing artifacts to generate condition predictions based on input symptoms.

## Architecture

- **Framework:** FastAPI
- **Machine Learning Integration:** Uses the existing `.joblib` and `.json` artifacts from the `ml/` directory directly. No ML model retraining is done in the backend.
- **Service Layer:** `MLService` loads the model and artifacts on application startup, converting incoming symptoms into the exact feature vector structure expected by the trained model.

## Folder Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application initialization & CORS
│   ├── config.py            # Environment settings and paths
│   ├── schemas.py           # Pydantic validation models
│   ├── routes/              # API endpoints (health, predict)
│   ├── services/            # Core logic (MLService, symptom processing)
│   └── utils/               # Utilities (e.g., path resolution)
├── tests/                   # Pytest suite
├── requirements.txt         # Dependencies
├── .env.example             # Example environment variables
└── PHASE_2A_INSPECTION.md   # Initial inspection of ML artifacts
```

## Installation & Setup

1. **Create and activate a virtual environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   You can run it directly as the defaults in `app.config.py` point correctly to the project root. Alternatively, copy `.env.example` to `.env` if you want to override paths.

## Running FastAPI

To start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be accessible at:
- **Root endpoint:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints

### 1. `GET /api/health`
Checks if the backend is running and the ML model is successfully loaded into memory.

**Response Example:**
```json
{
  "status": "ok",
  "service": "AI Medical Symptom Checker API",
  "model_loaded": true
}
```

### 2. `POST /api/predict`
Predicts the top 3 possible conditions based on an input array of symptoms.

**Request Example:**
```json
{
  "symptoms": [
    "fever",
    "cough",
    "headache"
  ]
}
```

**Response Example:**
```json
{
  "success": true,
  "input": {
    "symptoms": [
      "fever",
      "cough",
      "headache"
    ]
  },
  "recognized_symptoms": [
    "cough",
    "headache"
  ],
  "unknown_symptoms": [
    "fever"
  ],
  "predictions": [
    {
      "condition": "Paralysis (brain hemorrhage)",
      "model_probability": 0.26
    },
    {
      "condition": "Bronchial Asthma",
      "model_probability": 0.15
    },
    {
      "condition": "Hypertension",
      "model_probability": 0.11
    }
  ],
  "disclaimer": "This tool provides preliminary information only and is not a medical diagnosis."
}
```

## Testing

Run the test suite via Pytest:
```bash
pytest
```

## Phase 2B — Medical Information Integration

In Phase 2B, the API prediction response was enriched with datasets containing medical descriptions, general precautions, and symptom severity scales, without modifying the underlying Machine Learning model.

### Datasets Loaded
- `symptom_Description.csv`: Matched by predicted disease string to return a description.
- `symptom_precaution.csv`: Matched by predicted disease string to return up to 4 precautions (ignoring empty strings).
- `Symptom-severity.csv`: Matched against the list of `recognized_symptoms` (cleaned to replace underscores with spaces) to return severity weights.

### Implementation Details
- The data is loaded exactly once into an in-memory dictionary during the FastAPI lifespan startup via `MedicalInfoService` to avoid costly disk I/O on every request.
- If a CSV is missing or a condition lacks a description/precaution, the API safely handles it by returning `null` or empty lists, avoiding crashes or artificially generated information.
- The symptom severities are only retrieved for symptoms that the ML model's vocabulary actually recognized. Unknown symptoms are safely ignored in severity lookups.

### Example Phase 2B Enriched Response:

```json
{
  "success": true,
  "input": {
    "symptoms": [
      "high fever",
      "cough",
      "headache"
    ]
  },
  "recognized_symptoms": [
    "high fever",
    "cough",
    "headache"
  ],
  "unknown_symptoms": [],
  "predictions": [
    {
      "condition": "Bronchial Asthma",
      "model_probability": 0.26,
      "description": "Bronchial asthma is a medical condition...",
      "precautions": [
        "switch to loose clothing",
        "take deep breaths",
        "get away from trigger",
        "seek help"
      ]
    }
  ],
  "symptom_severity": [
    {
      "symptom": "high fever",
      "severity": 7
    },
    {
      "symptom": "cough",
      "severity": 4
    }
  ],
  "disclaimer": "This tool provides preliminary information only and is not a medical diagnosis."
}
```

## Phase 2C — NLP Symptom Extraction

In Phase 2C, a dedicated `NLPService` was created to safely extract symptoms from natural language text (e.g. "I have a high fever and a cough").

### Approach and Limitations
- The extraction strictly maps user input against the exact 131 phrases found in the `symptom_vocabulary.json`. 
- No Large Language Models (LLMs) or external AI services were utilized. 
- Regular Expressions (`\b`) are dynamically compiled based on vocabulary lengths to correctly identify multi-word phrases ("high fever") without being confused by sub-strings ("fever").
- **Important Limitation:** Generic synonyms (like mapping "fever" to "high fever" or "migraine" to "headache") are deliberately not supported unless they exist in the original vocabulary/normalization map. The system will safely ignore unrecognized medical terms rather than invent a diagnosis.

### New Endpoints
1. `POST /api/extract-symptoms`: A testing endpoint. Send `{"text": "I have a high fever, cough and headache."}` to see strictly which symptoms are recognized.
2. `POST /api/analyze`: The main conversational endpoint. It combines the `NLPService` extraction with the existing `MLService` prediction and `MedicalInfoService` enrichments to output the final Top 3 conditions.

Example `POST /api/analyze` request:
```json
{
  "text": "I have a high fever, cough and headache."
}
```
*(The response perfectly matches the enriched Phase 2B `/api/predict` response structure).*

## Phase 2D — Dynamic Follow-Up Questions

The backend features a stateless follow-up question engine that collects additional relevant symptoms before prediction.

### Co-occurrence Engine
- When the server starts, `FollowUpService` reads the original `ml/data/raw/dataset.csv` and builds a symptom co-occurrence matrix.
- When generating a follow-up question, the engine ranks un-asked symptoms based on their co-occurrence frequency with the user's *currently recognized* symptoms. 
- It formats the highest-ranking candidate into a "yes/no" question (e.g., "Are you experiencing shortness of breath?").

### Architecture and Limitations
- The system asks a maximum of 3 questions to prevent fatigue.
- Answers are parsed using the `NLPService`. A user can answer "no", "yes", or provide free-text like "Yes, and I also have a headache". The NLP gracefully merges any newly discovered valid symptoms.
- The engine does **not** rely on Large Language Models, nor does it possess any encoded diagnostic logic. It strictly acts as a data-gathering mechanism for the ML pipeline.

### Endpoints
1. `POST /api/follow-up/start`: Pass `{"symptoms": ["cough"]}` to initialize the state and get the first question.
2. `POST /api/follow-up/answer`: Pass the conversational state, the `question_id`, and the user's `answer`. The engine evaluates the text, updates `recognized_symptoms`, and returns the next question.
3. Once `complete=true`, the final array of `recognized_symptoms` can be passed to the standard `POST /api/predict` endpoint for the final diagnosis.

## Phase 2E — Safety & Urgency Classification

The backend evaluates predicted symptoms against a rigid, controlled catalog of high-risk medical patterns to append an informational urgency classification to API predictions.

### Safety Engine Architecture
- The service loads `backend/app/data/safety_rules.json` on startup. 
- During `POST /api/predict` or `POST /api/analyze`, recognized symptoms are checked for intersections against the rule catalog. 
- Categorizes urgency into `routine`, `medical_attention`, or `urgent_attention`. If multiple rules hit, the highest urgency level is escalated.
- The `UrgencyAssessment` is attached directly onto the `PredictionResponse` safely, strictly avoiding modifications to the underlying Machine Learning algorithms.

### Rules and Limitations
- The catalog heavily relies solely on symptom definitions matching `symptom_vocabulary.json` exactly (e.g. `chest pain`, `altered sensorium`). 
- **Disclaimer**: These safety mappings are simplified, not clinically validated triage models, and they never declare a definitive diagnosis or medical emergency. 

## Phase 2F — Specialist Recommendation & Provider Information

The backend includes a dedicated `SpecialistService` to suggest appropriate medical specialists strictly based on ML predictions, avoiding hallucinated recommendations.

### Specialist & Provider Architecture
- The service maps exact ML conditions (e.g., `Heart attack` or `GERD`) to appropriate experts (e.g., `Cardiologist`, `Gastroenterologist`) using a controlled `specialist_mapping.json`.
- A robust fallback assigns users to a `General Physician` if condition matches fail.
- A placeholder API `POST /api/providers/info` provides information about future external API configurations (like Google Places) to explicitly prevent hallucinating fake local hospitals or doctors.
- The `SpecialistRecommendation` is securely attached directly onto the `PredictionResponse`, completely untangling it from diagnostic probabilities.

## Medical Disclaimer
This backend provides preliminary predictive condition matching based solely on an ML model trained on simulated datasets. **It does not provide actual medical diagnoses.** The prediction `model_probability` refers exclusively to the statistical confidence of the model based on its training data, not the real-world probability of a patient having a disease.
