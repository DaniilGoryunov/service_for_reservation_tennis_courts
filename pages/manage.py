import streamlit as st
from roles.user import manage_users, get_user_role
from services.back_up import create_backup

user_id = st.session_state.get("user_id")
role = get_user_role(user_id) 

if role == 'admin':
    manage_users()
    
    if st.button("Сделать резервную копию базы данных"):
        try:
            create_backup()
        except Exception as e:
            st.error(f"Ошибка при создании резервной копии: {e}")
else:
    st.error("У вас нет прав для доступа к этой функции.")