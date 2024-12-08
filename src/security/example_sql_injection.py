import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv("env.env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


def get_sales(barcode):
    query = f"SELECT * FROM sales_details where barcode = '{barcode}'"

    with psycopg2.connect(**DB_CONFIG) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_sales_pro(barcode):
    query = "SELECT * FROM sales_details where barcode = %(barcode)s"

    with psycopg2.connect(**DB_CONFIG) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query, {"barcode": barcode})
            return cursor.fetchall()


if __name__ == "__main__":
    print(
        get_sales_pro(
            "123456789012' or 1=1; DROP TABLE suppliers_1; SELECT * FROM sales_details;--"
        )
    )


# SELECT * FROM Users WHERE UserId = 105 OR 1=1;

# SELECT * FROM Users WHERE Name ="John Doe" AND Pass ="myPass"

# SELECT * FROM Users WHERE Name ="" or ""="" AND Pass ="" or ""=""
