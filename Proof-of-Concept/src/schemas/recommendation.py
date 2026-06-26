from pydantic import BaseModel, Field
from typing import List, Dict

class AnomalyReport(BaseModel):
    is_anomaly: bool = Field(..., description="Flag indicating if any vital sign is anomalous")
    risk_score: float = Field(..., description="Aggregate risk score from 0.0 (healthy) to 100.0 (immediate critical risk)")
    severity: str = Field(..., description="Risk category: Low, Medium, or Critical")
    active_flags: List[str] = Field(..., description="List of active clinical warnings (e.g., Tachycardia, Hypoxia, Fever)")
    clinical_rationale: str = Field(..., description="Detailed explanation of the analytical flags and statistical deviations")

class TPORecommendation(BaseModel):
    treatment_recommendation: str = Field(..., description="Prioritized recommendations for clinical care, monitoring, or interventions")
    payment_integrity_recommendation: str = Field(..., description="Recommendations for billing review, claims coding validation, or upcoding risks")
    operational_recommendation: str = Field(..., description="Operational triage recommendations (e.g., ICU transfer, nurse home visit, discharge)")
    chain_of_thought_steps: List[str] = Field(..., description="Step-by-step reasoning steps leading to this final audit and TPO recommendation")
    audit_verdict: str = Field(..., description="Audit status choice: APPROVED, AUDIT_DENIAL, or PROVIDER_REVIEW")
