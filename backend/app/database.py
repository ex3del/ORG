"""
Модуль конфигурации базы данных PostgreSQL.

Этот модуль предоставляет базовую настройку и подключение к PostgreSQL через SQLAlchemy.

Компоненты:
    1. Конфигурация подключения:
        - SQLALCHEMY_DATABASE_URL: URL подключения к PostgreSQL
        - engine: Движок SQLAlchemy для управления пулом подключений
        - SessionLocal: Фабрика сессий для создания изолированных сессий БД
        - Base: Базовый класс для ORM-моделей

    2. Управление сессиями:
        - get_db(): Генератор сессий для внедрения зависимостей
        - Автоматическое закрытие сессий после использования

Использование:
    1. Определение моделей:
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)

    2. Создание таблиц:
        Base.metadata.create_all(bind=engine)

    3. Работа с сессией:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users

Примечания:
    - Используйте контекст сессии для автоматического закрытия
    - Каждый запрос получает свою изолированную сессию
    - Транзакции автоматически откатываются при ошибках
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
