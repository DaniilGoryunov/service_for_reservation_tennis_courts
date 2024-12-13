from concurrent.futures import ThreadPoolExecutor
import psycopg2
from dotenv import load_dotenv
import os
import asyncio

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