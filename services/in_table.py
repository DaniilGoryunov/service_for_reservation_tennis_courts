import streamlit as st
import psycopg2
import datetime
from services.reserv import *

def add_user_as_coach(username, salary_8_12, salary_12_18, salary_18_22):
    query_get_user_id = "SELECT user_id FROM users WHERE username = %s;"
    query_update_role = "UPDATE users SET role = 'coach' WHERE username = %s;"
    query_insert_coach = "INSERT INTO coaches (coach_id, name) VALUES (%s, %s);"
    query_insert_prices = """
        INSERT INTO coach_prices (coach_id, start_time, end_time, price) VALUES
        (%s, '08:00:00', '12:00:00', %s),
        (%s, '12:00:00', '18:00:00', %s),
        (%s, '18:00:00', '22:00:00', %s);
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Получаем user_id пользователя
                cur.execute(query_get_user_id, (username,))
                user_id = cur.fetchone()
                if not user_id:
                    return False
                user_id = user_id[0]
                cur.execute(query_update_role, (username,))
                cur.execute(query_insert_coach, (user_id, username))
                cur.execute(query_insert_prices, (user_id, salary_8_12, user_id, salary_12_18, user_id, salary_18_22))
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
    filter_user = st.text_input("Фильтр по имени пользователя")
    filter_date = st.date_input("Фильтр по дате")

    if filter_user:
        reservations = [r for r in reservations if isinstance(r[4], str) and filter_user.lower() in r[4].lower()]
    if filter_date:
        reservations = [r for r in reservations if isinstance(r[1], datetime.datetime) and r[1].date() == filter_date]

    return reservations

# Отображение записей
def display_reservations(reservations, role):
    if reservations:
        if role == 'user': st.write("Ваши текущие записи:")
        elif role == 'coach': st.write("Все ваши ученики")
        else: st.write("Все записи")

        for reservation in reservations:
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
                if role == 'user':
                    st.write(f"Тренер: {coach_name}") 
                else:
                    st.write(f"Ученик: {coach_name}") 
            else:
                st.write("Без тренера")

            st.write(f"- **Дата и время:** {reservation_time_str}")
            st.write(f"  **Длительность:** {duration} минут")
            st.write(f"  **Покрытие корта:** {surface}")
            if username:
                st.write(f"  **Пользователь:** {username}")

            if st.button(f"Удалить запись №{reservation_id}", key=f"delete_{reservation_id}"):
                success = cancel_reservation(reservation_id)
                if success:
                    st.success(f"Запись №{reservation_id} успешно удалена.")
                else:
                    st.error(f"Не удалось удалить запись №{reservation_id}.")

            st.write("---")
    else:
        st.write("У вас пока нет записей на корты.")

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
    query_check_coach = "SELECT COUNT(*) FROM coaches WHERE coach_id = (SELECT user_id FROM users WHERE username = %s);"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check_coach, (username,))
            if cur.fetchone()[0] > 0:
                st.error(f"Пользователь {username} уже назначен тренером.")
                return True
    return False

def change_user_role_to_user(username):
    query_update_role = "UPDATE users SET role = 'user' WHERE username = %s;"
    query_delete_coach_prices = "DELETE FROM coach_prices WHERE coach_id = (SELECT user_id FROM users WHERE username = %s);"
    query_delete_coach = "DELETE FROM coaches WHERE coach_id = (SELECT user_id FROM users WHERE username = %s);"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query_update_role, (username,))
                cur.execute(query_delete_coach_prices, (username,))
                cur.execute(query_delete_coach, (username,))
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Ошибка при изменении роли пользователя {username}: {e}")
        return False