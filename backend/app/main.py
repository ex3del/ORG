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

from fastapi import FastAPI, Depends, HTTPException
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
        raise HTTPException(
            status_code=400, detail="Имя пользователя уже зарегистрировано"
        )
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
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
    """Аутентификация пользователя и возврат JWT-токена.

    Аргументы:
        form_data (OAuth2PasswordRequestForm): Данные формы входа
        db (Session): Зависимость сессии базы данных

    Возвращает:
        dict: Токен доступа и тип токена

    Вызывает:
        HTTPException: 401 при неверных учетных данных
    """
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
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
