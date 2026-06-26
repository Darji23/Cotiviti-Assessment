from pydantic import BaseModel, Field
from typing import Optional

class PatientVitals(BaseModel):
    patient_id: int = Field(..., description="Unique ID of the patient")
    timestamp: str = Field(..., description="Timestamp of vitals reading")
    heart_rate: float = Field(..., description="Heart rate in beats per minute (BPM)")
    respiratory_rate: float = Field(..., description="Respiratory rate in breaths per minute")
    body_temp: float = Field(..., description="Body temperature in Celsius")
    spo2: float = Field(..., description="Oxygen saturation percentage (SpO2)")
    systolic_bp: float = Field(..., description="Systolic blood pressure (mmHg)")
    diastolic_bp: float = Field(..., description="Diastolic blood pressure (mmHg)")
    age: int = Field(..., description="Age of the patient")
    gender: str = Field(..., description="Gender of the patient")
    weight_kg: float = Field(..., description="Weight in kilograms")
    height_m: float = Field(..., description="Height in meters")
    hrv: Optional[float] = Field(None, description="Heart rate variability")
    pulse_pressure: Optional[float] = Field(None, description="Pulse pressure")
    bmi: Optional[float] = Field(None, description="Body Mass Index")
    map_score: Optional[float] = Field(None, description="Mean Arterial Pressure")

class ClinicalSummary(BaseModel):
    patient_id: int = Field(..., description="Unique ID of the patient")
    demographics: str = Field(..., description="Summary of patient age, gender, and physical details")
    vitals_baseline: str = Field(..., description="Narrative baseline overview of the current vitals readings")
    cardiovascular_assessment: str = Field(..., description="Clinical evaluation of heart rate and blood pressure")
    pulmonary_assessment: str = Field(..., description="Clinical evaluation of respiratory rate and oxygen levels")
    metabolic_assessment: str = Field(..., description="Clinical evaluation of body temperature and BMI indicators")
