"""
Подключение к PostgreSQL через SQLAlchemy.
Читаю настройки из переменных окружения (.env прокидывается в контейнер).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Собираем строку подключения из переменных окружения.
# Пример: postgresql://cam_user:pass@db:5432/cam_db
DB_USER = os.getenv("POSTGRES_USER", "cam_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "cam_pass_2026")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "cam_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаём движок — он управляет пулом соединений.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Фабрика сессий — каждый запрос получает свою сессию.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Базовый класс для ORM-моделей.
Base = declarative_base()


def get_db():
    """
    Зависимость FastAPI: выдаёт сессию БД и закрывает её после запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
