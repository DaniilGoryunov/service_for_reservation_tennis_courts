import psycopg2
from dotenv import load_dotenv
import os
import bcrypt

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
    query_insert = "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id;"
    
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Проверяем, существует ли пользователь с таким именем
            cur.execute(query_check, (username,))
            if cur.fetchone()[0] > 0:
                return None  # Пользователь уже существует
            
            # Если пользователь не существует, выполняем вставку
            cur.execute(query_insert, (username, password_hash))
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

def get_user_id(username):
    query = "SELECT user_id FROM users WHERE username = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            result = cur.fetchone()
            return result[0] if result else None