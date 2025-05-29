import streamlit as st
from service_for_reservation_tennis_courts.roles.admin import admin_page
from service_for_reservation_tennis_courts.roles.coach import coach_page
from service_for_reservation_tennis_courts.roles.user import user_page
from service_for_reservation_tennis_courts.pages.registration import show_auth_page
from services.redis_service import (
    get_user_session, set_user_session, delete_user_session,
    get_cached_user_reservations, get_cached_coach_reservations,
    get_cached_all_reservations,
    subscribe_to_notifications
)
import threading
import json
import time

def notification_listener():
    """Функция для прослушивания уведомлений в фоновом режиме"""
    pubsub = subscribe_to_notifications()
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                notification_type = data.get('type')
                
                if notification_type == 'new_reservation':
                    st.session_state['notifications'].append({
                        'type': 'success',
                        'message': f"Новая резервация: Корт {data['court_id']} на {data['reservation_time']}"
                    })
                elif notification_type == 'cancel_reservation':
                    st.session_state['notifications'].append({
                        'type': 'info',
                        'message': f"Отменена резервация: Корт {data['court_id']}"
                    })
                elif notification_type == 'coach_assigned':
                    st.session_state['notifications'].append({
                        'type': 'success',
                        'message': f"Тренер {data['coach_id']} назначен на вашу тренировку"
                    })
                
                # Ограничиваем количество уведомлений
                if len(st.session_state['notifications']) > 5:
                    st.session_state['notifications'] = st.session_state['notifications'][-5:]
                
            except Exception as e:
                print(f"Ошибка обработки уведомления: {e}")
        time.sleep(0.1)

def init_session():
    """Инициализация сессии"""
    if 'notifications' not in st.session_state:
        st.session_state['notifications'] = []
    
    if 'notification_thread' not in st.session_state:
        st.session_state['notification_thread'] = threading.Thread(
            target=notification_listener,
            daemon=True
        )
        st.session_state['notification_thread'].start()

def show_notifications():
    """Отображение уведомлений"""
    if st.session_state['notifications']:
        for notification in st.session_state['notifications']:
            if notification['type'] == 'success':
                st.success(notification['message'])
            elif notification['type'] == 'info':
                st.info(notification['message'])
            elif notification['type'] == 'error':
                st.error(notification['message'])

def main():
    init_session()
    
    # Инициализация состояния сессии
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
        st.session_state['user_role'] = None
    
    # Проверка сессии
    session_data = get_user_session(st.session_state.get('session_id'))
    if session_data:
        st.session_state['user_id'] = session_data.get('user_id')
        st.session_state['user_role'] = session_data.get('user_role')
    
    st.title("Теннисный клуб - Система бронирования")
    
    # Показываем уведомления
    show_notifications()
    
    if st.session_state['user_id'] is None:
        show_auth_page()
    else:
        if st.session_state['user_role'] == 'admin':
            admin_page()
        elif st.session_state['user_role'] == 'coach':
            coach_page()
        else:
            user_page()
        
        if st.sidebar.button("Выйти"):
            delete_user_session(st.session_state.get('session_id'))
            st.session_state['user_id'] = None
            st.session_state['user_role'] = None
            st.session_state['session_id'] = None
            st.experimental_rerun() 