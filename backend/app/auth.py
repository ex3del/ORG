"""
Модуль аутентификации FastAPI

Компоненты:
1. Хеширование паролей:
    - get_password_hash(password) -> str
    - verify_password(plain, hashed) -> bool

2. Работа с JWT-токенами:
    - create_access_token(data, expires_delta) -> str

3. Аутентификация:
    - get_current_user(token) -> User

Настройки:
- SECRET_KEY: Секретный ключ из переменных окружения
- ALGORITHM: Алгоритм подписи (HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES: Время жизни токена (30 мин)

Пример использования:
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas, database


# Password hashing settings
"""
Настройки хеширования паролей:
    - schemes: Используется схема bcrypt для хеширования
    - deprecated: Автоматическая обработка устаревших схем хеширования
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
"""
Настройки JWT-токенов:
    - SECRET_KEY: Секретный ключ для подписи токенов, получаемый из переменных окружения
    - ALGORITHM: Алгоритм шифрования (HS256)
    - ACCESS_TOKEN_EXPIRE_MINUTES: Время жизни токена в минутах (120)
"""
SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# OAuth2 scheme
"""
Схема OAuth2:
    - tokenUrl: URL для получения токена (/login)
    - Используется для извлечения и валидации токена из заголовка Authorization
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password: str) -> str:
    """
    Функция для хеширования паролей.

    Аргументы:
        password (str): Пароль в виде строки.

    Возвращает:
        str: Хешированный пароль.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Функция для проверки пароля.

    Аргументы:
        plain_password (str): Обычный пароль.
        hashed_password (str): Хешированный пароль.

    Возвращает:
        bool: True, если пароль совпадает, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Функция для создания JWT-токена.

    Аргументы:
        data (dict): Данные для включения в токен.
        expires_delta (Optional[timedelta]): Время жизни токена. Если не указано, используется значение по умолчанию.

    Возвращает:
        str: Сгенерированный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
) -> models.User:
    """
    Функция для получения текущего пользователя на основе токена.

    Аргументы:
        token (str): JWT-токен, извлеченный из заголовков.
        db (Session): Сессия базы данных.

    Возвращает:
        models.User: Объект пользователя из базы данных.

    Вызывает:
        HTTPException: Если токен недействителен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise credentials_exception
    return user


def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """
    Функция для проверки, является ли текущий пользователь администратором.

    Аргументы:
        current_user (models.User): Текущий пользователь, извлеченный из токена.

    Возвращает:
        models.User: Объект пользователя, если он администратор.

    Вызывает:
        HTTPException: Если пользователь не является администратором.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Not authorized to perform this action"
        )
    return current_user
