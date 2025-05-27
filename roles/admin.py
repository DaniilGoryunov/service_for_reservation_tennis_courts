import streamlit as st
import psycopg2
from services.reserv import *
from services.in_table import *
from roles import *
from services import *
from services.redis_service import (
    get_cached_all_reservations,
    cache_all_reservations,
    redis_client,
    deserialize_from_json
)
import json

def show_admin_cache_debug():
    """Показывает отладочную информацию о кэше всех резерваций"""
    if st.checkbox("Показать отладочную информацию кэша администратора"):
        key = "reservations:all"
        value = redis_client.get(key)
        ttl = redis_client.ttl(key)
        
        if value:
            try:
                reservations = deserialize_from_json(value)
                st.write(f"🔍 Кэш всех резерваций (TTL: {ttl} сек.):")
                st.write(f"Общее количество резерваций в кэше: {len(reservations)}")
                
                # Группируем резервации по пользователям
                user_reservations = {}
                for res in reservations:
                    username = res[4]  # Индекс username в кортеже
                    if username not in user_reservations:
                        user_reservations[username] = []
                    user_reservations[username].append(res)
                
                # Показываем статистику по пользователям
                st.write("📊 Статистика по пользователям:")
                for username, user_res in user_reservations.items():
                    st.write(f"Пользователь {username}: {len(user_res)} резерваций")
                
                # Показываем детали каждой резервации
                st.write("📝 Детали резерваций:")
                for i, res in enumerate(reservations, 1):
                    st.code(f"Резервация #{i}:\n{json.dumps(res, indent=2, ensure_ascii=False, default=str)}")
            except Exception as e:
                st.error(f"Ошибка при разборе кэша: {str(e)}")
        else:
            st.info("В кэше нет данных о резервациях")

# Страница для администратора
def admin_page():
    st.subheader("Все записи на корты")
    reservations = get_all_reservations()

    # Фильтрация записей
    reservations = filter_reservations(reservations)

    # Отображение записей
    display_reservations(reservations, role="admin")
    
    # Показываем отладочную информацию о кэше
    show_admin_cache_debug()