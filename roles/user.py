import streamlit as st
from services.in_table import *
from services.reserv import *

# Страница для пользователя
def user_page(user_id):
    st.subheader("Ваши записи на корты")
    reservations = get_user_reservations(user_id)  # Получаем записи пользователя
    display_reservations(reservations, role="user")