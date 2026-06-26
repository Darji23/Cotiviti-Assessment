# Standard clinical thresholds for adults

CLINICAL_THRESHOLDS = {
    "heart_rate": {
        "normal_min": 60.0,
        "normal_max": 100.0,
        "critical_min": 50.0,
        "critical_max": 120.0
    },
    "respiratory_rate": {
        "normal_min": 12.0,
        "normal_max": 20.0,
        "critical_min": 8.0,
        "critical_max": 28.0
    },
    "body_temp": {
        "normal_min": 36.1,
        "normal_max": 37.2,
        "critical_min": 35.0,
        "critical_max": 38.5
    },
    "spo2": {
        "normal_min": 95.0,
        "normal_max": 100.0,
        "critical_min": 90.0
    },
    "systolic_bp": {
        "normal_min": 90.0,
        "normal_max": 120.0,
        "critical_min": 80.0,
        "critical_max": 160.0
    },
    "diastolic_bp": {
        "normal_min": 60.0,
        "normal_max": 80.0,
        "critical_min": 50.0,
        "critical_max": 100.0
    }
}

def evaluate_metric(name: str, value: float) -> str:
    """Evaluates a single metric and returns CRITICAL, WARNING, or NORMAL."""
    if name not in CLINICAL_THRESHOLDS:
        return "NORMAL"
        
    rules = CLINICAL_THRESHOLDS[name]
    
    # Check Critical
    if "critical_max" in rules and value >= rules["critical_max"]:
        return "CRITICAL"
    if "critical_min" in rules and value <= rules["critical_min"]:
        return "CRITICAL"
        
    # Check normal min/max
    if value > rules["normal_max"] or value < rules["normal_min"]:
        return "WARNING"
        
    return "NORMAL"
