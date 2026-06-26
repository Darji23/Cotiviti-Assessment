import streamlit as st
from src.schemas.patient import ClinicalSummary
from src.schemas.recommendation import TPORecommendation
from ui.styles.theme import get_verdict_badge_html

def render_reasoning_panel(summary: ClinicalSummary, recommendation: TPORecommendation):
    """Renders the extractor summary, the reasoning chain steps, and the final TPO recommendations."""
    st.markdown("### 🧠 Agentic Decision Support & Reasoning Chain")
    
    # 1. Extracted Clinical Summary
    with st.expander("👤 Clinical Extractor Summary (Agent 1)", expanded=True):
        st.markdown(f"**Demographics baseline:** {summary.demographics}")
        st.markdown(f"**Vitals baseline narrative:** *{summary.vitals_baseline}*")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Cardiovascular:**\n{summary.cardiovascular_assessment}")
        with c2:
            st.markdown(f"**Pulmonary:**\n{summary.pulmonary_assessment}")
        with c3:
            st.markdown(f"**Metabolic:**\n{summary.metabolic_assessment}")
            
    # 2. Reasoner Chain of Thought Terminal
    st.markdown("#### 💬 Agent 2 - Reasoner Chain of Thought Logs")
    
    steps_html = "".join([
        f"""<div class="terminal-step">
            &gt; <span class="terminal-title">{step.split(':')[0]}:</span> {":".join(step.split(':')[1:])}
        </div>""" if ":" in step else f'<div class="terminal-step">&gt; {step}</div>'
        for step in recommendation.chain_of_thought_steps
    ])
    
    terminal_box = f"""
    <div class="agent-terminal">
        <div style="display: flex; gap: 0.35rem; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #ef4444;"></span>
            <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #f59e0b;"></span>
            <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #10b981;"></span>
            <span style="margin-left: 0.5rem; font-size: 0.7rem; color: #6b7280; font-family: sans-serif;">FIREWORKS-TPO-REASONING-SESSION</span>
        </div>
        {steps_html}
        <div style="color: #10b981; font-weight:600; margin-top: 0.75rem;">&gt;&gt; [REASONING STAGE COMPLETE]</div>
    </div>
    """
    st.markdown(terminal_box, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. TPO Recommendations
    st.markdown("#### 📋 Strategic TPO Recommendations")
    
    col_verdict, col_rec = st.columns([1.1, 2])
    
    with col_verdict:
        st.markdown("<span style='font-size: 0.85rem; color:#9ca3af; font-weight:600;'>AUDITING VERDICT</span>", unsafe_allow_html=True)
        st.markdown(get_verdict_badge_html(recommendation.audit_verdict), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
    with col_rec:
        st.markdown(f"**🩺 Treatment (Clinical Care):**\n{recommendation.treatment_recommendation}")
        st.markdown(f"**💰 Payment Integrity (Billing & Coding Audit):**\n{recommendation.payment_integrity_recommendation}")
        st.markdown(f"**⚙️ Operations (Triage & Workflows):**\n{recommendation.operational_recommendation}")
