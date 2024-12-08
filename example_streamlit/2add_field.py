import streamlit as st

num1 = st.number_input("Enter first number")
num2 = st.number_input("Enter second number")
btn = st.button("Sum")

if btn:
    res = num1 + num2
    st.write(f"Sum of {num1} and {num2} is {res}")
