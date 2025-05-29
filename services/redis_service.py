import redis
import os
import json
import secrets
from datetime import datetime

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    db=0,
    decode_responses=True
)

# Константы для TTL
TOKEN_TTL = 3600  # 1 час
SESSION_TTL = 86400  # 24 часа
CACHE_TTL = 300  # 5 минут
RESERVATION_CACHE_TTL = 60  # 1 минута для резерваций

# Константы для каналов уведомлений
NOTIFICATION_CHANNELS = {
    'new_reservation': 'notifications:new_reservation',
    'cancel_reservation': 'notifications:cancel_reservation',
    'coach_assigned': 'notifications:coach_assigned',
    'court_available': 'notifications:court_available'
}

class DateTimeEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для datetime объектов"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                '_type': 'datetime',
                'value': obj.isoformat()
            }
        return super().default(obj)

class DateTimeDecoder(json.JSONDecoder):
    """Кастомный JSON декодер для datetime объектов"""
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if '_type' in dct and dct['_type'] == 'datetime':
            return datetime.fromisoformat(dct['value'])
        return dct

def serialize_to_json(data):
    """Сериализует данные в JSON с поддержкой datetime"""
    return json.dumps(data, cls=DateTimeEncoder)

def deserialize_from_json(data):
    """Десериализует JSON в данные с поддержкой datetime"""
    return json.loads(data, cls=DateTimeDecoder)

def generate_token(user_id, ttl=3600):
    """Генерирует токен и сохраняет user_id в Redis"""
    token = secrets.token_hex(16)
    redis_client.setex(f"auth:{token}", ttl, str(user_id))
    return token

def get_user_id_from_token(token):
    """Возвращает user_id из Redis по токену"""
    if not token:
        return None
    return int(redis_client.get(f"auth:{token}")) if redis_client.exists(f"auth:{token}") else None

def delete_token(token):
    """Удаляет токен из Redis"""
    redis_client.delete(f"auth:{token}")

def cache_user_role(user_id, role, ttl=3600):
    """Кэширует роль пользователя"""
    redis_client.setex(f"user:{user_id}:role", ttl, role)

def get_cached_user_role(user_id):
    """Получает роль из кэша или None"""
    return redis_client.get(f"user:{user_id}:role")

def publish_reservation_update(reservation_data):
    """Публикует событие о новом бронировании"""
    redis_client.publish("channel_reservations", json.dumps(reservation_data))

