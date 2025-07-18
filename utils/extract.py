import re

def extract_tests(text):
    pattern = r"(Iron|Ferritin|Transferrin Saturation|UIBC|TIBC|Total Iron Binding Capacity)[\s:]*([0-9.]+)[^\d]+([a-zA-Z%µ/]+)[^\d]+([0-9.]+)\s*-\s*([0-9.]+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    results = []
    for match in matches:
        test, value, unit, low, high = match
        value = float(value)
        low, high = float(low), float(high)
        status = "Normal"
        if value < low:
            status = "Low" if value > low * 0.8 else "Very Low"
        elif value > high:
            status = "High" if value < high * 1.2 else "Very High"

        explanation = f"{test} is {status.lower()} which may indicate a clinical condition."
        results.append({
            "test": test,
            "value": value,
            "unit": unit,
            "ref_range": f"{low} - {high}",
            "status": status,
            "explanation": explanation
        })
    return results
