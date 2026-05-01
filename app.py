import streamlit as st
import pandas as pd
import csv
import re
from model import predict_risk

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Warm CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #1E293B;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFFBF5 0%, #F8FAFC 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #FF8000 0%, #FFB266 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #64748B;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FF8000 0%, #FFB266 100%);
        color: white !important;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 128, 0, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 128, 0, 0.3);
    }
    
    .stNumberInput, .stTextInput {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    
    .report-card {
        background-color: white;
        padding: 2rem;
        border-radius: 20px;
        border-left: 8px solid #FF8000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

try:
    from speech_to_text import get_voice_input
    from summarizer import summarize_text, generate_health_report, extract_metrics, chatbot_response
    voice_available = True
except (ModuleNotFoundError, ImportError):
    voice_available = False
    def get_voice_input(): return "Voice assistant module not available."
    def summarize_text(text): return "Summarizer module not available."
    def generate_health_report(input_data, result): return "Report generator not available."
    def extract_metrics(text): return {}
    def chatbot_response(query): return "Chatbot module not available."

def save_data(name, input_data, result):
    with open("history.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name] + input_data + [result])

# Initialize session state
if "messages" not in st.session_state: st.session_state.messages = []
if "age" not in st.session_state: st.session_state["age"] = 1
for field in ["preg", "glucose", "bp", "skin", "insulin", "bmi", "dpf"]:
    if field not in st.session_state: st.session_state[field] = 0.0 if field in ["bmi", "dpf"] else 0

# --- SIDEBAR CHATBOT ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=100)
    st.markdown("<h2 style='color:white;'>Medical AI</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #334155;'>", unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a medical question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        response = chatbot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

# --- MAIN APP UI ---
st.markdown("<h1 class='main-header'>🩺 AI Medical Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Predict diabetes risk and get AI-powered health insights in seconds.</p>", unsafe_allow_html=True)

patient_name = st.text_input("👤 Patient Name", "Guest")

col1, col2 = st.columns(2)

with col1:
    preg = st.number_input("Pregnancies", 0, 20, value=int(st.session_state["preg"]))
    bp = st.number_input("Blood Pressure (mmHg)", 0, 150, value=int(st.session_state["bp"]))
    insulin = st.number_input("Insulin (mu U/ml)", 0, 900, value=int(st.session_state["insulin"]))
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, value=float(st.session_state["dpf"]))

with col2:
    glucose = st.number_input("Glucose (mg/dL)", 0, 200, value=int(st.session_state["glucose"]))
    skin = st.number_input("Skin Thickness (mm)", 0, 100, value=int(st.session_state["skin"]))
    bmi = st.number_input("BMI (Weight/Height²)", 0.0, 50.0, value=float(st.session_state["bmi"]))
    age = st.number_input("Age (Years)", 1, 100, value=int(st.session_state["age"]))

st.markdown("<br>", unsafe_allow_html=True)

# Visual Impact
data = {"Feature": ["Glucose", "BP", "BMI"], "Values": [glucose, bp, bmi]}
df_chart = pd.DataFrame(data)
st.bar_chart(df_chart.set_index("Feature"), color="#FF8000")

st.markdown("<hr>", unsafe_allow_html=True)

# Voice Assistant Section
st.markdown("### 🎤 Voice Assistant")
if voice_available:
    if st.button("Start Listening"):
        with st.spinner("AI is listening..."):
            text = get_voice_input()
        if "Could not" not in text:
            summary = summarize_text(text)
            metrics = extract_metrics(text)
            for field, val in metrics.items(): st.session_state[field] = val
            if metrics:
                st.toast(f"Data Extracted: {', '.join(metrics.keys())} ✅")
                st.rerun()
            st.write("🗣️ Transcription:", text)
            st.info(f"🧾 Summary: {summary}")
        else:
            st.error(f"❌ {text}")
else:
    st.info("Voice assistant modules are not available.")

st.markdown("<hr>", unsafe_allow_html=True)

# Prediction Section
if st.button("✨ Predict Health Risk", use_container_width=True):
    input_data = [preg, glucose, bp, skin, insulin, bmi, dpf, age]
    result = predict_risk(input_data)

    st.markdown("<br>", unsafe_allow_html=True)
    if result == 1:
        st.error("### ⚠️ High Diabetes Risk Detected")
    else:
        st.success("### ✅ Low Diabetes Risk Detected")
    
    save_data(patient_name, input_data, result)

    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
    st.subheader("📋 AI Health Report Summary")
    with st.spinner("Analyzing..."):
        report = generate_health_report(input_data, result)
    st.write(report)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.subheader("💾 Past Patient History")
if st.checkbox("Show History Logs"):
    try:
        df_history = pd.read_csv("history.csv", names=["Name", "Preg", "Glucose", "BP", "Skin", "Insulin", "BMI", "DPF", "Age", "Result"])
        st.dataframe(df_history, use_container_width=True)
    except:
        st.info("No logs available.")