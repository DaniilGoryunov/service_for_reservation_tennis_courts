import streamlit as st
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv("env.env")

# Конфигурация для подключения к базе данных
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Функция для получения доступных кортов
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
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (reservation_time.time(), reservation_time.time(), 
                                    (reservation_time + timedelta(minutes=duration)), reservation_time))
                return cur.fetchall()
    except Exception as e:
        st.error(f"Ошибка при выполнении запроса: {e}")
        return []

# Функция для резервирования корта
def reserve_user_court(user_id, court_id, reservation_time, duration, coach_id=None):
    query = """
        INSERT INTO reservations (user_id, court_id, reservation_time, duration, coach_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING reservation_id;
    """
    
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Проверка на существующие резервирования
                check_query = """
                    SELECT COUNT(*) FROM reservations
                    WHERE court_id = %s
                    AND reservation_time < %s + INTERVAL '1 minute' * %s
                    AND (reservation_time + INTERVAL '1 minute' * duration) > %s;
                """
                cur.execute(check_query, (court_id, reservation_time, duration, reservation_time))
                count = cur.fetchone()[0]

                if count > 0:
                    st.error("Корт уже зарезервирован на это время.")
                    return None

                cur.execute(query, (user_id, court_id, reservation_time, duration, coach_id))
                reservation_id = cur.fetchone()[0]  # Получаем ID резервирования
                conn.commit()
                st.success("Резервирование успешно выполнено!")
                return reservation_id  # Возвращаем ID резервирования
    except Exception as e:
        st.error(f"Ошибка при резервировании: {e}")
        return None

# Функция для получения доступных тренеров
def get_available_coaches(reservation_time):
    query = """
    SELECT c.coach_id, c.name 
    FROM coaches c
    WHERE NOT EXISTS (
        SELECT 1 FROM reservations r
        WHERE r.coach_id = c.coach_id
        AND r.reservation_time <= %s
        AND (r.reservation_time + INTERVAL '1 minute' * r.duration) > %s
    );
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (reservation_time, reservation_time))
                return cur.fetchall()
    except Exception as e:
        st.error(f"Ошибка при получении тренеров: {e}")
        return []
