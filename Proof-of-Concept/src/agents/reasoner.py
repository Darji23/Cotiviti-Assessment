import json
from typing import List
from src.agents.base_agent import get_fireworks_client
from src.schemas.patient import ClinicalSummary
from src.schemas.recommendation import AnomalyReport, TPORecommendation
from src.utils.config import FIREWORKS_MODEL
from src.utils.logger import setup_logger

logger = setup_logger("reasoner-agent")

TPO_RECOMMENDATION_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_tpo_recommendation",
        "description": "Submits a clinical recommendation containing Treatment, Payment, and Operational assessments.",
        "parameters": {
            "type": "object",
            "properties": {
                "treatment_recommendation": {"type": "string", "description": "Priority clinical recommendations for care or monitoring"},
                "payment_integrity_recommendation": {"type": "string", "description": "Payment integrity suggestions, billing verification, or coding check directives"},
                "operational_recommendation": {"type": "string", "description": "Operational triage recommendations, care levels, or nursing workflows"},
                "chain_of_thought_steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sequential steps of logical reasoning leading to the decisions"
                },
                "audit_verdict": {
                    "type": "string",
                    "enum": ["APPROVED", "AUDIT_DENIAL", "PROVIDER_REVIEW"],
                    "description": "Final audit status decision"
                }
            },
            "required": ["treatment_recommendation", "payment_integrity_recommendation", "operational_recommendation", "chain_of_thought_steps", "audit_verdict"]
        }
    }
}

def generate_offline_tpo_recommendation(summary: ClinicalSummary, anomaly: AnomalyReport) -> TPORecommendation:
    """Offline heuristic decision engine for TPO recommendations."""
    logger.info("Executing offline rule-based clinical reasoner...")
    
    flags_str = ", ".join(anomaly.active_flags) if anomaly.active_flags else "none"
    
    if anomaly.severity == "Critical":
        cot = [
            f"1. Review Active Physiological Anomalies: Found critical flags [{flags_str}].",
            "2. Assess Clinical Care Severity: Patient is experiencing acute cardiorespiratory or thermal distress.",
            "3. Evaluate Billing & Coding Integrity: Billed procedures must be audited for high-severity code inflating (e.g. Critical Care time units).",
            "4. Operational Action: Route immediately to provider suspension review and dispatch emergency protocols."
        ]
        treatment = (
            "EMERGENCY CLINICAL PROTOCOL INDUCED: Initiate immediate hemodynamic stabilization. "
            "Administer oxygen therapy, check cardiac rhythm via 12-lead ECG, and prepare for critical care intervention."
        )
        payment = (
            "AUDIT WARNING: Claim exhibits extreme physiological outlier parameters. Hold payment. "
            "Conduct full manual review of the complete medical record, billing files, and modifier accuracy."
        )
        op = (
            "OPERATIONAL TRIASE: Dispatch emergency response team or route patient to the nearest intensive care unit. "
            "Issue emergency notification alerts to attending medical director."
        )
        verdict = "PROVIDER_REVIEW"
        
    elif anomaly.severity == "Medium":
        cot = [
            f"1. Scan Active Physiological Warnings: Found moderate flags [{flags_str}].",
            "2. Clinical Analysis: Vitals indicate borderline physiological drift or statistical outliers.",
            "3. Billing Check: Claim is eligible for regular audit sample to verify documentation completeness.",
            "4. Operational Plan: Escalate to outpatient case management."
        ]
        treatment = (
            "RECOMMEND CLINICAL ACTION: Schedule outpatient follow-up within 48 hours. "
            "Instruct patient to self-monitor vitals daily and coordinate lab diagnostics."
        )
        payment = (
            "PAYMENT AUDIT DIRECTIVE: Flag for random pre-payment audit. Check for coding specificity "
            "compliance and ensure no unbundled procedural codes are present on the claim."
        )
        op = (
            "OPERATIONAL TRIAGE: Escalate case to primary care nurse manager for telephone follow-up. "
            "Initiate standard tele-health outreach protocol."
        )
        verdict = "PROVIDER_REVIEW"
        
    else: # Low Risk
        cot = [
            "1. Evaluate Baseline: Vitals are within normal limits and show standard statistical profiles.",
            "2. Clinical Verification: Patient is clinically stable. No intervention necessary.",
            "3. Payment Accuracy: Claim represents standard low-risk preventive or outpatient service.",
            "4. Operational Verification: Fast-track processing."
        ]
        treatment = "CLINICAL MONITORING: Maintain routine preventive care checks. No immediate intervention required."
        payment = "PAYMENT ADJUDICATION: Low risk billing pattern. Approve claim for automated fast-track reimbursement."
        op = "OPERATIONAL TRIASE: Route to automated file and archive. Maintain standard care scheduling."
        verdict = "APPROVED"
        
    return TPORecommendation(
        treatment_recommendation=treatment,
        payment_integrity_recommendation=payment,
        operational_recommendation=op,
        chain_of_thought_steps=cot,
        audit_verdict=verdict
    )

def analyze_and_recommend(summary: ClinicalSummary, anomaly: AnomalyReport) -> TPORecommendation:
    """Invokes Fireworks to execute Chain-of-Thought reasoning or falls back to heuristics."""
    client = get_fireworks_client()
    if not client:
        return generate_offline_tpo_recommendation(summary, anomaly)
        
    logger.info(f"Generating Agentic TPO Recommendation via Fireworks for Patient {summary.patient_id}...")
    
    prompt = (
        "You are an advanced clinical decision support and payment integrity agent for Cotiviti.\n"
        "Evaluate the following patient clinical status and anomaly warnings:\n\n"
        f"--- CLINICAL EXTRACTED SUMMARY ---\n"
        f"Patient ID: {summary.patient_id}\n"
        f"Demographics: {summary.demographics}\n"
        f"Vitals Overview: {summary.vitals_baseline}\n"
        f"Cardio Assessment: {summary.cardiovascular_assessment}\n"
        f"Pulm Assessment: {summary.pulmonary_assessment}\n"
        f"Metabolic Assessment: {summary.metabolic_assessment}\n\n"
        f"--- ANOMALY DETECTION ALERTS ---\n"
        f"Is Anomaly: {anomaly.is_anomaly}\n"
        f"Risk Score: {anomaly.risk_score}/100\n"
        f"Severity Level: {anomaly.severity}\n"
        f"Active Warning Flags: {', '.join(anomaly.active_flags)}\n"
        f"Clinical Rationale: {anomaly.clinical_rationale}\n\n"
        "Generate a structured clinical and billing assessment. Output using the submit_tpo_recommendation tool."
    )
    
    try:
        response = client.chat.completions.create(
            model=FIREWORKS_MODEL,
            messages=[
                {"role": "system", "content": "You are a clinical decision support and payment integrity system expert."},
                {"role": "user", "content": prompt}
            ],
            tools=[TPO_RECOMMENDATION_TOOL],
            tool_choice={"type": "function", "function": {"name": "submit_tpo_recommendation"}},
            max_tokens=1000
        )
        
        # Parse tool output
        tool_call = response.choices[0].message.tool_calls[0]
        tpo_dict = json.loads(tool_call.function.arguments)
        return TPORecommendation(**tpo_dict)
        
    except Exception as e:
        logger.error(f"Fireworks reasoning failed: {e}. Falling back to offline heuristics.")
        return generate_offline_tpo_recommendation(summary, anomaly)
