import json
from src.agents.base_agent import get_fireworks_client
from src.schemas.patient import PatientVitals, ClinicalSummary
from src.utils.config import FIREWORKS_MODEL
from src.utils.logger import setup_logger

logger = setup_logger("extractor-agent")

CLINICAL_SUMMARY_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_clinical_summary",
        "description": "Submits a structured clinical summary extraction for a patient.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "integer", "description": "Unique ID of the patient"},
                "demographics": {"type": "string", "description": "Summary of patient age, gender, and physical details (height, weight)"},
                "vitals_baseline": {"type": "string", "description": "Narrative baseline overview of the current vitals readings"},
                "cardiovascular_assessment": {"type": "string", "description": "Clinical evaluation of heart rate and blood pressure"},
                "pulmonary_assessment": {"type": "string", "description": "Clinical evaluation of respiratory rate and oxygen levels"},
                "metabolic_assessment": {"type": "string", "description": "Clinical evaluation of body temperature and BMI indicators"}
            },
            "required": ["patient_id", "demographics", "vitals_baseline", "cardiovascular_assessment", "pulmonary_assessment", "metabolic_assessment"]
        }
    }
}

def generate_offline_clinical_summary(vitals: PatientVitals) -> ClinicalSummary:
    """Heuristic clinical summary generator for offline execution."""
    logger.info("Executing offline heuristic extractor...")
    
    # 1. Demographics
    bmi_val = vitals.bmi if vitals.bmi else (vitals.weight_kg / (vitals.height_m ** 2) if vitals.height_m > 0 else 0)
    dem = f"Patient is a {vitals.age}-year-old {vitals.gender.lower()} weighing {vitals.weight_kg}kg, height {vitals.height_m}m. (BMI: {bmi_val:.1f})."
    
    # 2. Vitals Baseline
    vitals_base = (
        f"Telemetry shows HR: {vitals.heart_rate} bpm, SpO2: {vitals.spo2}%, "
        f"BP: {vitals.systolic_bp:.0f}/{vitals.diastolic_bp:.0f} mmHg, "
        f"RR: {vitals.respiratory_rate} breaths/min, Temp: {vitals.body_temp}°C."
    )
    
    # 3. Cardiovascular Assessment
    cv_flags = []
    if vitals.heart_rate > 100:
        cv_flags.append("tachycardia")
    elif vitals.heart_rate < 60:
        cv_flags.append("bradycardia")
    else:
        cv_flags.append("normal heart rate")
        
    if vitals.systolic_bp > 140 or vitals.diastolic_bp > 90:
        cv_flags.append("stage-2 hypertension")
    elif vitals.systolic_bp > 120 or vitals.diastolic_bp > 80:
        cv_flags.append("elevated blood pressure")
    else:
        cv_flags.append("normal blood pressure")
    cv_assessment = f"Cardiovascular status shows {', and '.join(cv_flags)}. Pulse pressure is {vitals.pulse_pressure or 0:.0f} mmHg."
    
    # 4. Pulmonary Assessment
    pulm_flags = []
    if vitals.spo2 < 90:
        pulm_flags.append("severe hypoxia")
    elif vitals.spo2 < 95:
        pulm_flags.append("mild hypoxia")
    else:
        pulm_flags.append("adequate oxygenation")
        
    if vitals.respiratory_rate > 20:
        pulm_flags.append("tachypnea")
    elif vitals.respiratory_rate < 12:
        pulm_flags.append("bradypnea")
    else:
        pulm_flags.append("normal breathing rate")
    pulm_assessment = f"Pulmonary assessment indicates {', and '.join(pulm_flags)}. SpO2 is currently registered at {vitals.spo2}%."
    
    # 5. Metabolic Assessment
    temp_flags = []
    if vitals.body_temp > 38.0:
        temp_flags.append("pyrexia (fever)")
    elif vitals.body_temp < 35.5:
        temp_flags.append("hypothermia")
    else:
        temp_flags.append("normothermia (normal temperature)")
    metabolic_assessment = f"Metabolic status exhibits {', and '.join(temp_flags)} with a calculated BMI of {bmi_val:.1f}."
    
    return ClinicalSummary(
        patient_id=vitals.patient_id,
        demographics=dem,
        vitals_baseline=vitals_base,
        cardiovascular_assessment=cv_assessment,
        pulmonary_assessment=pulm_assessment,
        metabolic_assessment=metabolic_assessment
    )

def extract_clinical_summary(vitals: PatientVitals) -> ClinicalSummary:
    """Invokes Fireworks to parse vitals or falls back to heuristics."""
    client = get_fireworks_client()
    if not client:
        return generate_offline_clinical_summary(vitals)
        
    logger.info(f"Extracting clinical summary for Patient {vitals.patient_id} via Fireworks...")
    
    prompt = (
        f"Extract a structured clinical summary for this patient vital sign telemetry data:\n"
        f"{vitals.model_dump_json(indent=2)}\n\n"
        "Call the submit_clinical_summary tool to return the parsed values."
    )
    
    try:
        response = client.chat.completions.create(
            model=FIREWORKS_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert clinical summarization agent."},
                {"role": "user", "content": prompt}
            ],
            tools=[CLINICAL_SUMMARY_TOOL],
            tool_choice={"type": "function", "function": {"name": "submit_clinical_summary"}},
            max_tokens=1000
        )
        
        # Parse tool output
        tool_call = response.choices[0].message.tool_calls[0]
        summary_dict = json.loads(tool_call.function.arguments)
        return ClinicalSummary(**summary_dict)
        
    except Exception as e:
        logger.error(f"Fireworks extraction failed: {e}. Falling back to offline heuristics.")
        return generate_offline_clinical_summary(vitals)
