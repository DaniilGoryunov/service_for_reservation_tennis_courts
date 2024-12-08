import streamlit as st
from datetime import date
import pandas as pd
from services.sales import SalesService
import repositories.products
import random

# Хранение добавленных товаров в таблице
if "sales_table" not in st.session_state:
    st.session_state.sales_table = pd.DataFrame(
        columns=["Название продукта", "Barcode", "Количество"]
    )

@st.cache_data
def get_products() -> dict[str, str]:
    print("Получение продуктов")
    products = repositories.products.get_products()
    return {product["name"]: product["barcode"] for product in products}

def add_product_event(product_name, product_barcode, product_quantity):
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

def clear_table_event():
    st.session_state.sales_table = pd.DataFrame(
        columns=["Название продукта", "Barcode", "Количество"]
    )

def upload_sales(sales_table: pd.DataFrame) -> int:
    sale_date = date(2024, random.randint(1, 12), random.randint(1, 28))
    sale_id = SalesService().process_sale(
        sale_date,
        sales_table,
    )
    st.write(f"Продажа за число {sale_date}")
    return sale_id

def show_selling_products_page():
    if 'user' not in st.session_state:
        st.warning("Пожалуйста, войдите в систему, чтобы продолжить.")
        return 

    st.title("Продажа продуктов")

    products = get_products()
    selected_product = st.selectbox("Выберите продукт", products.keys())
    quantity = st.number_input("Количество", min_value=1, max_value=100, value=1)

    # кнопки
    add_product_btn = st.button("Добавить продукт")
    clear_table_btn = st.button("Очистить таблицу")
    apply_btn = st.button("Подтвердить продажу")

    # event handlers
    if add_product_btn:
        add_product_event(selected_product, products[selected_product], quantity)

    if clear_table_btn:
        clear_table_event()

    if apply_btn and len(st.session_state.sales_table) > 0:
        sale_id = upload_sales(st.session_state.sales_table)
        st.success(f"Продажа добавлена успешно! ID чека: {sale_id}")
        clear_table_event()

    st.write("Добавленные товары:")
    st.dataframe(st.session_state.sales_table)