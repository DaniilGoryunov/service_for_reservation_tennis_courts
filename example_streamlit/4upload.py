import os

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv
from pandas import DataFrame
from datetime import datetime

load_dotenv("env.env")

# Чтение и установка env
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# Pool settings
POOL_MIN_CONN = int(os.getenv("POOL_MIN_CONN", 1))
POOL_MAX_CONN = int(os.getenv("POOL_MAX_CONN", 10))


# Функции для работы с БД
def add_delivery(supplier_id, delivery_date):
    query = """
        INSERT INTO deliveries (supplier_id, delivery_date)
        VALUES (%(supplier_id)s, %(delivery_date)s) RETURNING delivery_id;
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                query, {"supplier_id": supplier_id, "delivery_date": delivery_date}
            )
            delivery_id = cur.fetchone()[0]
            conn.commit()

    return delivery_id


def add_delivery_contents(delivery: DataFrame):
    query = """
        INSERT INTO delivery_contents (delivery_id, barcode, quantity)
        VALUES (%s, %s, %s);
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                query,
                delivery[["delivery_id", "barcode", "quantity"]].itertuples(
                    index=False, name=None
                ),
            )


# Создание виджетов
st.title("CSV Viewer")
file = st.file_uploader("Upload your CSV file", type=["csv"])
btn = st.button("Добавить данные")

df = None
# Обработка загрузки файла
if file is not None:
    df = pd.read_csv(file)
    st.write(df)

# Обработка нажатия кнопки
if btn and df is not None:
    delivery_id = add_delivery(1, datetime.now())
    df["delivery_id"] = delivery_id
    add_delivery_contents(df)
    st.write("Данные загружены")
elif btn and df is None:
    st.write("Please upload a CSV file")
