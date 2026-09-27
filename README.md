# AI Medical Symptom Checker (Academic Prototype)

This is an academic prototype for an AI-powered medical symptom checker. **It is not a clinically validated medical product and should not be used for diagnosis or treatment.**

## Features

- **Guest Mode**: Start an assessment without logging in. Data is held ephemerally.
- **Symptom Recognition**: Extracts medical symptoms from natural language text using a fine-tuned NLP model, with graceful fallbacks.
- **Random Forest Prediction Engine**: Predicts potential medical conditions based on extracted symptoms and demographic data (Adults/Children).
- **Demographics & Newborn Safeguards**: Safe routing for newborns and infants, preventing AI model diagnosis and deferring to safety rules.
- **Body Cramps & Pain Assessment**: Detailed tracking of pain severity, location, frequency, and trends.
- **Menstruation Tracking**: Track menstrual cycles, length, flow, and symptoms.
- **Mood Tracking**: Log daily moods, emotional states, energy levels, and sleep quality with automated crisis intervention alerts.
- **Image Uploads (Visual AI)**: Securely attach images of visible symptoms (e.g., rashes) for AI-generated visual observations.
- **Medical Report Analysis**: Upload PDF or image-based medical reports for summarized context extraction.
- **Consultation Summaries**: Generate self-reported summaries to take to a doctor, structuring concerns, symptoms, medications, and questions.
- **Safety Service & Emergency Flags**: Detects crisis keywords (e.g., "heart attack", "suicide") and immediately surfaces emergency contacts.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Axios.
- **Backend**: FastAPI, Python, SQLAlchemy, Alembic.
- **Database**: PostgreSQL.
- **Authentication**: JWT token-based authentication with protected routes.
- **AI/ML**: Random Forest models (`scikit-learn`), Google Gemini API for medical text extraction and summarization.

## Prerequisites

1.  Python 3.10+
2.  Node.js 18+ and npm
3.  PostgreSQL 14+
4.  A Google Gemini API Key

## Setup & Installation

### 1. Database Setup

Ensure PostgreSQL is running. Create a database for the project:
```sql
CREATE DATABASE ai_medcheck;
```

### 2. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    Create a `.env` file in the `backend/` directory with the following variables:
    ```ini
    DATABASE_URL=postgresql://user:password@localhost:5432/ai_medcheck
    SECRET_KEY=your_super_secret_key_for_jwt
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=1440
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
5.  Run Database Migrations:
    ```bash
    alembic upgrade head
    ```
6.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```

### 3. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Configure Environment Variables:
    Create a `.env` file in the `frontend/` directory:
    ```ini
    VITE_API_URL=http://localhost:8000/api
    ```
4.  Start the Vite development server:
    ```bash
    npm run dev
    ```

## Testing

To run the automated tests for the backend (including integration and security tests):

1.  Navigate to the backend directory and ensure your virtual environment is active.
2.  Run pytest:
    ```bash
    pytest
    ```

*Note: The tests use a test database session. However, ensure you do not run tests against your production database as they perform CRUD operations.*

## Important Safety Disclaimers

- This application is a prototype.
- **Medical Emergency**: If you are experiencing a medical emergency, severe pain, or difficulty breathing, contact emergency services immediately (e.g., 911 or 112).
- **No Diagnostics**: The output provided by the AI models does not constitute clinical advice, diagnosis, or treatment.
- **Privacy**: Do not upload sensitive, identifiable images or personal information meant for clinical environments into this application.
