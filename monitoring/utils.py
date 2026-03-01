def calculate_risk(score):
    if score >= 8:
        return "High"
    elif score >= 4:
        return "Medium"
    return "Low"