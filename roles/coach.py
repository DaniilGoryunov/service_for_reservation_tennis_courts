import streamlit as st
import psycopg2
from services.in_table import *
from services.reserv import *

def coach_page(user_id):
    st.subheader("Ваши записи как тренера")
    reservations = get_coach_reservations(user_id)  # Получаем записи, где пользователь тренер
    display_reservations(reservations, role="coach")

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
    
def get_coach_reservations(coach_id):
    query = """
        SELECT r.reservation_id, r.reservation_time, r.duration, c.surface, u.username
        FROM reservations r
        JOIN courts c ON r.court_id = c.court_id
        JOIN users u ON r.user_id = u.user_id
        WHERE r.coach_id = %s
        ORDER BY r.reservation_time DESC;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (coach_id,))
                return cur.fetchall()
    except Exception as e:
        st.error(f"Ошибка при получении записей тренера: {e}")
        return []