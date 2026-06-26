import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from src.analytics.thresholds import evaluate_metric, CLINICAL_THRESHOLDS
from src.utils.logger import setup_logger

logger = setup_logger("anomaly-detector")

def compute_z_scores(current_vitals: Dict[str, float], patient_history: pd.DataFrame) -> Dict[str, float]:
    """Computes Z-scores for current vitals relative to patient historical means."""
    z_scores = {}
    metrics = ["heart_rate", "respiratory_rate", "body_temp", "spo2", "systolic_bp", "diastolic_bp"]
    
    for metric in metrics:
        if metric not in current_vitals or patient_history.empty:
            z_scores[metric] = 0.0
            continue
            
        history_vals = patient_history[metric].dropna()
        if len(history_vals) < 3: # Need at least 3 points for meaningful std
            z_scores[metric] = 0.0
            continue
            
        mean = history_vals.mean()
        std = history_vals.std()
        
        if std == 0:
            z_scores[metric] = 0.0
        else:
            z_scores[metric] = float((current_vitals[metric] - mean) / std)
            
    return z_scores

def detect_anomalies_for_row(
    current_vitals: Dict[str, Any], 
    patient_history: pd.DataFrame, 
    z_threshold: float = 2.5
) -> Tuple[bool, List[str], str]:
    """Combines rule-based checks and Z-scores to flag patient anomalies."""
    active_flags = []
    reasons = []
    
    # 1. Rule-Based Threshold Check
    metrics = ["heart_rate", "respiratory_rate", "body_temp", "spo2", "systolic_bp", "diastolic_bp"]
    for m in metrics:
        val = current_vitals.get(m)
        if val is None:
            continue
            
        status = evaluate_metric(m, val)
        if status == "CRITICAL":
            active_flags.append(f"Critical {m.replace('_', ' ').title()}")
            reasons.append(f"Metric {m.replace('_', ' ').title()} value {val} is in CRITICAL range.")
        elif status == "WARNING":
            active_flags.append(f"High/Low {m.replace('_', ' ').title()}")
            reasons.append(f"Metric {m.replace('_', ' ').title()} value {val} deviates from standard bounds.")

    # 2. Z-Score Statistical Check
    z_scores = compute_z_scores(current_vitals, patient_history)
    for m, z in z_scores.items():
        if abs(z) >= z_threshold:
            flag_name = f"Statistical {m.replace('_', ' ').title()} Outlier"
            if flag_name not in active_flags:
                active_flags.append(flag_name)
                reasons.append(f"{m.replace('_', ' ').title()} fluctuates significantly (Z-score: {z:.2f}).")
                
    is_anomalous = len(active_flags) > 0
    rationale = " ".join(reasons) if is_anomalous else "All vital signs fall within normal physiological and statistical tolerances."
    
    return is_anomalous, active_flags, rationale
