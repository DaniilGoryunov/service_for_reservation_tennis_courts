-- Таблица для хранения информации о продуктах
CREATE TABLE products (
    barcode VARCHAR(20) PRIMARY KEY,
    name VARCHAR(512),
    package_size VARCHAR(50),
    weight NUMERIC
);

COMMENT ON TABLE products IS 'Информация о продуктах';

COMMENT ON COLUMN products.name IS 'Название продукта';

COMMENT ON COLUMN products.barcode IS 'Уникальный штрихкод продукта';

COMMENT ON COLUMN products.package_size IS 'Размер упаковки продукта';

COMMENT ON COLUMN products.weight IS 'Вес продукта';

-- Таблица для хранения информации о поставщиках
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255)
);

COMMENT ON TABLE suppliers IS 'Информация о поставщиках';

COMMENT ON COLUMN suppliers.supplier_id IS 'Уникальный идентификатор поставщика';

COMMENT ON COLUMN suppliers.name IS 'Имя поставщика';

COMMENT ON COLUMN suppliers.phone IS 'Телефон поставщика';

COMMENT ON COLUMN suppliers.address IS 'Адрес поставщика';

-- Таблица для регистрации привозов продуктов
CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    delivery_date DATE NOT NULL
);

COMMENT ON TABLE deliveries IS 'Данные о привозах продуктов';

COMMENT ON COLUMN deliveries.delivery_id IS 'Уникальный идентификатор поставки';

COMMENT ON COLUMN deliveries.supplier_id IS 'Идентификатор поставщика';

COMMENT ON COLUMN deliveries.delivery_date IS 'Дата привоза';

-- Таблица для хранения состава каждой поставки
CREATE TABLE delivery_contents (
    delivery_content_id SERIAL PRIMARY KEY,
    delivery_id INT REFERENCES deliveries(delivery_id) ON DELETE CASCADE,
    barcode VARCHAR(20) REFERENCES products(barcode) ON DELETE CASCADE,
    quantity INT NOT NULL
);

COMMENT ON TABLE delivery_contents IS 'Состав поставки продуктов';

COMMENT ON COLUMN delivery_contents.delivery_content_id IS 'Уникальный идентификатор строки поставки';

COMMENT ON COLUMN delivery_contents.delivery_id IS 'Идентификатор поставки';

COMMENT ON COLUMN delivery_contents.barcode IS 'Штрихкод продукта';

COMMENT ON COLUMN delivery_contents.quantity IS 'Количество продукта в поставке';

-- Таблица для хранения основной информации о продаже
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL
);

COMMENT ON TABLE sales IS 'Основная информация о продажах';

COMMENT ON COLUMN sales.sale_id IS 'Уникальный идентификатор покупки';

COMMENT ON COLUMN sales.sale_date IS 'Дата продажи';

-- Таблица для хранения информации о проданных продуктах в рамках каждой покупки
CREATE TABLE sales_details (
    sale_id INT REFERENCES sales(sale_id) ON DELETE CASCADE,
    barcode VARCHAR(20) REFERENCES products(barcode) ON DELETE CASCADE,
    quantity INT NOT NULL
);

COMMENT ON TABLE sales_details IS 'Информация о проданных продуктах в рамках покупки';

COMMENT ON COLUMN sales_details.sale_id IS 'Идентификатор покупки';

COMMENT ON COLUMN sales_details.barcode IS 'Штрихкод проданного продукта';

COMMENT ON COLUMN sales_details.quantity IS 'Количество проданного продукта';

-- Таблица для хранения цен на продукты
CREATE TABLE prices (
    price_id SERIAL PRIMARY KEY,
    barcode VARCHAR(20) REFERENCES products(barcode) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE,
    price NUMERIC NOT NULL
);

COMMENT ON TABLE prices IS 'Цены на продукты';

COMMENT ON COLUMN prices.price_id IS 'Уникальный идентификатор записи цены';

COMMENT ON COLUMN prices.barcode IS 'Штрихкод продукта';

COMMENT ON COLUMN prices.start_date IS 'Дата начала действия цены';

COMMENT ON COLUMN prices.end_date IS 'Дата окончания действия цены (NULL, если цена актуальна)';

COMMENT ON COLUMN prices.price IS 'Цена продукта';

-- Таблица для хранения информации о пользователях

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
);

COMMENT ON TABLE users IS 'Информация о пользователях';

COMMENT ON COLUMN users.user_id IS 'Уникальный идентификатор пользователя';

COMMENT ON COLUMN users.username IS 'Имя пользователя';

COMMENT ON COLUMN users.password_hash IS 'Хешированный пароль пользователя';

COMMENT ON COLUMN users.created_at IS 'Дата и время создания пользователя';

CREATE VIEW v_warehouse_state AS
SELECT
    p.barcode,
    COALESCE(SUM(dc.quantity), 0) - COALESCE(SUM(sd.quantity), 0) AS stock_quantity
FROM
    products p
    LEFT JOIN delivery_contents dc ON p.barcode = dc.barcode
    LEFT JOIN sales_details sd ON p.barcode = sd.barcode
GROUP BY
    p.barcode;

COMMENT ON VIEW v_warehouse_state IS 'Текущее состояние склада, основанное на привозах и продажах';

CREATE VIEW v_sales_statistics AS
SELECT
    s.sale_date,
    sd.barcode,
    SUM(sd.quantity * p.price) AS revenue,
    SUM(sd.quantity) AS quantity
FROM
    sales s
    JOIN sales_details sd ON s.sale_id = sd.sale_id
    JOIN prices p ON sd.barcode = p.barcode
WHERE
    s.sale_date BETWEEN p.start_date
    AND COALESCE(p.end_date, '5999-12-31' :: date)
GROUP BY
    s.sale_date,
    sd.barcode;

COMMENT ON VIEW v_sales_statistics IS 'Агрегированная статистика по продажам, сгруппированная по дням с расчетом суммы на основе текущих цен';