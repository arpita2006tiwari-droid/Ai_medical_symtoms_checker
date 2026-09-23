from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from app.utils.paths import get_project_root

class Settings(BaseSettings):
    # Determine the project root
    PROJECT_ROOT: str = str(get_project_root())
    
    # ML paths relative to the project root
    MODEL_PATH: str = Field(default="ml/models/symptom_random_forest.joblib")
    VOCABULARY_PATH: str = Field(default="ml/artifacts/symptom_vocabulary.json")
    NORMALIZATION_PATH: str = Field(default="ml/artifacts/symptom_normalization.json")
    
    # Phase 3 LLM Config
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")
    LLM_ENABLED: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
