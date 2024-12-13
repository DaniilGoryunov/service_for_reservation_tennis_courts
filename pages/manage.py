import streamlit as st
from services.reserv import *
from services.in_table import *
from roles.user import *

user_id = st.session_state.get("user_id")
role = get_user_role(user_id) 

if role == 'admin':
    manage_users()
else:
    st.error("У вас нет прав для доступа к этой функции.")