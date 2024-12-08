import os
from datetime import date

import pandas as pd
import psycopg2
import psycopg2.extras
import streamlit as st
from dotenv import load_dotenv

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


# @st.cache_data
def get_products() -> dict[str, str]:
    print("Получение продуктов")
    query = "SELECT barcode, name FROM products;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            products = cur.fetchall()

    return {product["name"]: product["barcode"] for product in products}


def add_sale(sale_date: date) -> int:
    query = """
        INSERT INTO sales (sale_date)
        VALUES (%(sale_date)s) RETURNING sale_id;
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"sale_date": sale_date})
            return cur.fetchone()[0]


def add_sale_details(sales: pd.DataFrame) -> None:
    query = """
        INSERT INTO sales_details (sale_id, barcode, quantity)
        VALUES (%s, %s, %s);
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                query,
                sales[["sale_id", "barcode", "quantity"]].itertuples(
                    index=False, name=None
                ),
            )


products = get_products()

# Хранение добавленных товаров в таблице
if "sales_table" not in st.session_state:
    st.session_state.sales_table = pd.DataFrame(
        columns=["Название продукта", "Barcode", "Количество"]
    )


st.title("Продажа продуктов")

# Поля для ввода данных
selected_product = st.selectbox("Выберите продукт", products.keys())
quantity = st.number_input("Количество", min_value=1, max_value=100, value=1)

# кнопки
add_product_btn = st.button("Добавить продукт")
clear_table_btn = st.button("Очистить таблицу")
apply_btn = st.button("Подтвердить продажу")


def add_product(product_name, product_barcode, product_quantity):
    new_row = pd.DataFrame(
        {
            "Название продукта": [product_name],
            "Barcode": [product_barcode],
            "Количество": [product_quantity],
        }
    )
    st.session_state.sales_table = pd.concat(
        [st.session_state.sales_table, new_row], ignore_index=True
    )


def clear_table():
    st.session_state.sales_table = pd.DataFrame(
        columns=["Название продукта", "Barcode", "Количество"]
    )
    # st.rerun()


def upload_sales(sales_table: pd.DataFrame) -> int:
    items = sales_table.rename(columns={"Количество": "quantity", "Barcode": "barcode"})
    items = items.groupby("barcode", as_index=False)["quantity"].sum()
    sale_id = add_sale(date.today())

    items["sale_id"] = sale_id
    add_sale_details(items)

    return sale_id


# event handlers
if add_product_btn:
    add_product(selected_product, products[selected_product], quantity)

if clear_table_btn:
    clear_table()

if apply_btn and len(st.session_state.sales_table) > 0:
    sale_id = upload_sales(st.session_state.sales_table)
    st.success(f"Продажа добавлена успешно! ID чека: {sale_id}")
    clear_table()

st.write("Добавленные товары:")
st.dataframe(st.session_state.sales_table)
