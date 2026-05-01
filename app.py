try:
    from speech_to_text import get_voice_input
    from summarizer import summarize_text, generate_health_report, extract_metrics, chatbot_response
    voice_available = True
except (ModuleNotFoundError, ImportError):
    voice_available = False
    def get_voice_input():
        return "Voice assistant module not available."
    def summarize_text(text):
        return "Summarizer module not available."
    def generate_health_report(input_data, result):
        return "Report generator not available."
    def extract_metrics(text):
        return {}
    def chatbot_response(query):
        return "Chatbot module not available."

import streamlit as st
import pandas as pd
import csv
from model import predict_risk

def save_data(name, input_data, result):
    with open("history.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name] + input_data + [result])

# Initialize session state for form fields and chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "age" not in st.session_state:
    st.session_state["age"] = 1
for field in ["preg", "glucose", "bp", "skin", "insulin", "bmi", "dpf"]:
    if field not in st.session_state:
        st.session_state[field] = 0.0 if field in ["bmi", "dpf"] else 0

# Sidebar Chatbot
with st.sidebar:
    st.header("💬 Medical AI Chatbot")
    st.info("Ask me about diabetes, BMI, or health tips!")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a medical question..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and add assistant response
        response = chatbot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

st.title("🩺 AI Medical Assistant")
st.markdown("This app analyzes symptoms and predicts diabetes risk using AI.")

patient_name = st.text_input("👤 Patient Name", "Guest")

col1, col2 = st.columns(2)

with col1:
    preg = st.number_input("Pregnancies", 0, 20, value=int(st.session_state["preg"]))
    bp = st.number_input("Blood Pressure", 0, 150, value=int(st.session_state["bp"]))
    insulin = st.number_input("Insulin", 0, 900, value=int(st.session_state["insulin"]))
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, value=float(st.session_state["dpf"]))

with col2:
    glucose = st.number_input("Glucose", 0, 200, value=int(st.session_state["glucose"]))
    skin = st.number_input("Skin Thickness", 0, 100, value=int(st.session_state["skin"]))
    bmi = st.number_input("BMI", 0.0, 50.0, value=float(st.session_state["bmi"]))
    age = st.number_input("Age", 1, 100, value=int(st.session_state["age"]))

data = {"Feature": ["Glucose", "BP", "BMI"],
        "Values": [glucose, bp, bmi]}

df_chart = pd.DataFrame(data)
st.bar_chart(df_chart.set_index("Feature"))

st.subheader("🎤 Voice Assistant")

if voice_available:
    if st.button("Speak"):
        with st.spinner("Listening..."):
            text = get_voice_input()

        st.write("🗣️ You said:", text)

        if "Could not" not in text:
            with st.spinner("Generating summary..."):
                summary = summarize_text(text)
                metrics = extract_metrics(text)
                
                # Update session state with extracted metrics
                for field, val in metrics.items():
                    st.session_state[field] = val
                
                if metrics:
                    st.success(f"Extracted: {', '.join(metrics.keys())}")
                    st.rerun()

            st.write("🗣️ You said:", text)
            st.write("🧾 Summary:", summary)
else:
    st.info("Voice assistant modules are not available. Install or enable speech_to_text and summarizer modules to use this feature.")

# Prediction
if st.button("Predict Risk"):
    input_data = [preg, glucose, bp, skin, insulin, bmi, dpf, age]
    result = predict_risk(input_data)

    if result == 1:
        st.error("⚠️ High Diabetes Risk")
    else:
        st.success("✅ Low Diabetes Risk")
    
    save_data(patient_name, input_data, result)

    # Display AI Report Summary
    st.subheader("📋 AI Health Report Summary")
    with st.spinner("Analyzing data for summary..."):
        report = generate_health_report(input_data, result)
    st.info(report)

st.divider()
st.subheader("💾 Past Patient History")
if st.checkbox("Show History"):
    try:
        df_history = pd.read_csv("history.csv", names=["Name", "Preg", "Glucose", "BP", "Skin", "Insulin", "BMI", "DPF", "Age", "Result"])
        st.dataframe(df_history)
    except Exception as e:
        st.info("No history data available yet. Complete a prediction to start tracking!")