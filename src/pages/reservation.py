import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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

def get_available_courts(reservation_time, duration):
    query = """
        SELECT c.court_id, c.surface, cp.price
        FROM courts c
        JOIN court_prices cp ON c.court_id = cp.court_id
        WHERE cp.start_time <= %s::time AND cp.end_time > %s::time
        AND NOT EXISTS (
            SELECT 1 FROM reservations r
            WHERE r.court_id = c.court_id
            AND r.reservation_time < %s
            AND (r.reservation_time + INTERVAL '1 minute' * r.duration) > %s
        );
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (reservation_time.time(), reservation_time.time(), 
                                reservation_time + timedelta(minutes=duration), reservation_time))
            return cur.fetchall()

def reserve_court(user_id, court_id, reservation_time, duration):
    query = """
        INSERT INTO reservations (user_id, court_id, reservation_time, duration)
        VALUES (%s, %s, %s, %s);
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, court_id, reservation_time, duration))
                conn.commit()
                st.success("Резервирование успешно выполнено!")
    except Exception as e:
        st.error(f"Ошибка при резервировании: {e}")

def show_reservation_page():
    if 'user' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему, чтобы продолжить.")
        return

    st.title("Резервирование теннисного корта")

    # Выбор даты
    reservation_date = st.date_input("Выберите дату резервирования")
    
    # Выбор времени
    reservation_time = st.time_input("Выберите время резервирования")
    
    # Ввод количества часов
    duration_hours = st.number_input("Введите количество часов для резервирования", min_value=1, value=1, step=1)

    # Преобразование продолжительности в минуты для базы данных
    duration_minutes = int(duration_hours * 60)

    if st.button("Показать доступные корты"):
        reservation_datetime = datetime.combine(reservation_date, reservation_time)
        available_courts = get_available_courts(reservation_datetime, duration_minutes)
        if available_courts:
            for court in available_courts:
                court_id, surface, price = court  # Распаковка данных о корте
                st.write(f"Корт №{court_id}: {surface}, Цена: {price * duration_hours} руб.")
                if st.button(f"Зарезервировать {court_id}", key=f"reserve_{court_id}"):
                    st.write(f"Пользователь: {st.session_state.user_id}, Корт: {court_id}, Время: {reservation_datetime}, Продолжительность: {duration_minutes}")
                    reserve_court(st.session_state.user_id, court_id, reservation_datetime, duration_minutes)
        else:
            st.warning("Нет доступных кортов на это время.")