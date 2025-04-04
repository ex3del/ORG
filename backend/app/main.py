"""
Документация приложения FastAPI

Этот модуль реализует систему аутентификации и управления пользователями со следующими функциями:
- Регистрация и вход пользователей
- Аутентификация на основе JWT-токенов
- Базовые операции управления пользователями
- Интеграция с SQLAlchemy для работы с базой данных

Конечные точки (Endpoints):
1. Корневая точка: Проверка работоспособности
2. Управление пользователями:
   - GET /users - Список всех пользователей
   - POST /register - Регистрация нового пользователя
   - POST /login - Аутентификация и получение JWT-токена
   - GET /users/me - Получение информации о текущем пользователе

Модели:
- User: Хранит учетные данные и информацию о пользователях
- Document: (Импортируется, но не используется в этих конечных точках)
- ChatSession: (Импортируется, но не используется в этих конечных точках)
- Message: (Импортируется, но не используется в этих конечных точках)

Зависимости:
- SQLAlchemy для ORM
- Passlib для хэширования паролей
- PyJWT для работы с JWT-токенами
- Утилиты безопасности FastAPI
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .database import engine, Base, get_db
from .models import (
    User,
    Document,
    ChatSession,
    Message,
)
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание всех таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    """Точка проверки работоспособности.

    Возвращает:
        dict: Простое приветственное сообщение
    """
    return {"message": "Hello, World!"}


@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    """Получить список всех зарегистрированных пользователей.

    Аргументы:
        db (Session): Зависимость сессии базы данных

    Возвращает:
        List[User]: Все пользователи в базе данных
    """
    users = db.query(User).all()
    return users


@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Регистрация нового пользователя.

    Аргументы:
        user (schemas.UserCreate): Данные для создания пользователя
        db (Session): Зависимость сессии базы данных

    Возвращает:
        models.User: Созданный объект пользователя

    Вызывает:
        HTTPException: 400 если имя пользователя или email уже существуют
    """
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    """
    POST /login
    Аутентификация пользователя и возврат JWT-токена.

    Описание:
        Этот эндпоинт позволяет пользователю войти в систему, предоставив свои учетные данные.
        Если учетные данные корректны и пользователь одобрен, возвращается JWT-токен.

    Аргументы:
        form_data (OAuth2PasswordRequestForm): Данные формы входа (имя пользователя и пароль).
        db (Session): Сессия базы данных для выполнения запросов.

    Возвращает:
        dict: Словарь с токеном доступа и типом токена.

    Ошибки:
        HTTPException 401: Если имя пользователя или пароль неверны.
        HTTPException 403: Если учетная запись пользователя ожидает одобрения.
    """
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    if not user:
        logger.info(f"Login failed: User {form_data.username} not found")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_approved:
        logger.info(f"Login failed: User {form_data.username} not approved")
        raise HTTPException(
            status_code=403,
            detail="Account pending approval",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth.verify_password(form_data.password, user.hashed_password):
        logger.info(f"Login failed: Incorrect password for {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    logger.info(f"Login successful for {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """Получение информации о текущем аутентифицированном пользователе.

    Аргументы:
        current_user (models.User): Аутентифицированный пользователь из JWT-токена

    Возвращает:
        models.User: Данные аутентифицированного пользователя
    """
    return current_user


@app.post("/approve_user/{user_id}", response_model=schemas.User)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_current_admin_user),
):
    """
    POST /approve_user/{user_id}
    Одобрение учетной записи пользователя администратором.

    Описание:
        Этот эндпоинт позволяет администратору одобрить учетную запись пользователя.
        После одобрения пользователь сможет войти в систему.

    Аргументы:
        user_id (int): Идентификатор пользователя, которого нужно одобрить.
        db (Session): Сессия базы данных для выполнения запросов.
        admin_user (models.User): Аутентифицированный администратор, выполняющий запрос.

    Возвращает:
        models.User: Обновленный объект пользователя с установленным флагом одобрения.

    Ошибки:
        HTTPException 404: Если пользователь с указанным идентификатором не найден.
        HTTPException 400: Если пользователь уже одобрен.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_approved:
        raise HTTPException(status_code=400, detail="User already approved")

    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user
