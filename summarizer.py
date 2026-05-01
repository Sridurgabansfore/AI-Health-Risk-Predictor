def summarize_text(text):
    # This is a very simple mock summarizer.
    # In a real app, you might use a library like 'transformers' or 'sumy'.
    words = text.split()
    if len(words) > 10:
        return " ".join(words[:10]) + "..."
    return text

def generate_health_report(input_data, result):
    risk_level = "High" if result == 1 else "Low"
    report = f"Patient Health Summary: The AI analysis indicates a {risk_level} risk of diabetes. "
    report += f"Main factors analyzed include Glucose ({input_data[1]}), BMI ({input_data[5]}), and Age ({input_data[7]}). "
    
    if result == 1:
        report += "Urgent: We recommend scheduling a follow-up with a specialist to discuss these results."
    else:
        report += "Status: Metrics are within a manageable range. Continue regular monitoring and a healthy diet."
    return report
