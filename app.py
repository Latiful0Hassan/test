# app.py
import streamlit as st

st.set_page_config(page_title="Simple Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Simple Calculator")

# ইউজার থেকে ইনপুট নেওয়া
num1 = st.number_input("Enter first number")
num2 = st.number_input("Enter second number")

# অপারেশন সিলেক্ট করা
operation = st.selectbox("Select operation", ("Add", "Subtract", "Multiply", "Divide"))

# ক্যালকুলেশন বাটন
if st.button("Calculate"):
    if operation == "Add":
        result = num1 + num2
    elif operation == "Subtract":
        result = num1 - num2
    elif operation == "Multiply":
        result = num1 * num2
    elif operation == "Divide":
        if num2 != 0:
            result = num1 / num2
        else:
            result = "Cannot divide by zero"
    
    st.success(f"Result: {result}")
