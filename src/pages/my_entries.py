import streamlit as st
from services.reserv import get_user_reservations, cancel_reservation

# Функция для отображения страницы с записями пользователя
def show_user_reservations_page():
    st.title("Ваши записи на корты")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
        return

    # Получаем записи пользователя
    reservations = get_user_reservations(user_id)

    if reservations:
        st.write("Ваши текущие записи:")

        # Форматируем записи в таблицу
        for reservation in reservations:
            reservation_id, reservation_time, duration, surface, coach_name = reservation
            reservation_time = reservation_time.strftime("%Y-%m-%d %H:%M")
            coach_info = f"Тренер: {coach_name}" if coach_name else "Без тренера"

            st.write(f"- **Дата и время:** {reservation_time}")
            st.write(f"  **Длительность:** {duration} минут")
            st.write(f"  **Покрытие корта:** {surface}")
            st.write(f"  {coach_info}")

            # Добавляем кнопку для отмены записи
            if st.button(f"Отменить запись №{reservation_id}", key=f"cancel_{reservation_id}"):
                success = cancel_reservation(reservation_id)
                if success:
                    st.success(f"Запись №{reservation_id} успешно отменена.")
                else:
                    st.error(f"Не удалось отменить запись №{reservation_id}.")

            st.write("---")
    else:
        st.write("У вас пока нет записей на корты.")

show_user_reservations_page()
