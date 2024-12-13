-- Таблица для хранения информации о теннисных кортам
CREATE TABLE courts (
    court_id SERIAL PRIMARY KEY,
    surface VARCHAR(50) NOT NULL, 
    location VARCHAR(100) NOT NULL
);

COMMENT ON TABLE courts IS 'Информация о теннисных кортах';

-- Таблица для хранения информации о пользователях
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(50) NOT NULL
);

COMMENT ON TABLE users IS 'Информация о пользователях';

-- Таблица для хранения цен на корты в зависимости от времени
CREATE TABLE court_prices (
    court_id INT REFERENCES courts(court_id),
    start_time TIME, 
    end_time TIME, 
    price DECIMAL(10, 2),
    PRIMARY KEY (court_id, start_time)
);

COMMENT ON TABLE court_prices IS 'Цены на теннисные корты в зависимости от времени';

-- Создание таблицы для хранения информации о тренерах
CREATE TABLE coaches (
    user_id INT REFERENCES users(user_id),
    coach_id SERIAL PRIMARY KEY,  
    name VARCHAR(100) NOT NULL,
    price INT
);

COMMENT ON TABLE coaches IS 'Информация о тренерах';

-- Создание таблицы для хранения цен на услуги тренеров
CREATE TABLE coach_prices (
    coach_id INT REFERENCES coaches(coach_id),
    start_time TIME,
    end_time TIME, 
    price DECIMAL(10, 2),
    PRIMARY KEY (coach_id, start_time)
);

COMMENT ON TABLE coach_prices IS 'Цены на услуги тренеров в зависимости от времени';

CREATE TABLE users_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

COMMENT ON TABLE users_roles IS 'Роли пользователей';

-- Таблица для хранения резерваций
CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    court_id INT REFERENCES courts(court_id) ON DELETE CASCADE,
    reservation_time TIMESTAMP NOT NULL,
    duration INT NOT NULL,
    coach_id INT REFERENCES coaches(coach_id) ON DELETE SET NULL
);

COMMENT ON TABLE reservations IS 'Информация о резервациях теннисных кортов';

-- Таблица для хранения отзывов пользователей
CREATE TABLE user_reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    court_id INT REFERENCES courts(court_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_reviews IS 'Отзывы пользователей о теннисных кортах';