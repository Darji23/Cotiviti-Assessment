import os
import pandas as pd
from src.utils.config import RAW_DATA_PATH
from src.utils.logger import setup_logger

logger = setup_logger("data-loader")

def load_raw_data(limit_rows: int = 50000) -> pd.DataFrame:
    """Loads the raw vital signs dataset from disk and performs basic schema checks."""
    if not os.path.exists(RAW_DATA_PATH):
        err_msg = f"Raw data file not found at {RAW_DATA_PATH}. Please run cp/download script."
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)
        
    logger.info(f"Ingesting raw dataset from {RAW_DATA_PATH}...")
    
    df = pd.read_csv(RAW_DATA_PATH, nrows=limit_rows)
    logger.info(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns successfully.")
    
    # Schema check for new patient-vital-signs-and-event-tracking dataset
    required_cols = [
        "hadm_id", "HR", "RR", "SBP", "TEMP", "SPO2", "charttime", "age", "sex"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        err_msg = f"Invalid CSV Schema. Missing columns: {missing}"
        logger.error(err_msg)
        raise ValueError(err_msg)
        
    return df
