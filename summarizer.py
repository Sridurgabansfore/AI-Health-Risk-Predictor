import re

def summarize_text(text):
    # Improved mock summarizer that looks for medical keywords
    keywords = ["pain", "fever", "glucose", "insulin", "headache", "tired", "thirsty", "weight"]
    found = [word for word in keywords if word in text.lower()]
    
    if found:
        return f"The AI detected potential symptoms/metrics: {', '.join(found)}. Please ensure these are accurately entered in the form below."
    
    words = text.split()
    if len(words) > 10:
        return "Analysis: " + " ".join(words[:10]) + "... (Consider mentioning specific symptoms like glucose level or thirst)."
    return f"Analysis: {text}"

def generate_health_report(input_data, result):
    risk_level = "High" if result == 1 else "Low"
    report = f"Patient Health Summary: The AI analysis indicates a {risk_level} risk of diabetes. "
    report += f"Main factors analyzed include Glucose ({input_data[1]}), BMI ({input_data[5]}), and Age ({input_data[7]}). "
    
    if result == 1:
        report += "Urgent: We recommend scheduling a follow-up with a specialist to discuss these results."
    else:
        report += "Status: Metrics are within a manageable range. Continue regular monitoring and a healthy diet."
    return report

def extract_metrics(text):
    # Map spoken words to form fields
    mapping = {
        "glucose": "glucose",
        "sugar": "glucose",
        "blood pressure": "bp",
        "bp": "bp",
        "weight": "bmi",
        "bmi": "bmi",
        "age": "age",
        "insulin": "insulin",
        "pregnancies": "preg",
        "pregnancy": "preg",
        "skin": "skin",
        "thickness": "skin"
    }
    
    extracted = {}
    for key, field in mapping.items():
        # Look for the keyword followed by a number
        match = re.search(rf"{key}\D*(\d+\.?\d*)", text.lower())
        if match:
            extracted[field] = float(match.group(1))
    return extracted

def chatbot_response(query):
    query = query.lower()
    responses = {
        "diabetes": "Diabetes is a chronic disease that occurs when the pancreas does not produce enough insulin or when the body cannot effectively use the insulin it produces.",
        "glucose": "Glucose is the main type of sugar in the blood and is the primary source of energy for the body's cells. High glucose is a key indicator of diabetes.",
        "bmi": "Body Mass Index (BMI) is a measure of body fat based on height and weight. For adults, a BMI of 18.5 to 24.9 is generally considered healthy.",
        "prevention": "To help prevent type 2 diabetes, maintain a healthy weight, be physically active, and eat a healthy diet low in sugar and saturated fats.",
        "accuracy": "Our ML model uses a Logistic Regression algorithm trained on the PIMA Diabetes dataset. While accurate for demo purposes, it should not replace professional medical advice.",
        "help": "You can ask me about diabetes, glucose, BMI, prevention, or the accuracy of our model!"
    }
    
    for key in responses:
        if key in query:
            return responses[key]
            
    return "I'm a medical assistant specialized in diabetes risk. You can ask me about glucose, BMI, or diabetes prevention!"
