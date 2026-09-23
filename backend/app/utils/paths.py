import os
from pathlib import Path

def get_project_root() -> Path:
    """Returns the absolute path to the project root directory."""
    # Assuming backend/app/utils/paths.py, project root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent.parent
