import os
import subprocess
from datetime import datetime
import streamlit as st


def create_backup():

    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    BACKUP_DIR = "backup"

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_backup_{timestamp}.sql")

    os.environ['PGPASSWORD'] = DB_PASS

    try:
        subprocess.run(
            ["pg_dump", "-h", DB_HOST, "-U", DB_USER, "-F", "c", "-b", "-f", backup_file, DB_NAME],
            check=True
        )
        st.success(f"Резервная копия создана: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        st.error(f"Ошибка при создании резервной копии: {e}")
        return None
    finally:
        os.environ.pop('PGPASSWORD', None)


def restore_backup(backup_file):
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")

    if not os.path.exists(backup_file):
        st.error("Файл резервной копии не найден!")
        return

    os.environ['PGPASSWORD'] = DB_PASS

    try:
        subprocess.run(
            ["pg_restore", "-h", DB_HOST, "-U", DB_USER, "-d", DB_NAME, "-c", backup_file],
            check=True
        )
        st.success(f"База данных восстановлена из: {backup_file}")
    except subprocess.CalledProcessError as e:
        st.error(f"Ошибка при восстановлении базы данных: {e}")
    finally:
        os.environ.pop('PGPASSWORD', None)


def backup_controller():
    st.subheader("Управление резервными копиями")
    if st.button("Создать резервную копию"):
        create_backup()
