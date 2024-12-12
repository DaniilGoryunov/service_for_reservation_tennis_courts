-- Вставка данных о теннисных кортах
INSERT INTO courts (surface, location) VALUES
('Грунт', 'Стадион 1'),
('Хард', 'Стадион 2'),
('Трава', 'Стадион 3');

-- Вставка данных о ценах на корты в зависимости от времени
INSERT INTO court_prices (court_id, start_time, end_time, price) VALUES
(1, '08:00:00', '12:00:00', 500.00),  -- Корт 1, цена с 8:00 до 12:00
(1, '12:00:00', '18:00:00', 700.00),  -- Корт 1, цена с 12:00 до 18:00
(2, '08:00:00', '12:00:00', 600.00),  -- Корт 2, цена с 8:00 до 12:00
(2, '12:00:00', '18:00:00', 800.00),  -- Корт 2, цена с 12:00 до 18:00
(3, '08:00:00', '12:00:00', 900.00),  -- Корт 3, цена с 8:00 до 12:00
(3, '12:00:00', '18:00:00', 1100.00); -- Корт 3, цена с 12:00 до 18:00

-- Вставка данных о тренерах
INSERT INTO coaches (name, price) VALUES
('Иван Иванов', 1000),
('Петр Петров', 1200),
('Сергей Сергеев', 1500);

-- Вставка данных о ценах на услуги тренеров
INSERT INTO coach_prices (coach_id, start_time, end_time, price) VALUES
(1, '08:00:00', '12:00:00', 1000.00),  -- Тренер 1, цена с 8:00 до 12:00
(1, '12:00:00', '18:00:00', 1200.00),  -- Тренер 1, цена с 12:00 до 18:00
(2, '08:00:00', '12:00:00', 800.00),   -- Тренер 2, цена с 8:00 до 12:00
(2, '12:00:00', '18:00:00', 900.00),   -- Тренер 2, цена с 12:00 до 18:00
(3, '08:00:00', '12:00:00', 1500.00),  -- Тренер 3, цена с 8:00 до 12:00
(3, '12:00:00', '18:00:00', 1700.00);  -- Тренер 3, цена с 12:00 до 18:00