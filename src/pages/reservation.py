import streamlit as st
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv("env.env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def show_reservation_page():
    if 'user' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему, чтобы продолжить.")
        return

    st.title("Резервирование теннисного корта")