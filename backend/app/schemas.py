"""
Pydantic схемы для системы аутентификации и управления пользователями.

Схемы:
    1. UserBase - Базовая схема пользователя:
        - Используется как родительский класс
        - Поля: username, email

    2. UserCreate - Схема для создания пользователя:
        - Наследует UserBase
        - Добавляет поле password
        - Используется в эндпоинте регистрации

    3. User - Схема ответа с данными пользователя:
        - Наследует UserBase
        - Добавляет id, is_active, is_approved
        - Поддерживает конвертацию из ORM (orm_mode = True)
        - Используется для возврата данных пользователя (без пароля)

    4. Token - Схема JWT токена:
        - Поля: access_token, token_type
        - Используется в эндпоинте логина

    5. TokenData - Схема данных из JWT токена:
        - Поле: username (опциональное)
        - Используется для извлечения данных из токена

Примеры использования:
    # Валидация данных при регистрации
    user_data = UserCreate(
        username="john_doe",
        email="john@example.com",
        password="secret"
    )

    # Возврат данных пользователя из API
    user_response = User(
        id=1,
        username="john_doe",
        email="john@example.com",
        is_active=True,
        is_approved=False
    )

    # Возврат токена
    token_response = Token(
        access_token="eyJhbGciOi...",
        token_type="bearer"
    )
"""

from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_approved: bool

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
