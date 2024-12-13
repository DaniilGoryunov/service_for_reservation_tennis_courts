import streamlit as st
import psycopg2
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
from roles.user import *
from services.reviews import *

def show_reviews():
    # Асинхронный вызов для получения отзывов
    if 'reviews_visible' not in st.session_state:
        st.session_state.reviews_visible = False

    if st.button("Показать отзывы"):
        st.session_state.reviews_visible = not st.session_state.reviews_visible

    if st.session_state.reviews_visible:
        reviews = asyncio.run(async_fetch_reviews())
        st.write("Отзывы:")
        for review in reviews:
            st.write(f"Пользователь {review[0]}  \n  **Отзыв:** {review[1]}  \n  **Рейтинг:** {review[2]}  \n  **Корт:** {review[3]}")

    # Форма для добавления нового отзыва
    with st.form("Добавить отзыв"):
        user_id = st.session_state.get("user_id")
        user_reservations = get_user_reservations(user_id)
        court_ids = [reservation[4] for reservation in user_reservations]  # Предполагается, что court_id находится на позиции 1
        court_ids = set(court_ids)
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
