import streamlit as st
from src.schemas.recommendation import AnomalyReport
from ui.styles.theme import get_severity_badge_html

def render_anomaly_panel(current_vitals: dict, report: AnomalyReport):
    """Renders the detailed anomaly checks and current vitals values."""
    st.markdown("### 🔍 Current Vitals & Anomaly Status")
    
    # 1. Row of Current Vitals Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Heart Rate", 
            value=f"{current_vitals['heart_rate']} bpm",
            delta="High" if current_vitals['heart_rate'] > 100 else ("Low" if current_vitals['heart_rate'] < 60 else None),
            delta_color="inverse"
        )
    with col2:
        st.metric(
            label="SpO2 (Oxygen)", 
            value=f"{current_vitals['spo2']}%",
            delta="Hypoxic" if current_vitals['spo2'] < 95 else None,
            delta_color="inverse"
        )
    with col3:
        st.metric(
            label="Blood Pressure", 
            value=f"{current_vitals['systolic_bp']:.0f}/{current_vitals['diastolic_bp']:.0f}",
            delta="Hypertensive" if current_vitals['systolic_bp'] > 130 else None,
            delta_color="inverse"
        )
    with col4:
        st.metric(
            label="Body Temp", 
            value=f"{current_vitals['body_temp']:.1f}°C",
            delta="Fever" if current_vitals['body_temp'] > 37.5 else None,
            delta_color="inverse"
        )
    with col5:
        st.metric(
            label="Resp Rate", 
            value=f"{current_vitals['respiratory_rate']} breaths/min",
            delta="Tachypnea" if current_vitals['respiratory_rate'] > 20 else None,
            delta_color="inverse"
        )
        
    st.markdown("---")
    
    # 2. Anomaly Report Visuals
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown("<span style='font-size: 0.95rem; color:#9ca3af; font-weight:600;'>RISK SEVERITY</span>", unsafe_allow_html=True)
        st.markdown(get_severity_badge_html(report.severity), unsafe_allow_html=True)
        
        st.markdown("<br><span style='font-size: 0.95rem; color:#9ca3af; font-weight:600;'>RISK SCORE</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size: 2.5rem; font-weight: 800; color: #8b5cf6;'>{report.risk_score}</span> <span style='color:#9ca3af;'>/ 100</span>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<span style='font-size: 0.95rem; color:#9ca3af; font-weight:600;'>ACTIVE PHYSIOLOGICAL ALERTS</span>", unsafe_allow_html=True)
        if report.active_flags:
            flags_html = " ".join([
                f"""<span style="
                    display: inline-block;
                    margin: 0.2rem;
                    padding: 0.25rem 0.65rem;
                    border-radius: 6px;
                    background-color: rgba(239, 68, 68, 0.1);
                    color: #ef4444;
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    font-size: 0.78rem;
                    font-weight: 600;
                ">{flag}</span>""" for flag in report.active_flags
            ])
            st.markdown(flags_html, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #10b981; font-weight:600; font-size:0.9rem;'><i class='fa-solid fa-circle-check'></i> No Active Physiological Warnings</div>", unsafe_allow_html=True)
            
        st.markdown("<br><span style='font-size: 0.95rem; color:#9ca3af; font-weight:600;'>ANALYTICAL RATIONALE</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 0.9rem; line-height:1.4; color: #f3f4f6;'>{report.clinical_rationale}</div>", unsafe_allow_html=True)
