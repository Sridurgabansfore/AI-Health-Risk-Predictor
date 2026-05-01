import streamlit as st
import pandas as pd
from model import predict_risk

st.title("🩺 AI Medical Assistant")
st.markdown("This app analyzes symptoms and predicts diabetes risk using AI.")

col1, col2 = st.columns(2)

with col1:
    preg = st.number_input("Pregnancies", 0, 20)
    bp = st.number_input("Blood Pressure", 0, 150)
    insulin = st.number_input("Insulin", 0, 900)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0)

with col2:
    glucose = st.number_input("Glucose", 0, 200)
    skin = st.number_input("Skin Thickness", 0, 100)
    bmi = st.number_input("BMI", 0.0, 50.0)
    age = st.number_input("Age", 1, 100)

data = {"Feature": ["Glucose", "BP", "BMI"],
        "Values": [glucose, bp, bmi]}

df_chart = pd.DataFrame(data)
st.bar_chart(df_chart.set_index("Feature"))

# Prediction
if st.button("Predict Risk"):
    input_data = [preg, glucose, bp, skin, insulin, bmi, dpf, age]
    result = predict_risk(input_data)

    if result == 1:
        st.error("⚠️ High Diabetes Risk")
    else:
        st.success("✅ Low Diabetes Risk")