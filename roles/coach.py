import streamlit as st
import psycopg2
from services.in_table import *
from services.reserv import *
from services.redis_service import (
    get_cached_coach_reservations,
    cache_coach_reservations,
    invalidate_reservation_cache,
    redis_client,
    deserialize_from_json
)
import json

def show_coach_cache_debug(coach_id):
    """Показывает отладочную информацию о кэше резерваций тренера"""
    if st.checkbox("Показать отладочную информацию кэша тренера"):
        key = f"reservations:coach:{coach_id}"
        value = redis_client.get(key)
        ttl = redis_client.ttl(key)
        
        if value:
            try:
                reservations = deserialize_from_json(value)
                st.write(f"🔍 Кэш резерваций тренера (TTL: {ttl} сек.):")
                st.write(f"Количество резерваций в кэше: {len(reservations)}")
                for i, res in enumerate(reservations, 1):
                    st.code(f"Резервация #{i}:\n{json.dumps(res, indent=2, ensure_ascii=False, default=str)}")
            except Exception as e:
                st.error(f"Ошибка при разборе кэша: {str(e)}")
        else:
            st.info("В кэше нет данных о резервациях тренера")

def coach_page(user_id):
    coach_id = get_coach_id_by_user_id(user_id)
    if coach_id:
        reservations_coach = get_coach_reservations(coach_id)
        reservations_coach = filter_reservations(reservations_coach)
        display_reservations(reservations_coach, role="coach")
        # Показываем отладочную информацию о кэше
        show_coach_cache_debug(coach_id)
    
    reservations = get_user_reservations(user_id)
    display_reservations(reservations, role="user")


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
    # Сначала проверяем кэш
    cached_reservations = get_cached_coach_reservations(coach_id)
    if cached_reservations is not None:
        return cached_reservations

    query = """
        SELECT r.reservation_id, r.reservation_time, r.duration, c.surface, ch.name, u.username AS user_name
        FROM reservations r
        JOIN courts c ON r.court_id = c.court_id
        JOIN users u ON r.user_id = u.user_id
        JOIN coaches ch ON r.coach_id = ch.coach_id
        WHERE r.coach_id = %s
        ORDER BY r.reservation_time DESC;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (coach_id,))
                reservations = cur.fetchall()
                # Кэшируем результат
                cache_coach_reservations(coach_id, reservations)
                return reservations
    except Exception as e:
        st.error(f"Ошибка при получении записей тренера: {e}")
        return []
    
# Функция для добавления пользователя как тренера
def add_user_as_coach(username, salary_8_12, salary_12_18, salary_18_22):
    query_get_user_id = "SELECT user_id FROM users WHERE username = %s;"
    query_update_role = "UPDATE users SET role = 'coach' WHERE username = %s;"
    query_insert_coach = "INSERT INTO coaches (user_id, name) VALUES (%s, %s);"
    query_insert_prices = """
        INSERT INTO coach_prices (coach_id, start_time, end_time, price) VALUES
        (%s, '08:00:00', '12:00:00', %s),
        (%s, '12:00:00', '18:00:00', %s),
        (%s, '18:00:00', '22:00:00', %s);
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query_get_user_id, (username,))
                user_id = cur.fetchone()
                if not user_id:
                    return False
                user_id = user_id[0]
                coach_id = get_coach_id_by_user_id(user_id)
                cur.execute(query_update_role, (username))
                cur.execute(query_insert_coach, (user_id, username))
                cur.execute(query_insert_prices, (coach_id, salary_8_12, coach_id, salary_12_18, coach_id, salary_18_22))
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Ошибка при добавлении тренера: {e}")
        return False