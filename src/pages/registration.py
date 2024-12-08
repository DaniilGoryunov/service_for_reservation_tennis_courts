import streamlit as st
import os
from dotenv import load_dotenv
from auth import register_user, authenticate_user, get_user_id  # Импортируем функции

load_dotenv("env.env")

def show_auth_page():
    st.title("Авторизация")

    menu = st.selectbox("Выберите действие", ["Вход", "Регистрация"])

    if menu == "Регистрация":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        confirm_password = st.text_input("Подтвердите пароль", type="password")
        
        if st.button("Зарегистрироваться"):
            if password == confirm_password:
                user_id = register_user(username, password)  # Используем функцию из auth.py
                st.success(f"Пользователь зарегистрирован с ID: {user_id}")
            else:
                st.error("Пароли не совпадают!")

    elif menu == "Вход":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти", key="login_button"):
            if authenticate_user(username, password):  # Используем функцию из auth.py
                user_id = get_user_id(username)  # Получаем user_id
                if user_id is not None:
                    st.session_state.user = username
                    st.session_state.user_id = user_id  # Сохраняем user_id после успешного входа
                    st.success("Успешный вход!")
                    st.session_state.show_auth = False
                else:
                    st.error("Не удалось получить user_id.")
            else:
                st.error("Неверное имя пользователя или пароль.")