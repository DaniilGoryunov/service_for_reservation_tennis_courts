import streamlit as st
from datetime import datetime
import os
from services.reserv import get_available_coaches, get_available_courts, reserve_user_court
# Функция для отображения страницы с резервированием
def show_reservation_page():
    # Инициализация значений в session_state, если они еще не установлены
    if 'reservation_date' not in st.session_state:
        st.session_state.reservation_date = datetime.today().date()  # Текущая дата по умолчанию

    if 'reservation_time' not in st.session_state:
        st.session_state.reservation_time = datetime.today().time()  # Текущее время по умолчанию

    if 'duration_minutes' not in st.session_state:
        st.session_state.duration_minutes = 60  # 60 минут по умолчанию

    # Создаем поля для ввода данных
    st.date_input("Выберите дату", key="reservation_date")
    st.time_input("Выберите время", key="reservation_time")
    st.number_input("Продолжительность в минутах", min_value=30, key="duration_minutes")

    # Выбор тренера (необязательный)
    reservation_datetime = datetime.combine(st.session_state.reservation_date, st.session_state.reservation_time)
    available_coaches = get_available_coaches(reservation_datetime)
    coach_options = [f"{coach[1]}" for coach in available_coaches]
    st.selectbox("Выберите тренера (необязательно)", ["Не выбрать"] + coach_options, key="coach_select")

    # Проверяем наличие доступных кортов
    available_courts = get_available_courts(reservation_datetime, st.session_state.duration_minutes)
    if available_courts:
        st.write("Доступные корты:")
        for court in available_courts:
            court_id, surface, price = court
            st.write(f"Корт №{court_id}: {surface}, Цена: {price * st.session_state.duration_minutes / 60} руб.")
            
            # Кнопка для резервирования корта
            if st.button(f"Зарезервировать {court_id}", key=f"reserve_{court_id}"):
                coach_id = None
                if st.session_state.coach_select != "Не выбрать":
                    coach_id = available_coaches[coach_options.index(st.session_state.coach_select)][0]
                reserve_user_court(st.session_state.user_id, court_id, reservation_datetime, st.session_state.duration_minutes, coach_id)
    else:
        st.write("Нет доступных кортов для выбранного времени.")

