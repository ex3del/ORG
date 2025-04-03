"""
Модуль для настройки подключения к базе данных через SQLAlchemy.

Компоненты:
    - SQLALCHEMY_DATABASE_URL: URL подключения к БД
    - engine: Движок SQLAlchemy для управления подключениями
    - SessionLocal: Фабрика для создания сессий БД
    - Base: Базовый класс для ORM-моделей
    - get_db(): Генератор сессий для dependency injection

Пример использования:
    # Создание модели
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    # Создание таблиц
    Base.metadata.create_all(bind=engine)

    # Работа с сессией
    db = next(get_db())
    new_user = User(name="John")
    db.add(new_user)
    db.commit()
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@db:5432/mydatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
