import streamlit as st
import os
from dotenv import load_dotenv
from services.auth import *
from services.redis_service import get_user_session, cache_user_data

load_dotenv("env.env")

def show_auth_page():
    st.title("Авторизация")

    menu = st.selectbox("Выберите действие", ["Вход", "Регистрация"], key="auth_menu_unique")

    if menu == "Регистрация":
        username = st.text_input("Имя пользователя", key="register_username")
        password = st.text_input("Пароль", type="password", key="register_password")
        confirm_password = st.text_input("Подтвердите пароль", type="password", key="confirm_password")
        
        if st.button("Зарегистрироваться"):
            if password == confirm_password:
                user_id = register_user(username, password)
                if user_id:
                    # Кэшируем данные нового пользователя
                    user_data = {
                        'username': username,
                        'user_id': user_id,
                        'role': 'user'
                    }
                    cache_user_data(username, user_data)
                    st.success("Регистрация успешна! Теперь вы можете войти.")
            else:
                st.error("Пароли не совпадают!")

    elif menu == "Вход":
        username = st.text_input("Имя пользователя", key="login_username")
        password = st.text_input("Пароль", type="password", key="login_password")
        if st.button("Войти", key="login_button"):
            token, user_id = login_user(username, password)
            if token and user_id:
                st.session_state.user = username
                st.session_state.user_id = user_id
                st.session_state.token = token
                st.success("Успешный вход!")
                st.session_state.show_auth = False
            else:
                st.error("Неверное имя пользователя или пароль.")

    if 'user' in st.session_state:
        if st.button("Выйти"):
            if 'token' in st.session_state and 'user_id' in st.session_state:
                logout_user(st.session_state.user_id, st.session_state.token)
            del st.session_state.user
            del st.session_state.user_id
            if 'token' in st.session_state:
                del st.session_state.token
            st.success("Вы вышли из аккаунта.")


show_auth_page()