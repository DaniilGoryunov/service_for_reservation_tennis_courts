-- Вставка данных о теннисных кортах
INSERT INTO courts (court_id, surface) VALUES
    ('1', 'хард'),
    ('2', 'xард'),
    ('3', 'хард'),
    ('4', 'грунт'),
    ('5', 'грунт'),
    ('6', 'грунт');

-- Вставка данных о ценах на корты в зависимости от времени
INSERT INTO court_prices (court_id, start_time, end_time, price) VALUES
    (1, '08:00:00', '12:00:00', 500.0),
    (1, '12:00:00', '18:00:00', 600.0),
    (1, '18:00:00', '22:00:00', 700.0),
    (2, '08:00:00', '12:00:00', 550.0),
    (2, '12:00:00', '18:00:00', 650.0),
    (2, '18:00:00', '22:00:00', 750.0),
    (3, '08:00:00', '12:00:00', 600.0),
    (3, '12:00:00', '18:00:00', 700.0),
    (3, '18:00:00', '22:00:00', 800.0),
    (4, '08:00:00', '12:00:00', 500.0),
    (4, '12:00:00', '18:00:00', 600.0),
    (4, '18:00:00', '22:00:00', 700.0),
    (5, '08:00:00', '12:00:00', 550.0),
    (5, '12:00:00', '18:00:00', 650.0),
    (5, '18:00:00', '22:00:00', 750.0),
    (6, '08:00:00', '12:00:00', 600.0),
    (6, '12:00:00', '18:00:00', 700.0),
    (6, '18:00:00', '22:00:00', 800.0);
