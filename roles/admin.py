import streamlit as st
import psycopg2
from services.reserv import *
from services.in_table import *
from roles import *
from services import *
    
# Страница для администратора
def admin_page():
    st.subheader("Все записи на корты")
    reservations = get_all_reservations()

    # Фильтрация записей
    reservations = filter_reservations(reservations)

    # Отображение записей
    display_reservations(reservations, role="admin")