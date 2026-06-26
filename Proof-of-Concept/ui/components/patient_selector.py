import streamlit as st
import pandas as pd
from typing import Tuple

def render_patient_selector(df: pd.DataFrame) -> Tuple[int, pd.DataFrame, pd.Series]:
    """Renders the dropdown patient selector and returns selected patient details."""
    st.sidebar.markdown("### 🔍 Patient Investigation Selection")
    
    # Dropdown for unique patients
    unique_patients = sorted(df["patient_id"].unique())
    selected_id = st.sidebar.selectbox(
        "Select Patient ID:",
        options=unique_patients,
        index=0,
        help="Select a patient to pull their historical vital signs and run the clinical audit."
    )
    
    # Filter dataset for patient history
    patient_history = df[df["patient_id"] == selected_id].sort_values("timestamp")
    current_record = patient_history.iloc[-1] # Treat latest row as the current evaluation
    
    # Demographics Info Card
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Patient Information")
    
    gender_icon = "♀️" if str(current_record.get('gender')).lower() == 'female' else "♂️"
    
    demographics_html = f"""
    <div class="metric-card" style="margin-bottom: 1rem;">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
            Patient {selected_id} {gender_icon}
        </div>
        <div style="font-size: 0.85rem; color: #9ca3af; line-height: 1.6;">
            <b>Age:</b> {int(current_record.get('age', 0))} yrs<br>
            <b>Gender:</b> {current_record.get('gender', 'N/A')}<br>
            <b>Weight:</b> {current_record.get('weight_kg', 0.0):.1f} kg<br>
            <b>Height:</b> {current_record.get('height_m', 0.0):.2f} m<br>
            <b>BMI:</b> {current_record.get('bmi', 0.0):.1f} (kg/m²)<br>
            <b>Baseline Risk:</b> {current_record.get('risk_category', 'Low Risk')}
        </div>
    </div>
    """
    st.sidebar.markdown(demographics_html, unsafe_allow_html=True)
    
    return selected_id, patient_history, current_record
