import streamlit as st
import psycopg2
from services.reserv import *
from services.in_table import *

def get_all_reservations():
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
                return cur.fetchall()
    except Exception as e:
        st.error(f"Ошибка при получении всех записей: {e}")
        return []
    
# Страница для администратора
def admin_page():
    st.subheader("Все записи на корты")
    reservations = get_all_reservations()

    # Фильтрация записей
    reservations = filter_reservations(reservations)

    # Управление пользователями
    manage_users()

    # Отображение записей
    display_reservations(reservations, role="admin")

# Функция управления пользователями
def manage_users():
    st.subheader("Управление пользователями")
    user_to_change = st.text_input("Введите имя пользователя для изменения роли")
    new_role = st.selectbox("Выберите новую роль", ["user", "coach"], key="role_select")

    salary_8_12 = st.number_input("Зарплата (08:00-12:00)", min_value=0.0, value=1000.0, step=100.0)
    salary_12_18 = st.number_input("Зарплата (12:00-18:00)", min_value=0.0, value=1200.0, step=100.0)
    salary_18_22 = st.number_input("Зарплата (18:00-22:00)", min_value=0.0, value=1400.0, step=100.0)

    if st.button("Изменить роль пользователя"):
        if new_role == "coach":
            coach_added = add_user_as_coach(user_to_change, salary_8_12, salary_12_18, salary_18_22)
            if coach_added:
                st.success(f"Пользователь {user_to_change} успешно назначен тренером.")
            else:
                st.error(f"Не удалось изменить роль пользователя {user_to_change}.")

# Функция для добавления пользователя как тренера
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