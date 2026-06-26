import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.analytics.anomaly_detector import detect_anomalies_for_row

def render_vitals_chart(patient_history: pd.DataFrame):
    """Plots interactive historical vitals for the patient using Plotly, highlighting outliers."""
    st.markdown("### 📈 Historical Vitals Timeline")
    
    # Selection of Metric
    metric_options = {
        "Heart Rate (BPM)": "heart_rate",
        "Oxygen Saturation (SpO2 %)": "spo2",
        "Body Temperature (°C)": "body_temp",
        "Respiratory Rate (Breaths/Min)": "respiratory_rate",
        "Blood Pressure (mmHg)": "bp" # Special double plot
    }
    
    selected_label = st.selectbox("Select Vital Sign to Graph:", options=list(metric_options.keys()))
    selected_metric = metric_options[selected_label]
    
    fig = go.Figure()
    
    # Prepare history with anomaly labels pre-calculated for each point
    history_anoms = []
    for idx, row in patient_history.iterrows():
        # Baseline history up to that point
        history_prior = patient_history[patient_history["timestamp"] < row["timestamp"]]
        vitals_dict = row.to_dict()
        is_anom, flags, _ = detect_anomalies_for_row(vitals_dict, history_prior)
        history_anoms.append((is_anom, flags))
        
    patient_history = patient_history.copy()
    patient_history["is_anomaly"] = [item[0] for item in history_anoms]
    patient_history["flags"] = [", ".join(item[1]) for item in history_anoms]
    
    # Color settings
    line_color = "#8b5cf6" # Purple
    anom_color = "#ef4444" # Red
    
    if selected_metric == "bp":
        # Draw Systolic
        fig.add_trace(go.Scatter(
            x=patient_history["timestamp"],
            y=patient_history["systolic_bp"],
            mode='lines+markers',
            name='Systolic BP',
            line=dict(color='#8b5cf6', width=2),
            marker=dict(size=4)
        ))
        # Draw Diastolic
        fig.add_trace(go.Scatter(
            x=patient_history["timestamp"],
            y=patient_history["diastolic_bp"],
            mode='lines+markers',
            name='Diastolic BP',
            line=dict(color='#ec4899', width=2), # Pink
            marker=dict(size=4)
        ))
        
        # Highlight BP anomalies
        bp_anoms = patient_history[patient_history["is_anomaly"] & 
                                   (patient_history["flags"].str.contains("bp", case=False) | 
                                    patient_history["flags"].str.contains("systolic", case=False) | 
                                    patient_history["flags"].str.contains("diastolic", case=False))]
                                    
        if not bp_anoms.empty:
            fig.add_trace(go.Scatter(
                x=bp_anoms["timestamp"],
                y=bp_anoms["systolic_bp"],
                mode='markers',
                name='Systolic Outliers',
                marker=dict(color=anom_color, size=10, symbol='diamond', line=dict(color='#fff', width=1.5))
            ))
            fig.add_trace(go.Scatter(
                x=bp_anoms["timestamp"],
                y=bp_anoms["diastolic_bp"],
                mode='markers',
                name='Diastolic Outliers',
                marker=dict(color=anom_color, size=10, symbol='diamond', line=dict(color='#fff', width=1.5))
            ))
            
    else:
        # Draw standard metric line
        fig.add_trace(go.Scatter(
            x=patient_history["timestamp"],
            y=patient_history[selected_metric],
            mode='lines+markers',
            name=selected_label,
            line=dict(color=line_color, width=2.5),
            marker=dict(size=5)
        ))
        
        # Highlight anomalies for this metric
        metric_anoms = patient_history[patient_history["is_anomaly"] & 
                                       (patient_history["flags"].str.contains(selected_metric.replace('_', ' '), case=False) |
                                        patient_history["flags"].str.contains("spo2" if selected_metric == "spo2" else "---", case=False) |
                                        patient_history["flags"].str.contains("temp" if selected_metric == "body_temp" else "---", case=False))]
                                        
        if not metric_anoms.empty:
            fig.add_trace(go.Scatter(
                x=metric_anoms["timestamp"],
                y=metric_anoms[selected_metric],
                mode='markers',
                name='Outlier Alert',
                marker=dict(color=anom_color, size=11, symbol='diamond', line=dict(color='#fff', width=1.5))
            ))
            
    # Chart Styling
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#9ca3af', family='Outfit'),
            linecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#9ca3af', family='Outfit'),
            linecolor='rgba(255,255,255,0.1)'
        ),
        legend=dict(
            font=dict(color='#f3f4f6', family='Outfit'),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=320,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
