import streamlit as st
import pandas as pd
import csv
import re
from model import predict_risk

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="AI Health Dashboard",
    page_icon="🏥",
    layout="wide"
)

# Custom Dark Blue Dashboard CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #F8FAFC;
    }
    
    .stApp {
        background-color: #0F172A;
    }
    
    .header-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 0 0 30px 30px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    
    .card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        border: 1px solid #334155;
        color: #F8FAFC;
    }
    
    h1, h2, h3, h4, p, label {
        color: #F8FAFC !important;
    }
    
    .stButton>button {
        width: 100%;
        background: #3B82F6;
        color: white !important;
        border-radius: 10px;
        padding: 0.5rem;
        font-weight: 700;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background: #60A5FA;
        transform: scale(1.02);
    }
    
    .stNumberInput input, .stTextInput input {
        background-color: #0F172A !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #020617;
        color: white;
    }
    
    .stTable {
        background-color: #1E293B !important;
        color: white !important;
    }
    
    </style>
""", unsafe_allow_html=True)

try:
    from speech_to_text import get_voice_input
    from summarizer import summarize_text, generate_health_report, extract_metrics, chatbot_response
    voice_available = True
except (ModuleNotFoundError, ImportError):
    voice_available = False
    def get_voice_input(): return "Voice assistant unavailable."
    def summarize_text(text): return "Summarizer unavailable."
    def generate_health_report(input_data, result): return "Report unavailable."
    def extract_metrics(text): return {}
    def chatbot_response(query): return "Chatbot unavailable."

def save_data(name, input_data, result):
    with open("history.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name] + input_data + [result])

# Initialize session state
if "messages" not in st.session_state: st.session_state.messages = []
if "age" not in st.session_state: st.session_state["age"] = 1
for f in ["preg", "glucose", "bp", "skin", "insulin", "bmi", "dpf"]:
    if f not in st.session_state: st.session_state[f] = 0.0 if f in ["bmi", "dpf"] else 0

# Sidebar Chatbot
with st.sidebar:
    st.markdown("### 💬 Medical Assistant")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        res = chatbot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": res})
        with st.chat_message("assistant"): st.markdown(res)

# Header
st.markdown("""
    <div class='header-container' style='padding: 1rem; margin-bottom: 1rem;'>
        <h2 style='margin:0;'>🏥 AI Health Dashboard</h2>
    </div>
""", unsafe_allow_html=True)

# Main Grid
top_col1, top_col2 = st.columns([1.5, 1])

with top_col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("#### 👤 Patient Details")
    p_name = st.text_input("Name", "Guest", label_visibility="collapsed")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: preg = st.number_input("Preg", 0, 20, value=int(st.session_state["preg"]))
    with c2: glucose = st.number_input("Gluc", 0, 200, value=int(st.session_state["glucose"]))
    with c3: bp = st.number_input("BP", 0, 150, value=int(st.session_state["bp"]))
    with c4: skin = st.number_input("Skin", 0, 100, value=int(st.session_state["skin"]))
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: insulin = st.number_input("Ins", 0, 900, value=int(st.session_state["insulin"]))
    with c2: bmi = st.number_input("BMI", 0.0, 50.0, value=float(st.session_state["bmi"]))
    with c3: dpf = st.number_input("DPF", 0.0, 3.0, value=float(st.session_state["dpf"]))
    with c4: age = st.number_input("Age", 1, 100, value=int(st.session_state["age"]))
    
    if st.button("🚀 Analyze Patient Risk"):
        input_data = [preg, glucose, bp, skin, insulin, bmi, dpf, age]
        res = predict_risk(input_data)
        save_data(p_name, input_data, res)
        st.session_state['last_result'] = res
        st.session_state['last_input'] = input_data
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with top_col2:
    st.markdown("<div class='card' style='height: 100%;'>", unsafe_allow_html=True)
    st.markdown("#### 📊 Insights & Voice")
    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        if voice_available:
            if st.button("🎤 Listen"):
                with st.spinner("..."): text = get_voice_input()
                if "Could not" not in text:
                    m = extract_metrics(text)
                    for k, v in m.items(): st.session_state[k] = v
                    st.rerun()
    with v_col2: st.markdown("<p style='font-size:0.8rem; opacity:0.7;'>Click to speak symptoms</p>", unsafe_allow_html=True)
    
    st.bar_chart(pd.DataFrame({"Values": [glucose, bp, bmi]}, index=["Gluc", "BP", "BMI"]), color="#3B82F6", height=180)
    st.markdown("</div>", unsafe_allow_html=True)

# Results Row
if 'last_result' in st.session_state:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    res = st.session_state['last_result']
    inp = st.session_state['last_input']
    
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if res == 1: st.error("### ⚠️ HIGH RISK")
        else: st.success("### ✅ LOW RISK")
    with col_b:
        st.markdown("<p style='font-weight:600; margin-bottom:0;'>📋 AI Health Summary</p>", unsafe_allow_html=True)
        st.write(generate_health_report(inp, res))
    st.markdown("</div>", unsafe_allow_html=True)

# History
if st.checkbox("Show Logs"):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    try:
        df = pd.read_csv("history.csv", names=["Name", "Preg", "Gluc", "BP", "Skin", "Ins", "BMI", "DPF", "Age", "Res"])
        st.table(df.tail(3))
    except: st.info("No logs")
    st.markdown("</div>", unsafe_allow_html=True)
