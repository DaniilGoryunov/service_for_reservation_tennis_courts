import psycopg2
from dotenv import load_dotenv
import os
import bcrypt
import streamlit as st
from .redis_service import (
    generate_token, get_user_id_from_token, delete_token,
    cache_user_role, get_cached_user_role, store_user_session,
    get_user_session, delete_user_session, cache_user_data,
    get_cached_user_data, TOKEN_TTL
)
from datetime import datetime

load_dotenv("env.env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Хеширование пароля
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Проверка пароля
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, password):
    password_hash = hash_password(password)
    query_check = "SELECT COUNT(*) FROM users WHERE username = %s;"
    query_insert = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING user_id;"
    
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Проверяем, существует ли пользователь с таким именем
            cur.execute(query_check, (username,))
            if cur.fetchone()[0] > 0:
                st.error("Пользователь с таким именем уже существует.")  # Добавлена проверка
                return  
            else: 
                role = "user"
            
            # Если пользователь не существует, выполняем вставку
            cur.execute(query_insert, (username, password_hash, role))
            user_id = cur.fetchone()[0]
            conn.commit()
            st.success(f"Пользователь зарегистрирован с ID: {user_id}")
    return user_id

def authenticate_user(username, password):
    # Сначала проверяем кэш
    cached_user_data = get_cached_user_data(username)
    if cached_user_data and check_password(password, cached_user_data['password_hash']):
        return True

    query = "SELECT user_id, password_hash, role FROM users WHERE username = %s;"
    
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            result = cur.fetchone()
            if result and check_password(password, result[1]):
                user_id, _, role = result
                # Кэшируем данные пользователя
                user_data = {
                    'user_id': user_id,
                    'username': username,
                    'password_hash': result[1],
                    'role': role
                }
                cache_user_data(username, user_data)
                cache_user_role(user_id, role)
                return True
            return False

def login_user(username, password):
    """Расширенная функция входа с использованием Redis"""
    if authenticate_user(username, password):
        user_id = get_user_id(username)
        if user_id:
            # Генерируем токен
            token = generate_token(user_id, TOKEN_TTL)
            
            # Сохраняем сессию
            session_data = {
                'username': username,
                'user_id': user_id,
                'token': token
            }
            store_user_session(user_id, session_data)
            
            # Публикуем событие входа
            from .redis_service import publish_event
            publish_event('user_login', {
                'user_id': user_id,
                'username': username,
                'timestamp': str(datetime.now())
            })
            
            return token, user_id
    return None, None

def logout_user(user_id, token):
    """Функция выхода с очисткой данных в Redis"""
    delete_token(token)
    delete_user_session(user_id)
    
    # Публикуем событие выхода
    from .redis_service import publish_event
    publish_event('user_logout', {
        'user_id': user_id,
        'timestamp': str(datetime.now())
    })

def get_user_id(username):
    query = "SELECT user_id FROM users WHERE username = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            result = cur.fetchone()
            return result[0] if result else None