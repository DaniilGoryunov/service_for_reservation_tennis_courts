import streamlit as st
import pandas as pd

st.title("CSV Viewer")
file = st.file_uploader("Upload your CSV file", type=["csv"])
df = None
if file is not None:
    df = pd.read_csv(file)
    st.write(df)


btn = st.button("Calculate sum quantity")

if btn and df is not None:
    st.write(df["quantity"].sum())
elif btn and df is None:
    st.write("Please upload a CSV file")
