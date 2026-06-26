import pytest
import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.schemas.patient import ClinicalSummary
from src.schemas.recommendation import AnomalyReport
from src.agents.reasoner import generate_offline_tpo_recommendation

def test_reasoner_low_risk():
    summary = ClinicalSummary(
        patient_id=1,
        demographics="Patient is a 45-year-old male.",
        vitals_baseline="HR: 70 bpm, SpO2: 98%",
        cardiovascular_assessment="Normal",
        pulmonary_assessment="Normal",
        metabolic_assessment="Normal"
    )
    
    anomaly = AnomalyReport(
        is_anomaly=False,
        risk_score=10.0,
        severity="Low",
        active_flags=[],
        clinical_rationale="All parameters within limits."
    )
    
    recommendation = generate_offline_tpo_recommendation(summary, anomaly)
    
    assert recommendation.audit_verdict == "APPROVED"
    assert "adjudication" in recommendation.payment_integrity_recommendation.lower()

def test_reasoner_critical_risk():
    summary = ClinicalSummary(
        patient_id=2,
        demographics="Patient is a 60-year-old female.",
        vitals_baseline="HR: 130 bpm (Tachycardia), SpO2: 88% (Critical Hypoxia)",
        cardiovascular_assessment="Tachycardic",
        pulmonary_assessment="Hypoxic",
        metabolic_assessment="Normal"
    )
    
    anomaly = AnomalyReport(
        is_anomaly=True,
        risk_score=95.0,
        severity="Critical",
        active_flags=["Critical Spo2", "Critical Heart Rate"],
        clinical_rationale="Vitals are severely out of range."
    )
    
    recommendation = generate_offline_tpo_recommendation(summary, anomaly)
    
    assert recommendation.audit_verdict == "PROVIDER_REVIEW"
    assert "hemodynamic stabilization" in recommendation.treatment_recommendation.lower()
