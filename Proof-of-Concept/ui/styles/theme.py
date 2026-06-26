# Styling and theme constants for Streamlit

THEME_COLORS = {
    "bg_dark": "#0f111a",
    "card_bg": "#161925",
    "primary": "#8b5cf6",
    "primary_glow": "rgba(139, 92, 246, 0.25)",
    "emerald": "#10b981",
    "emerald_glow": "rgba(16, 185, 129, 0.15)",
    "crimson": "#ef4444",
    "crimson_glow": "rgba(239, 68, 68, 0.15)",
    "amber": "#f59e0b",
    "amber_glow": "rgba(245, 158, 11, 0.15)",
    "text_main": "#f3f4f6",
    "text_muted": "#9ca3af"
}

def get_severity_badge_html(severity: str) -> str:
    """Returns a styled HTML badge based on severity levels."""
    if severity == "Critical":
        color = THEME_COLORS["crimson"]
        bg = THEME_COLORS["crimson_glow"]
        border = "rgba(239, 68, 68, 0.4)"
    elif severity == "Medium":
        color = THEME_COLORS["amber"]
        bg = THEME_COLORS["amber_glow"]
        border = "rgba(245, 158, 11, 0.4)"
    else:
        color = THEME_COLORS["emerald"]
        bg = THEME_COLORS["emerald_glow"]
        border = "rgba(16, 185, 129, 0.4)"
        
    return f"""
    <div style="
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 8px;
        background-color: {bg};
        color: {color};
        border: 1px solid {border};
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-align: center;
    ">
        {severity.upper()} RISK LEVEL
    </div>
    """

def get_verdict_badge_html(verdict: str) -> str:
    """Returns a styled HTML badge based on audit decisions."""
    if verdict == "APPROVED":
        color = THEME_COLORS["emerald"]
        bg = THEME_COLORS["emerald_glow"]
        border = "rgba(16, 185, 129, 0.4)"
    elif verdict == "AUDIT_DENIAL":
        color = THEME_COLORS["crimson"]
        bg = THEME_COLORS["crimson_glow"]
        border = "rgba(239, 68, 68, 0.4)"
    else: # PROVIDER_REVIEW
        color = THEME_COLORS["amber"]
        bg = THEME_COLORS["amber_glow"]
        border = "rgba(245, 158, 11, 0.4)"
        
    return f"""
    <div style="
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 10px;
        background-color: {bg};
        color: {color};
        border: 1px solid {border};
        font-weight: 800;
        font-size: 1rem;
        letter-spacing: 0.5px;
        text-align: center;
        box-shadow: 0 0 15px {bg};
    ">
        VERDICT: {verdict.replace('_', ' ').upper()}
    </div>
    """

CUSTOM_CSS = """
<style>
    /* Dark Theme tweaks for Streamlit elements */
    .stApp {
        background-color: #0c0e17;
        color: #f3f4f6;
    }
    
    /* Card design mimic */
    .metric-card {
        background-color: #161925;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Agent Terminal simulation */
    .agent-terminal {
        background-color: #0b0c10;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.25rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #a7f3d0;
        margin-top: 1rem;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.8);
        height: 250px;
        overflow-y: auto;
    }
    
    .terminal-step {
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    
    .terminal-title {
        color: #8b5cf6;
        font-weight: 600;
    }
</style>
"""
