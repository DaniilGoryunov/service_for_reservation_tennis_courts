import os
import psycopg2
from dotenv import load_dotenv
from security.example_password import hash_password, check_password  # Импортируем функции из example_password.py

load_dotenv("env.env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def register_user(username, password):
    password_hash = hash_password(password)  # Используем функцию хеширования
    query = "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id;"
    
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username, password_hash))  # Сохраняем как байты
            user_id = cur.fetchone()[0]
            conn.commit()
    
    return user_id

def authenticate_user(username, password):
    query = "SELECT password_hash FROM users WHERE username = %s;"
    
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            result = cur.fetchone()
            if result and check_password(password, result[0]):  
                return True
            return False