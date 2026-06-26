from typing import List, Dict, Any
from src.schemas.recommendation import AnomalyReport
from src.utils.logger import setup_logger

logger = setup_logger("risk-scorer")

def generate_anomaly_report(
    is_anomaly: bool,
    active_flags: List[str],
    clinical_rationale: str
) -> AnomalyReport:
    """Calculates risk score and severity category to compile an AnomalyReport."""
    if not is_anomaly or not active_flags:
        return AnomalyReport(
            is_anomaly=False,
            risk_score=10.0,
            severity="Low",
            active_flags=[],
            clinical_rationale=clinical_rationale
        )
        
    # Calculate weighted risk score based on flag severity
    base_score = 20.0
    critical_count = 0
    warning_count = 0
    statistical_count = 0
    
    for flag in active_flags:
        if "Critical" in flag:
            base_score += 25.0
            critical_count += 1
        elif "High/Low" in flag:
            base_score += 12.0
            warning_count += 1
        elif "Statistical" in flag:
            base_score += 8.0
            statistical_count += 1
            
    # Cap score at 100
    risk_score = min(base_score, 100.0)
    
    # Classify severity
    if critical_count > 0 or risk_score >= 70.0:
        severity = "Critical"
    elif warning_count > 0 or statistical_count > 0 or risk_score >= 30.0:
        severity = "Medium"
    else:
        severity = "Low"
        
    logger.info(f"Generated AnomalyReport: Severity={severity}, RiskScore={risk_score:.1f}, ActiveFlags={len(active_flags)}")
    
    return AnomalyReport(
        is_anomaly=is_anomaly,
        risk_score=round(risk_score, 1),
        severity=severity,
        active_flags=active_flags,
        clinical_rationale=clinical_rationale
    )
