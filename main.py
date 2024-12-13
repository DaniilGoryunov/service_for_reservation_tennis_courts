import streamlit as st

def main():
    st.title("Резервирование теннисных кортов")

    if 'user' in st.session_state:
        st.success(f"Вы вошли как {st.session_state.user}")
    else:
        st.error(f"Вы не авторизированны. Пройдите во вкладку registrarion")
    
    if 'show_image' not in st.session_state:
        st.session_state.show_image = False

    if st.button("Сюрприз"):
        st.session_state.show_image = not st.session_state.show_image

    if st.session_state.show_image:
        st.image("images/моя_боль.png", width=500) 
if __name__ == "__main__":
    main()