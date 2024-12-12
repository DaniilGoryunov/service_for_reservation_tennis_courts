import streamlit as st
from services.reserv import *
from datetime import datetime

# Функция для отображения страницы с записями пользователя
def show_user_reservations_page():

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
        return

    role = get_user_role(user_id) # Получаем роль пользователя
    
    st.write(f"Ваша роль: {role}")

    if role == "admin":
        st.subheader("Все записи на корты")
        reservations = get_all_reservations()  # Получаем все записи

        # Фильтрация записей
        filter_user = st.text_input("Фильтр по имени пользователя")
        filter_date = st.date_input("Фильтр по дате")

        if filter_user:
            reservations = [r for r in reservations if isinstance(r[4], str) and filter_user.lower() in r[4].lower()]
        if filter_date:
            reservations = [r for r in reservations if isinstance(r[1], datetime) and r[1].date() == filter_date]

    elif role == "coach":
        st.subheader("Ваши записи как тренера")
        reservations = get_coach_reservations(user_id)  # Получаем записи, где пользователь тренер
    else:  # роль user
        st.subheader("Ваши записи на корты")
        reservations = get_user_reservations(user_id)  # Получаем записи пользователя

    if reservations:
        st.write("Ваши текущие записи:")

        for reservation in reservations:
            if len(reservation) == 6:
                reservation_id, reservation_time, duration, surface, username, coach_name = reservation
            elif len(reservation) == 5:
                reservation_id, reservation_time, duration, surface, coach_name = reservation
                username = ""
            else:
                st.error("Ошибка в структуре данных записей.")
                continue

            if isinstance(reservation_time, datetime):
                reservation_time_str = reservation_time.strftime("%Y-%m-%d %H:%M")
            else:
                reservation_time_str = str(reservation_time)

            coach_info = f"Тренер: {coach_name}" if coach_name else "Без тренера"

            st.write(f"- **Дата и время:** {reservation_time_str}")
            st.write(f"  **Длительность:** {duration} минут")
            st.write(f"  **Покрытие корта:** {surface}")
            if username:
                st.write(f"  **Пользователь:** {username}")
            st.write(f"  {coach_info}")

            # Дополнительный функционал для admin
            if role == "admin":
                if st.button(f"Удалить запись №{reservation_id}", key=f"delete_{reservation_id}"):
                    success = cancel_reservation(reservation_id)
                    if success:
                        st.success(f"Запись №{reservation_id} успешно удалена.")
                    else:
                        st.error(f"Не удалось удалить запись №{reservation_id}.")

            st.write("---")
    else:
        st.write("У вас пока нет записей на корты.")

show_user_reservations_page()
