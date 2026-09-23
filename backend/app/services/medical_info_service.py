import os
import pandas as pd
from app.config import settings
from app.utils.paths import get_project_root

class MedicalInfoService:
    def __init__(self):
        self._descriptions: dict[str, str] = {}
        self._precautions: dict[str, list[str]] = {}
        self._severities: dict[str, int] = {}
        self.is_loaded = False

    def load_data(self):
        if self.is_loaded:
            return

        project_root = get_project_root()
        desc_path = os.path.join(project_root, "ml/data/raw/symptom_Description.csv")
        prec_path = os.path.join(project_root, "ml/data/raw/symptom_precaution.csv")
        sev_path = os.path.join(project_root, "ml/data/raw/Symptom-severity.csv")

        # Load Descriptions
        if os.path.exists(desc_path):
            try:
                df_desc = pd.read_csv(desc_path)
                for _, row in df_desc.iterrows():
                    disease = str(row['Disease']).strip()
                    self._descriptions[disease] = str(row['Description']).strip()
            except Exception as e:
                print(f"Warning: Failed to load descriptions from {desc_path}: {e}")

        # Load Precautions
        if os.path.exists(prec_path):
            try:
                df_prec = pd.read_csv(prec_path)
                for _, row in df_prec.iterrows():
                    disease = str(row['Disease']).strip()
                    precs = []
                    for i in range(1, 5):
                        col = f'Precaution_{i}'
                        if col in row and pd.notna(row[col]):
                            val = str(row[col]).strip()
                            if val:
                                precs.append(val)
                    self._precautions[disease] = precs
            except Exception as e:
                print(f"Warning: Failed to load precautions from {prec_path}: {e}")

        # Load Severities
        if os.path.exists(sev_path):
            try:
                df_sev = pd.read_csv(sev_path)
                for _, row in df_sev.iterrows():
                    # Clean the raw symptom to match the recognized vocabulary format
                    raw_symptom = str(row['Symptom']).strip().replace('_', ' ').lower()
                    self._severities[raw_symptom] = int(row['weight'])
            except Exception as e:
                print(f"Warning: Failed to load severities from {sev_path}: {e}")

        self.is_loaded = True

    def get_description(self, condition: str) -> str | None:
        """Returns the description for a given condition, or None if not found."""
        return self._descriptions.get(condition.strip())

    def get_precautions(self, condition: str) -> list[str]:
        """Returns a list of precautions for a given condition. Empty list if not found."""
        return self._precautions.get(condition.strip(), [])

    def get_severity(self, symptom: str) -> int | None:
        """Returns the integer severity weight for a recognized symptom, or None if not found."""
        return self._severities.get(symptom.strip().replace('_', ' ').lower())

# Singleton instance
medical_info_service = MedicalInfoService()
