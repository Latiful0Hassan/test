# app.py
import streamlit as st
from calculator import add, sub, mul, div, mod

st.title("Simple Calculator")

# ইউজার থেকে ইনপুট নেওয়া
num1 = st.number_input("Enter first number")
num2 = st.number_input("Enter second number")

operation = st.selectbox("Select operation", ("Add", "Sub", "Mul", "Div", "Mod"))

if st.button("Calculate"):
    if operation == "Add":
        result = add(num1, num2)
    elif operation == "Sub":
        result = sub(num1, num2)
    elif operation == "Mul":
        result = mul(num1, num2)
    elif operation == "Div":
        result = div(num1, num2)
    elif operation == "Mod":
        result = mod(num1, num2)
    
    st.success(f"Result: {result}")
