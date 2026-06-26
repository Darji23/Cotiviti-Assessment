import os
import streamlit as st
import pandas as pd

# Fix path to include workspace root for relative imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.utils.config import RAW_DATA_PATH, PROCESSED_DATA_PATH
from src.data.loader import load_raw_data
from src.data.preprocessor import preprocess_vital_signs
from src.schemas.patient import PatientVitals
from src.analytics.anomaly_detector import detect_anomalies_for_row
from src.analytics.risk_scorer import generate_anomaly_report
from src.agents.extractor import extract_clinical_summary
from src.agents.reasoner import analyze_and_recommend

# Import UI panels
from ui.styles.theme import CUSTOM_CSS
from ui.components.patient_selector import render_patient_selector
from ui.components.vitals_chart import render_vitals_chart
from ui.components.anomaly_panel import render_anomaly_panel
from ui.components.reasoning_panel import render_reasoning_panel

# Set page configuration
st.set_page_config(
    page_title="CareVerify AI - Cotiviti Claims Intelligence",
    page_icon="🩺",
    layout="wide"
)

# Render Custom Styling CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Data Loader Cache wrapper
@st.cache_data
def get_dataset() -> pd.DataFrame:
    """Checks raw data existence, runs preprocessors, and loads the clean dataset."""
    if not os.path.exists(RAW_DATA_PATH):
        st.error(f"Raw data file not found at {RAW_DATA_PATH}. Ingestion failed.")
        st.stop()
        
    if not os.path.exists(PROCESSED_DATA_PATH):
        with st.spinner("Executing initial preprocessor pipeline on Kaggle CSV..."):
            df_raw = load_raw_data(limit_rows=20000) # Load 20k rows for dashboard performance
            df_clean = preprocess_vital_signs(df_raw)
    else:
        df_clean = pd.read_csv(PROCESSED_DATA_PATH)
        
    return df_clean

# --- MAIN APP LOGIC ---

def main():
    # Header logo and titles
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 2rem;">
        <span style="font-size: 2.2rem; color: #8b5cf6;">🩺</span>
        <div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800;">CareVerify AI</h1>
            <p style="margin: 0; color: #9ca3af; font-size: 0.95rem;">Cotiviti Clinical Decision Support &amp; Payment Integrity POC</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ingest data
    df = get_dataset()
    
    # Sidebar: patient selector dropdown + demographics
    patient_id, patient_history, current_record = render_patient_selector(df)
    
    # Chart Area (History timeline)
    render_vitals_chart(patient_history)
    
    st.markdown("---")
    
    # Compute Anomalies & Run Agent Chain
    vitals_dict = current_record.to_dict()
    if 'timestamp' in vitals_dict and not isinstance(vitals_dict['timestamp'], str):
        vitals_dict['timestamp'] = str(vitals_dict['timestamp'])
    vitals_model = PatientVitals(**vitals_dict)
    
    # Execute Anomaly Detector
    history_prior = patient_history[patient_history["timestamp"] < current_record["timestamp"]]
    is_anomaly, active_flags, rationale = detect_anomalies_for_row(vitals_dict, history_prior)
    anomaly_report = generate_anomaly_report(is_anomaly, active_flags, rationale)
    
    # Tab Layout for panels
    tab_anoms, tab_agents = st.tabs([
        "🔍 Vitals & Physiological Alerts", 
        "🧠 Agent Reasoning & TPO Audits"
    ])
    
    # Run Agent Extraction & Recommendations
    # Cache results per patient ID and timestamp to avoid redundant Fireworks API calls during streamlit redraws
    cache_key = f"pat_{patient_id}_t_{current_record['timestamp']}"
    if "agent_cache" not in st.session_state:
        st.session_state["agent_cache"] = {}
        
    if cache_key not in st.session_state["agent_cache"]:
        with st.spinner("Invoking multi-agent validation pipeline..."):
            clinical_summary = extract_clinical_summary(vitals_model)
            tpo_rec = analyze_and_recommend(clinical_summary, anomaly_report)
            st.session_state["agent_cache"][cache_key] = (clinical_summary, tpo_rec)
            
    clinical_summary, tpo_rec = st.session_state["agent_cache"][cache_key]
    
    with tab_anoms:
        render_anomaly_panel(vitals_dict, anomaly_report)
        
    with tab_agents:
        render_reasoning_panel(clinical_summary, tpo_rec)

if __name__ == "__main__":
    main()
