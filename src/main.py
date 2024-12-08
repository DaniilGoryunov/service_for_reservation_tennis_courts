import streamlit as st
from pages.selling_products import show_selling_products_page
from pages.analyze_sales import show_analyze_sales_page
from pages.registration import show_auth_page

def main():
    st.title("Добро пожаловать в приложение")

    # Боковая панель для навигации
    if 'user' in st.session_state:
        st.success(f"Вы вошли как {st.session_state.user}")
        
        # Боковая панель с кнопками для навигации
        menu = st.sidebar.radio("Выберите действие", ["Анализ продаж", "Продажа продуктов", "Выйти"])
        
        if menu == "Выйти":
            del st.session_state.user  # Удаляем информацию о пользователе из сессии
            st.success("Вы вышли из системы.")
        elif menu == "Продажа продуктов":
            show_selling_products_page()
        elif menu == "Анализ продаж":
            show_analyze_sales_page()
    else:
        # Если пользователь не вошел, показываем кнопку "Войти"
        if st.sidebar.button("Войти", key="login_sidebar"):  # Уникальный ключ
            st.session_state.show_auth = True  # Устанавливаем флаг для отображения формы аутентификации

        if 'show_auth' in st.session_state and st.session_state.show_auth:
            show_auth_page()  # Показываем форму аутентификации, если флаг установлен
        else:
            st.info("Пожалуйста, войдите в систему, чтобы продолжить.")

if __name__ == "__main__":
    main()