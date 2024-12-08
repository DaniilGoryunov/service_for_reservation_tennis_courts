import streamlit as st
from auth import register_user, authenticate_user

def show_auth_page():
    st.title("Авторизация")

    menu = st.selectbox("Выберите действие", ["Вход", "Регистрация"])

    if menu == "Регистрация":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        confirm_password = st.text_input("Подтвердите пароль", type="password")
        
        if st.button("Зарегистрироваться"):
            if password == confirm_password:
                user_id = register_user(username, password)
                st.success(f"Пользователь зарегистрирован с ID: {user_id}")
            else:
                st.error("Пароли не совпадают!")

    elif menu == "Вход":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти", key="login_button"):  # Уникальный ключ
            if authenticate_user(username, password):
                st.session_state.user = username  # Сохраняем имя пользователя в сессии
                st.success("Успешный вход!")
                st.session_state.show_auth = False  # Скрываем форму аутентификации
            else:
                st.error("Неверное имя пользователя или пароль.")