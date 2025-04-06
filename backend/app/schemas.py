"""
Pydantic схемы для системы аутентификации и управления пользователями.

Схемы:
    1. DocumentBase - Базовая схема документа:
        - Поля: file_name
        - Используется как родительский класс для других схем документов

    2. DocumentCreate - Схема для создания документа:
        - Наследует DocumentBase
        - Используется для передачи данных при создании документа

    3. Document - Схема ответа с данными документа:
        - Наследует DocumentBase
        - Добавляет id, uploaded_at
        - Поддерживает конвертацию из ORM (orm_mode = True)
        - Используется для возврата данных о документе

    4. UserBase - Базовая схема пользователя:
        - Поля: username, email
        - Используется как родительский класс для других схем пользователей

    5. UserCreate - Схема для создания пользователя:
        - Наследует UserBase
        - Добавляет поле password
        - Используется в эндпоинте регистрации

    6. User - Схема ответа с данными пользователя:
        - Наследует UserBase
        - Добавляет id, is_active, is_approved
        - Поддерживает конвертацию из ORM (orm_mode = True)
        - Используется для возврата данных пользователя (без пароля)

    7. Token - Схема JWT токена:
        - Поля: access_token, token_type
        - Используется в эндпоинте логина

    8. TokenData - Схема данных из JWT токена:
        - Поле: username (опциональное)
        - Используется для извлечения данных из токена
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    file_name: str


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_approved: bool
    is_admin: bool

    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy models


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
