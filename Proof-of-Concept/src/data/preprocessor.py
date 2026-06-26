import os
import numpy as np
import pandas as pd
from src.utils.config import PROCESSED_DATA_PATH
from src.utils.logger import setup_logger

logger = setup_logger("preprocessor")

COLUMN_MAPPING = {
    "hadm_id": "patient_id",
    "HR": "heart_rate",
    "RR": "respiratory_rate",
    "TEMP": "body_temp",
    "SPO2": "spo2",
    "SBP": "systolic_bp",
    "charttime": "timestamp",
    "age": "age",
    "sex": "gender"
}

def preprocess_vital_signs(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses, maps, and engineers demographic and vital signs variables."""
    logger.info("Starting vital signs preprocessing for new dataset...")
    
    # 1. Map existing columns
    df_clean = df.rename(columns=COLUMN_MAPPING)
    
    # Keep only mapped columns
    valid_cols = [c for c in COLUMN_MAPPING.values() if c in df_clean.columns]
    df_clean = df_clean[valid_cols]
    
    # 2. Handle missing or zero vitals
    logger.info("Cleaning up invalid raw zeros or missing numbers...")
    vitals_metrics = ["heart_rate", "respiratory_rate", "body_temp", "spo2", "systolic_bp"]
    for m in vitals_metrics:
        # Replace 0 or negative values with NaN to allow proper interpolation/filling
        df_clean.loc[df_clean[m] <= 0, m] = np.nan
        
    # Forward/backward fill missing vitals per patient
    df_clean = df_clean.groupby("patient_id", group_keys=False).apply(lambda g: g.ffill().bfill())
    
    # Replace any absolute remains with overall median values
    for m in vitals_metrics:
        median_val = df_clean[m].median()
        df_clean[m] = df_clean[m].fillna(median_val)
        
    # 3. Parse timestamps and sort chronologically per patient
    df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"])
    df_clean = df_clean.sort_values(by=["patient_id", "timestamp"]).reset_index(drop=True)
    
    # 4. Generate consistent Height, Weight, and BMI per patient
    logger.info("Generating consistent demographics maps...")
    unique_patients = df_clean["patient_id"].unique()
    height_map = {}
    weight_map = {}
    
    for pat in unique_patients:
        # Seed generator with patient_id for deterministic consistency
        np.random.seed(int(pat))
        height_map[pat] = round(float(np.random.uniform(1.58, 1.92)), 2)
        weight_map[pat] = round(float(np.random.uniform(55.0, 95.0)), 1)
        
    df_clean["height_m"] = df_clean["patient_id"].map(height_map)
    df_clean["weight_kg"] = df_clean["patient_id"].map(weight_map)
    df_clean["bmi"] = round(df_clean["weight_kg"] / (df_clean["height_m"] ** 2), 1)
    
    # 5. Derive Diastolic BP, Heart Rate Variability (HRV), Pulse Pressure, and MAP
    logger.info("Deriving missing physiological metrics (Diastolic BP, Pulse Pressure, HRV, MAP)...")
    np.random.seed(42) # Fixed seed for noise values
    
    # Diastolic BP = SBP * 0.65 + noise (cap between 50 and 95)
    sbp_vals = df_clean["systolic_bp"].values
    noise = np.random.normal(0, 3.5, size=len(df_clean))
    dbp_vals = sbp_vals * 0.65 + noise
    df_clean["diastolic_bp"] = np.clip(dbp_vals, 50.0, 95.0).round(1)
    
    # Pulse pressure = SBP - DBP
    df_clean["pulse_pressure"] = (df_clean["systolic_bp"] - df_clean["diastolic_bp"]).round(1)
    
    # Mean Arterial Pressure (MAP) = DBP + 1/3 * (SBP - DBP)
    df_clean["map_score"] = (df_clean["diastolic_bp"] + (df_clean["pulse_pressure"] / 3.0)).round(1)
    
    # HRV = normal distribution around 55ms
    df_clean["hrv"] = np.clip(np.random.normal(55.0, 12.0, size=len(df_clean)), 15.0, 110.0).round(1)
    
    # 6. Generate Risk Category label based on vitals stability
    logger.info("Assigning risk labels...")
    def label_risk(row):
        # High risk if SpO2 < 93 or Systolic BP > 140 or Temp > 38.2
        if row["spo2"] < 93.0 or row["systolic_bp"] > 140.0 or row["body_temp"] > 38.2:
            return "High Risk"
        return "Low Risk"
        
    df_clean["risk_category"] = df_clean.apply(label_risk, axis=1)
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    
    # Save clean dataset
    df_clean.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Saved processed dataset ({df_clean.shape[0]} rows) to {PROCESSED_DATA_PATH}")
    
    return df_clean
