import streamlit as st
import psycopg2
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from roles.user import *

load_dotenv("env.env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Функция для получения отзывов
def fetch_reviews():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, review_text, rating, court_id FROM user_reviews")
            reviews = cursor.fetchall()
            return reviews

# Функция для добавления отзыва
def add_review(username, court_id, review_text, rating):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_reviews (user_id, court_id, review_text, rating) VALUES (%s, %s, %s, %s)",
                (username, court_id, review_text, rating)
            )
            conn.commit()

async def async_fetch_reviews():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(ThreadPoolExecutor(), fetch_reviews)

async def async_add_review(user_id, court_id, review_text, rating):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(ThreadPoolExecutor(), add_review, user_id, court_id, review_text, rating)

def show_reviews():
# Асинхронный вызов для получения отзывов
    if st.button("Показать отзывы"):
        reviews = asyncio.run(async_fetch_reviews())
        st.write("Отзывы:")
        for review in reviews:
            st.write(f"Пользователь {review[0]}  \n  **Отзыв:** {review[1]}  \n  **Рейтинг:** {review[2]}  \n  **Корт:** {review[3]}")

    # Форма для добавления нового отзыва
    with st.form("Добавить отзыв"):
        user_id = st.session_state.get("user_id")
        user_reservations = get_user_reservations(user_id)
        court_ids = [reservation[5] for reservation in user_reservations]  # Предполагается, что court_id находится на позиции 1
        court_id = st.selectbox("Выберите корт", court_ids)
        review_text = st.text_area("Текст отзыва")
        rating = st.slider("Рейтинг", 1, 5)
        submitted = st.form_submit_button("Отправить отзыв")
        if submitted:
            if not court_id or not review_text:
                st.error("Пожалуйста, заполните все поля.")
            else:
                asyncio.run(async_add_review(user_id, court_id, review_text, rating))
                st.success("Отзыв успешно добавлен!")



if 'user_id' in st.session_state:
    show_reviews()
else:
    st.error("Вы не авторизованы. Пожалуйста, войдите в систему.")
