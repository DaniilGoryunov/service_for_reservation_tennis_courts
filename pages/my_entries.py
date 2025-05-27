import streamlit as st
from roles.admin import admin_page
from roles.coach import coach_page
from roles.user import user_page, get_user_role

def show_user_reservations_page():
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
        return

    role = get_user_role(user_id)  
    st.write(f"Ваша роль: {role}")

    if role == "admin":
        admin_page()
    elif role == "coach":
        coach_page(user_id)
    else:  
        user_page(user_id)

show_user_reservations_page()
