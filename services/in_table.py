import streamlit as st
import psycopg2
import datetime
from services.reserv import *

def fetch_ratings_for_court(court_id):
    query = "SELECT rating FROM user_reviews WHERE court_id = %s;"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (court_id,))
                ratings = cur.fetchall()
                if ratings:  # Проверяем, есть ли оценки
                    return sum(r[0] for r in ratings) / len(ratings)  # Извлекаем оценки из кортежей
                return 0  # Возвращаем 0, если нет оценок
    except Exception as e:
        st.error(f"Ошибка при получении оценок для корта {court_id}: {e}")
        return 0  # Возвращаем 0 в случае ошибки

def get_coach_id_by_user_id(user_id):
    query = "SELECT coach_id FROM coaches WHERE user_id = %s;"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                coach_id = cur.fetchone()
                return coach_id[0] if coach_id else None
    except Exception as e:
        st.error(f"Ошибка при получении coach_id: {e}")
        return None


def add_user_as_coach(username, salary_8_12, salary_12_18, salary_18_22):
    query_get_user_id = "SELECT user_id FROM users WHERE username = %s;"
    query_update_role = "UPDATE users SET role = 'coach' WHERE username = %s;"
    query_insert_coach = "INSERT INTO coaches (user_id, name) VALUES (%s, %s);"
    query_insert_prices = """
        INSERT INTO coach_prices (coach_id, start_time, end_time, price) VALUES
        (currval(pg_get_serial_sequence('coaches', 'coach_id')), '08:00:00', '12:00:00', %s),
        (currval(pg_get_serial_sequence('coaches', 'coach_id')), '12:00:00', '18:00:00', %s),
        (currval(pg_get_serial_sequence('coaches', 'coach_id')), '18:00:00', '22:00:00', %s);
    """
    query_delete_user_reservations = "DELETE FROM reservations WHERE user_id = %s;"

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Получаем user_id пользователя
                cur.execute(query_get_user_id, (username,))
                user_id = cur.fetchone()
                if not user_id:
                    return False
                user_id = user_id[0]
                cur.execute(query_delete_user_reservations, (user_id,))
                cur.execute(query_update_role, (username,))
                cur.execute(query_insert_coach, (user_id, username))
                cur.execute(query_insert_prices, (salary_8_12, salary_12_18, salary_18_22))
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Ошибка при добавлении тренера: {e}")
        return False
# Форматирование времени записи
def format_reservation_time(reservation_time):
    if isinstance(reservation_time, datetime.datetime):
        return reservation_time.strftime("%Y-%m-%d %H:%M")
    return str(reservation_time)

# Функция фильтрации записей
def filter_reservations(reservations):
    filter_date = st.date_input("Фильтр по дате")
    if filter_date:
        reservations = [r for r in reservations if isinstance(r[1], datetime.datetime) and r[1].date() == filter_date]

    return reservations

# Отображение записей
def display_reservations(reservations, role):
    future_reservations = [r for r in reservations if isinstance(r[1], datetime.datetime) and r[1] > datetime.datetime.now()]

    if future_reservations:
        if role == 'user': st.title("Ваши будущие записи:")
        elif role == 'coach': st.title("Все ваши будущие ученики")
        else: st.title("Все будущие записи")

        for reservation in future_reservations:
            if len(reservation) == 6:
                reservation_id, reservation_time, duration, surface, username, coach_name = reservation
            elif len(reservation) == 5:
                reservation_id, reservation_time, duration, surface, coach_name = reservation
                username = ""
            else:
                st.error("Ошибка в структуре данных записей.")
                continue

            reservation_time_str = format_reservation_time(reservation_time)

            if coach_name:
                if role == 'user' or role == 'admin':
                    st.write(f"Тренер: {coach_name}") 
                else:
                    st.write(f"Ученик: {coach_name}") 
            else:
                st.write("Без тренера")
            st.write(f" **Пользователь:** {username}")
            st.write(f" **Дата и время:** {reservation_time_str}")
            st.write(f"  **Длительность:** {duration} минут")
            st.write(f"  **Покрытие корта:** {surface}")

            if st.button(f"Удалить запись №{reservation_id}", key=f"delete_{reservation_id}"):
                success = cancel_reservation(reservation_id)
                if success:
                    st.success(f"Запись №{reservation_id} успешно удалена.")
                else:
                    st.error(f"Не удалось удалить запись №{reservation_id}.")

            st.write("---")
    else:
        st.write("У вас пока нет будущих записей на корты.")

def get_salary_inputs(new_role):
    if new_role == "coach":
        salary_8_12 = st.number_input("Зарплата (08:00-12:00)", min_value=0.0, value=1000.0, step=100.0)
        salary_12_18 = st.number_input("Зарплата (12:00-18:00)", min_value=0.0, value=1200.0, step=100.0)
        salary_18_22 = st.number_input("Зарплата (18:00-22:00)", min_value=0.0, value=1400.0, step=100.0)
    else:
        salary_8_12 = salary_12_18 = salary_18_22 = 0.0
    return salary_8_12, salary_12_18, salary_18_22

def check_user_exists(username):
    query_check_user = "SELECT COUNT(*) FROM users WHERE username = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check_user, (username,))
            if cur.fetchone()[0] == 0:
                st.error(f"Пользователь {username} не существует.")
                return False
    return True

def check_coach_exists(username):
    query_check_coach = "SELECT COUNT(*) FROM coaches WHERE user_id = (SELECT user_id FROM users WHERE username = %s);"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check_coach, (username,))
            if cur.fetchone()[0] > 0:
                st.error(f"Пользователь {username} уже назначен тренером.")
                return True
    return False

def change_coach_role_to_user(username):
    query_update_role = "UPDATE users SET role = 'user' WHERE username = %s;"
    query_delete_coach_prices = "DELETE FROM coach_prices WHERE coach_id = (SELECT coach_id FROM coaches WHERE name = %s);"
    query_delete_coach = "DELETE FROM coaches WHERE user_id = (SELECT user_id FROM users WHERE username = %s);"
    query_delete_reservations = "DELETE FROM reservations WHERE coach_id = (SELECT coach_id FROM coaches WHERE name = %s);"

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query_update_role, (username,))
                cur.execute(query_delete_coach_prices, (username,))
                cur.execute(query_delete_coach, (username,))
                cur.execute(query_delete_reservations, (username,))
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Ошибка при изменении роли пользователя {username}: {e}")
        return False