def subscribe_to_reservations():
    """Подписка на события бронирования"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe("channel_reservations")
    return pubsub

def store_user_session(user_id, session_data):
    """Сохраняет сессионные данные пользователя"""
    key = f"session:{user_id}"
    redis_client.setex(key, SESSION_TTL, json.dumps(session_data))

def get_user_session(user_id):
    """Получает сессионные данные пользователя"""
    key = f"session:{user_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_user_session(user_id):
    """Удаляет сессионные данные пользователя"""
    key = f"session:{user_id}"
    redis_client.delete(key)

def cache_user_data(user_id, user_data):
    """Кэширует данные пользователя"""
    key = f"user:{user_id}:data"
    redis_client.setex(key, CACHE_TTL, json.dumps(user_data))

def get_cached_user_data(user_id):
    """Получает кэшированные данные пользователя"""
    key = f"user:{user_id}:data"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def cache_court_availability(court_id, availability_data):
    """Кэширует данные о доступности корта"""
    key = f"court:{court_id}:availability"
    redis_client.setex(key, CACHE_TTL, json.dumps(availability_data))

def get_cached_court_availability(court_id):
    """Получает кэшированные данные о доступности корта"""
    key = f"court:{court_id}:availability"
    data = redis_client.get(key)
    return json.loads(data) if data else None

def publish_event(event_type, event_data):
    """Публикует событие в Redis PubSub"""
    channel = f"channel_{event_type}"
    redis_client.publish(channel, json.dumps(event_data))

def subscribe_to_events(event_types):
    """Подписка на несколько типов событий"""
    pubsub = redis_client.pubsub()
    for event_type in event_types:
        pubsub.subscribe(f"channel_{event_type}")
    return pubsub

def cache_user_reservations(user_id, reservations):
    """Кэширует резервации пользователя"""
    key = f"reservations:user:{user_id}"
    redis_client.setex(key, RESERVATION_CACHE_TTL, serialize_to_json(reservations))

def get_cached_user_reservations(user_id):
    """Получает кэшированные резервации пользователя"""
    key = f"reservations:user:{user_id}"
    data = redis_client.get(key)
    return deserialize_from_json(data) if data else None

def cache_coach_reservations(coach_id, reservations):
    """Кэширует резервации тренера"""
    key = f"reservations:coach:{coach_id}"
    redis_client.setex(key, RESERVATION_CACHE_TTL, serialize_to_json(reservations))

def get_cached_coach_reservations(coach_id):
    """Получает кэшированные резервации тренера"""
    key = f"reservations:coach:{coach_id}"
    data = redis_client.get(key)
    return deserialize_from_json(data) if data else None

def cache_all_reservations(reservations):
    """Кэширует все резервации"""
    key = "reservations:all"
    redis_client.setex(key, RESERVATION_CACHE_TTL, serialize_to_json(reservations))

def get_cached_all_reservations():
    """Получает все кэшированные резервации"""
    key = "reservations:all"
    data = redis_client.get(key)
    return deserialize_from_json(data) if data else None

def invalidate_reservation_cache(user_id=None, coach_id=None):
    """Инвалидирует кэш резерваций"""
    if user_id:
        redis_client.delete(f"reservations:user:{user_id}")
    if coach_id:
        redis_client.delete(f"reservations:coach:{coach_id}")
    redis_client.delete("reservations:all")

def publish_notification(event_type, data):
    """Публикует уведомление в Redis PubSub"""
    if event_type not in NOTIFICATION_CHANNELS:
        raise ValueError(f"Неизвестный тип события: {event_type}")
    
    channel = NOTIFICATION_CHANNELS[event_type]
    notification = {
        'type': event_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    redis_client.publish(channel, serialize_to_json(notification))
    return notification

def subscribe_to_notifications(event_types=None):
    """Подписывается на уведомления указанных типов"""
    if event_types is None:
        event_types = NOTIFICATION_CHANNELS.keys()
    
    channels = [NOTIFICATION_CHANNELS[event_type] for event_type in event_types]
    pubsub = redis_client.pubsub()
    for channel in channels:
        pubsub.subscribe(channel)
    return pubsub

def get_notification_handler():
    """Создает обработчик уведомлений"""
    def handle_notification(message):
        if message['type'] == 'message':
            try:
                notification = deserialize_from_json(message['data'])
                return notification
            except Exception as e:
                st.error(f"Ошибка при обработке уведомления: {e}")
        return None
    return handle_notification

# Функции для конкретных типов уведомлений
def notify_new_reservation(reservation_id, user_id, court_id, reservation_time, duration, coach_id=None):
    """Отправляет уведомление о новой резервации"""
    data = {
        'reservation_id': reservation_id,
        'user_id': user_id,
        'court_id': court_id,
        'reservation_time': reservation_time.isoformat(),
        'duration': duration,
        'coach_id': coach_id
    }
    return publish_notification('new_reservation', data)

def notify_cancel_reservation(reservation_id, user_id, court_id, coach_id=None):
    """Отправляет уведомление об отмене резервации"""
    data = {
        'reservation_id': reservation_id,
        'user_id': user_id,
        'court_id': court_id,
        'coach_id': coach_id
    }
    return publish_notification('cancel_reservation', data)

def notify_coach_assigned(reservation_id, coach_id, user_id):
    """Отправляет уведомление о назначении тренера"""
    data = {
        'reservation_id': reservation_id,
        'coach_id': coach_id,
        'user_id': user_id
    }
    return publish_notification('coach_assigned', data)

def notify_court_available(court_id, available_time):
    """Отправляет уведомление о доступности корта"""
    data = {
        'court_id': court_id,
        'available_time': available_time.isoformat()
    }
    return publish_notification('court_available', data)