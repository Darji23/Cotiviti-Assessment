import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "vital_signs.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "vital_signs_clean.csv"

# Load environment
load_dotenv(ROOT_DIR / ".env")

# API Keys
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/gpt-oss-20b")

# Constants
VITAL_COLUMNS = [
    "Heart Rate", 
    "Respiratory Rate", 
    "Body Temperature", 
    "Oxygen Saturation", 
    "Systolic Blood Pressure", 
    "Diastolic Blood Pressure"
]
