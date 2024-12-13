import streamlit as st
import datetime
import os
from services.reserv import *
from services.in_table import *
from roles.coach import *
from roles.user import *

def show_reservation_page():
    if 'reservation_date' not in st.session_state:
        st.session_state.reservation_date = datetime.datetime.now().date() 

    if 'reservation_time' not in st.session_state:
        st.session_state.reservation_time = datetime.datetime.now().time() 

    if 'duration_minutes' not in st.session_state:
        st.session_state.duration_minutes = 60

    st.date_input("Выберите дату", key="reservation_date")
    st.time_input("Выберите время", key="reservation_time")
    st.number_input("Продолжительность в минутах", min_value=60, key="duration_minutes")

    reservation_datetime = datetime.datetime.combine(st.session_state.reservation_date, st.session_state.reservation_time)

    available_coaches = get_available_coaches(reservation_datetime)
    role = get_user_role(st.session_state.get("user_id"))
    if available_coaches and role != "coach":
        coach_options = [f"{coach[1]}" for coach in available_coaches]
    else:
        coach_options = []

    st.selectbox("Выберите тренера (необязательно)", ["Не выбрать"] + coach_options, key="coach_select")

    available_courts = get_available_courts(reservation_datetime, st.session_state.duration_minutes)
    
    if available_courts:
        st.write("Доступные корты:")
        for court in available_courts:
            court_id, surface, price = court
            total_price = price * st.session_state.duration_minutes / 60 
            average_rating = fetch_ratings_for_court(court_id)  
            st.write(f"Корт №{court_id}: {surface}, Цена: {total_price} руб., Средняя оценка: {average_rating:.1f}")

            if st.button(f"Зарезервировать {court_id}", key=f"reserve_{court_id}"):
                coach_id = None
                if st.session_state.coach_select != "Не выбрать":
                    coach_id = available_coaches[coach_options.index(st.session_state.coach_select)][0]

                reserve_user_court(st.session_state.user_id, court_id, reservation_datetime, st.session_state.duration_minutes, coach_id)
                st.success(f"Корт №{court_id} зарезервирован успешно!")
    else:
        st.write("Нет доступных кортов для выбранного времени.")

if 'user_id' in st.session_state:
    if get_user_role(st.session_state.get("user_id")) != 'admin':
        show_reservation_page()
    else:
        st.error("Вы АДМИН. Пожалуйста, войдите в систему под user.")
else:
    st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
