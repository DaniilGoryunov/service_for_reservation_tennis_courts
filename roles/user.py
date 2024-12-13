import streamlit as st
from services.in_table import *
from services.reserv import *

# Страница для пользователя
def user_page(user_id):
    reservations = get_user_reservations(user_id)  # Получаем записи пользователя
    display_reservations(reservations, role="user")

# Функция управления пользователями
def manage_users():
    st.subheader("Управление пользователями")
    user_to_change = st.text_input("Введите имя пользователя для изменения роли")
    
    if user_to_change:
        if not check_user_exists(user_to_change):
            return 

    new_role = st.selectbox("Выберите новую роль", ["user", "coach"], key="role_select")

    salary_8_12, salary_12_18, salary_18_22 = get_salary_inputs(new_role)

    if st.button("Изменить роль пользователя"):
        if new_role == "coach":
            if check_coach_exists(user_to_change):
                return

            coach_added = add_user_as_coach(user_to_change, salary_8_12, salary_12_18, salary_18_22)
            if coach_added:
                st.success(f"Пользователь {user_to_change} успешно назначен тренером.")
            else:
                st.error(f"Не удалось изменить роль пользователя {user_to_change}.")
        elif new_role == "user":
            if change_coach_role_to_user(user_to_change):
                st.success(f"Пользователь {user_to_change} успешно назначен пользователем.")
            else:
                st.error(f"Ошибка при изменении роли пользователя {user_to_change}.")

def get_user_role(user_id):
    query = "SELECT role FROM users WHERE user_id = %s;"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                result = cur.fetchone()
                if result:
                    return result[0]  
                else:
                    return None
    except Exception as e:
        st.error(f"Ошибка при получении роли пользователя: {e}")
        return None
    