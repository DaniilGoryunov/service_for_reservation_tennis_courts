import streamlit as st
from pages.registration import show_auth_page
from pages.reservation import show_reservation_page

def main():
    st.title("Резервирование теннисных кортов")

    if 'user' in st.session_state:
        st.success(f"Вы вошли как {st.session_state.user}")
        show_reservation_page()
    else:
        if st.sidebar.button("Войти", key="login_sidebar"):
            st.session_state.show_auth = True

        if 'show_auth' in st.session_state and st.session_state.show_auth:
            show_auth_page()

if __name__ == "__main__":
    main()