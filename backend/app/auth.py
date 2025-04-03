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
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas, database


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
) -> models.User:
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
