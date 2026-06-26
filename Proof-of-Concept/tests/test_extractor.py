import pytest
import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.schemas.patient import PatientVitals
from src.agents.extractor import generate_offline_clinical_summary

def test_offline_extractor_normal():
    vitals = PatientVitals(
        patient_id=102,
        timestamp="2026-06-25 10:00:00",
        heart_rate=72.0,
        respiratory_rate=15.0,
        body_temp=36.8,
        spo2=98.0,
        systolic_bp=118.0,
        diastolic_bp=75.0,
        age=45,
        gender="Female",
        weight_kg=68.0,
        height_m=1.70,
        bmi=23.5,
        map_score=89.3
    )
    
    summary = generate_offline_clinical_summary(vitals)
    
    assert summary.patient_id == 102
    assert "45-year-old" in summary.demographics
    assert "72" in summary.vitals_baseline
    assert "normal heart rate" in summary.cardiovascular_assessment.lower()
    assert "adequate oxygenation" in summary.pulmonary_assessment.lower()
