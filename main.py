import streamlit as st
import asyncio

async def check_user_session():
    if 'user' in st.session_state:
        return True, st.session_state.user
    else:
        return False, None

async def main():
    st.title("Резервирование теннисных кортов")

    is_authenticated, user = await check_user_session()
    if is_authenticated:
        st.success(f"Вы вошли как {user}")
    else:
        st.error("Вы не авторизированны. Пройдите во вкладку registrarion")

    if 'show_image' not in st.session_state:
        st.session_state.show_image = False

    if st.button("Сюрприз"):
        st.session_state.show_image = not st.session_state.show_image

    if st.session_state.show_image:
        st.image("images/моя_боль.png", width=500)

if __name__ == "__main__":
    asyncio.run(main())
