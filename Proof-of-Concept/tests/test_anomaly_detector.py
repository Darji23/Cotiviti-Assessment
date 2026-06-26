import pandas as pd
import pytest
import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analytics.thresholds import evaluate_metric
from src.analytics.anomaly_detector import detect_anomalies_for_row
from src.analytics.risk_scorer import generate_anomaly_report

def test_evaluate_metric_normal():
    # Heart rate 72 is normal
    assert evaluate_metric("heart_rate", 72.0) == "NORMAL"
    # SpO2 98% is normal
    assert evaluate_metric("spo2", 98.0) == "NORMAL"

def test_evaluate_metric_warning():
    # Heart rate 105 is high (warning)
    assert evaluate_metric("heart_rate", 105.0) == "WARNING"

def test_evaluate_metric_critical():
    # SpO2 88% is critical
    assert evaluate_metric("spo2", 88.0) == "CRITICAL"
    # Temp 39.0 is fever (critical)
    assert evaluate_metric("body_temp", 39.0) == "CRITICAL"

def test_detect_anomalies_no_history():
    current_vitals = {
        "heart_rate": 75.0,
        "respiratory_rate": 14.0,
        "body_temp": 36.6,
        "spo2": 98.0,
        "systolic_bp": 115.0,
        "diastolic_bp": 75.0
    }
    history = pd.DataFrame()
    
    is_anomaly, flags, rationale = detect_anomalies_for_row(current_vitals, history)
    assert is_anomaly is False
    assert len(flags) == 0
    
def test_detect_anomalies_critical_hypoxia():
    current_vitals = {
        "heart_rate": 75.0,
        "respiratory_rate": 14.0,
        "body_temp": 36.6,
        "spo2": 85.0, # Critical Hypoxia
        "systolic_bp": 115.0,
        "diastolic_bp": 75.0
    }
    history = pd.DataFrame()
    is_anomaly, flags, rationale = detect_anomalies_for_row(current_vitals, history)
    
    assert is_anomaly is True
    assert "Critical Spo2" in flags
    
    report = generate_anomaly_report(is_anomaly, flags, rationale)
    assert report.severity == "Critical"
    assert report.risk_score >= 45.0
