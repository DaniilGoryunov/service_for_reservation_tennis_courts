import streamlit as st
import asyncio
import redis
import json
from services.redis_service import (
    get_user_session, get_user_id_from_token, 
    get_cached_user_data, get_cached_user_role,
    redis_client
)
from services.auth import get_user_id

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True 
)

def test_redis_connection():
    try:
        r.ping()
        st.success("✅ Redis подключен успешно!")
        
        # Тест записи/чтения
        r.set("test_key", "Hello from Tennis App!")
        value = r.get("test_key")
        st.write(f"Тестовое значение из Redis: {value}")
        
    except Exception as e:
        st.error(f"❌ Ошибка подключения к Redis: {e}")

async def restore_session():
    """Восстанавливает сессию пользователя из Redis"""
    if 'token' in st.session_state:
        user_id = get_user_id_from_token(st.session_state.token)
        if user_id:
            session_data = get_user_session(user_id)
            if session_data:
                st.session_state.user = session_data['username']
                st.session_state.user_id = user_id
                return True
    return False

async def check_user_session():
    # Сначала проверяем, есть ли активная сессия в Redis
    if 'token' in st.session_state:
        if await restore_session():
            return True, st.session_state.user
    
    # Если нет активной сессии, проверяем локальное состояние
    if 'user' in st.session_state and 'user_id' in st.session_state:
        return True, st.session_state.user
    return False, None

def show_redis_debug_info():
    """Показывает отладочную информацию о данных в Redis"""
    if st.checkbox("Показать отладочную информацию Redis"):
        st.subheader("Данные в Redis:")
        
        # Получаем все ключи
        all_keys = redis_client.keys("*")
        
        if not all_keys:
            st.info("В Redis нет данных")
            return
            
        # Группируем ключи по типам
        auth_keys = [k for k in all_keys if k.startswith("auth:")]
        session_keys = [k for k in all_keys if k.startswith("session:")]
        user_keys = [k for k in all_keys if k.startswith("user:")]
        reservation_keys = [k for k in all_keys if k.startswith("reservations:")]
        
        # Показываем токены авторизации
        if auth_keys:
            st.write("🔑 Токены авторизации:")
            for key in auth_keys:
                value = redis_client.get(key)
                ttl = redis_client.ttl(key)
                st.code(f"Ключ: {key}\nЗначение: {value}\nTTL: {ttl} сек.")
        
        # Показываем сессии
        if session_keys:
            st.write("👤 Сессии пользователей:")
            for key in session_keys:
                value = redis_client.get(key)
                ttl = redis_client.ttl(key)
                try:
                    session_data = json.loads(value)
                    st.code(f"Ключ: {key}\nДанные: {json.dumps(session_data, indent=2, ensure_ascii=False)}\nTTL: {ttl} сек.")
                except:
                    st.code(f"Ключ: {key}\nЗначение: {value}\nTTL: {ttl} сек.")
        
        # Показываем данные пользователей
        if user_keys:
            st.write("👥 Данные пользователей:")
            for key in user_keys:
                value = redis_client.get(key)
                ttl = redis_client.ttl(key)
                try:
                    user_data = json.loads(value)
                    st.code(f"Ключ: {key}\nДанные: {json.dumps(user_data, indent=2, ensure_ascii=False)}\nTTL: {ttl} сек.")
                except:
                    st.code(f"Ключ: {key}\nЗначение: {value}\nTTL: {ttl} сек.")

        # Показываем резервации
        if reservation_keys:
            st.write("🎾 Резервации кортов:")
            for key in reservation_keys:
                value = redis_client.get(key)
                ttl = redis_client.ttl(key)
                try:
                    reservations = json.loads(value)
                    st.code(f"Ключ: {key}\nКоличество резерваций: {len(reservations)}\nTTL: {ttl} сек.")
                    # Показываем детали каждой резервации
                    for i, res in enumerate(reservations, 1):
                        st.code(f"Резервация #{i}:\n{json.dumps(res, indent=2, ensure_ascii=False, default=str)}")
                except Exception as e:
                    st.code(f"Ключ: {key}\nОшибка при разборе данных: {str(e)}\nTTL: {ttl} сек.")

async def main():
    st.title("Резервирование теннисных кортов")
    test_redis_connection()
    
    # Пытаемся восстановить сессию при загрузке страницы
    is_authenticated, user = await check_user_session()
    if is_authenticated:
        st.success(f"Вы вошли как {user}")
        # Показываем отладочную информацию, если пользователь авторизован
        show_redis_debug_info()
    else:
        st.error("Вы не авторизированны. Пройдите во вкладку registration")
        # Очищаем все данные сессии, если аутентификация не удалась
        if 'token' in st.session_state:
            del st.session_state.token
        if 'user' in st.session_state:
            del st.session_state.user
        if 'user_id' in st.session_state:
            del st.session_state.user_id

    if 'show_image' not in st.session_state:
        st.session_state.show_image = False

    if st.button("Сюрприз"):
        st.session_state.show_image = not st.session_state.show_image

    if st.session_state.show_image:
        st.image("images/моя_боль.png", width=500)

if __name__ == "__main__":
    asyncio.run(main())
