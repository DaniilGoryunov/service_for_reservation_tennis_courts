-- Таблица для хранения информации о теннисных кортах
CREATE TABLE IF NOT EXISTS courts (
    court_id SERIAL PRIMARY KEY,
    surface VARCHAR(100) NOT NULL
);

COMMENT ON TABLE courts IS 'Информация о теннисных кортах';

-- Таблица для хранения информации о пользователях
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'Информация о пользователях';

-- Таблица для хранения резерваций
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    court_id INT REFERENCES courts(court_id) ON DELETE CASCADE,
    reservation_time TIMESTAMP NOT NULL,
    duration INT NOT NULL  -- Продолжительность в минутах
);

COMMENT ON TABLE reservations IS 'Информация о резервациях теннисных кортов';

-- Таблица для хранения цен на корты в зависимости от времени
CREATE TABLE IF NOT EXISTS court_prices (
    price_id SERIAL PRIMARY KEY,
    court_id INT REFERENCES courts(court_id) ON DELETE CASCADE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    price NUMERIC NOT NULL
);

COMMENT ON TABLE court_prices IS 'Цены на теннисные корты в зависимости от времени';