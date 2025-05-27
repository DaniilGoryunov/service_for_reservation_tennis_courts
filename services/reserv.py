import streamlit as st
from datetime import timedelta
import psycopg2
from dotenv import load_dotenv
import os
from services.redis_service import (
    cache_user_reservations, get_cached_user_reservations,
    cache_coach_reservations, get_cached_coach_reservations,
    cache_all_reservations, get_cached_all_reservations,
    invalidate_reservation_cache
)

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
                reservation_id = cur.fetchone()[0]
                conn.commit()
                
                # Инвалидируем кэш после создания новой резервации
                invalidate_reservation_cache(user_id=user_id, coach_id=coach_id)
                
                return reservation_id
    except Exception as e:
        st.error(f"Ошибка при резервировании: {e}")
        return None
    
# Функция для отмены записи на корт
def cancel_reservation(reservation_id):
    # Сначала получаем информацию о резервации для инвалидации кэша
    query_get_info = """
        SELECT user_id, coach_id FROM reservations WHERE reservation_id = %s;
    """
    query_delete = """
        DELETE FROM reservations WHERE reservation_id = %s;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Получаем информацию о резервации
                cur.execute(query_get_info, (reservation_id,))
                result = cur.fetchone()
                if result:
                    user_id, coach_id = result
                    
                    # Удаляем резервацию
                    cur.execute(query_delete, (reservation_id,))
                    conn.commit()
                    
                    # Инвалидируем кэш
                    invalidate_reservation_cache(user_id=user_id, coach_id=coach_id)
                    return True
                return False
    except Exception as e:
        st.error(f"Ошибка при отмене записи: {e}")
        return False

# Функция для получения записей пользователя на корт
def get_user_reservations(user_id):
    # Сначала проверяем кэш
    cached_reservations = get_cached_user_reservations(user_id)
    if cached_reservations is not None:
        return cached_reservations

    query = """
        SELECT r.reservation_id, r.reservation_time, r.duration, c.surface, r.court_id, co.name AS coach_name
        FROM reservations r
        JOIN courts c ON r.court_id = c.court_id
        LEFT JOIN coaches co ON r.coach_id = co.coach_id
        WHERE r.user_id = %s
        ORDER BY r.reservation_time DESC;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                reservations = cur.fetchall()
                # Кэшируем результат
                cache_user_reservations(user_id, reservations)
                return reservations
    except Exception as e:
        st.error(f"Ошибка при получении записей: {e}")
        return []

def get_all_reservations():
    # Сначала проверяем кэш
    cached_reservations = get_cached_all_reservations()
    if cached_reservations is not None:
        return cached_reservations

    query = """ 
        SELECT r.reservation_id, r.reservation_time, r.duration, c.surface, u.username, co.name AS coach_name
        FROM reservations r
        JOIN courts c ON r.court_id = c.court_id
        JOIN users u ON r.user_id = u.user_id
        LEFT JOIN coaches co ON r.coach_id = co.coach_id
        ORDER BY r.reservation_time DESC;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                reservations = cur.fetchall()
                # Кэшируем результат
                cache_all_reservations(reservations)
                return reservations
    except Exception as e:
        st.error(f"Ошибка при получении всех записей: {e}")
        return []