from sqlmodel import create_engine, Session
import os

# Получаем строку подключения из переменных окружения или задаём по умолчанию
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/doctorbot"
)

engine = create_engine(DATABASE_URL, echo=True)

# Функция для получения сессии

def get_session():
    return Session(engine) 