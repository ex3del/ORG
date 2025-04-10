"""
Документация приложения FastAPI

Этот модуль реализует систему аутентификации и управления пользователями со следующими функциями:
- Регистрация и вход пользователей
- Аутентификация на основе JWT-токенов
- Базовые операции управления пользователями
- Загрузка и управление документами
- Интеграция с SQLAlchemy для работы с базой данных

Конечные точки (Endpoints):
1. Корневая точка: Проверка работоспособности
2. Управление пользователями:
   - GET /users - Список всех пользователей
   - POST /register - Регистрация нового пользователя
   - POST /login - Аутентификация и получение JWT-токена
   - GET /users/me - Получение информации о текущем пользователе
   - POST /approve_user/{user_id} - Одобрение учетной записи пользователя
   - POST /disapprove_user/{user_id} - Отмена одобрения учетной записи пользователя
3. Управление документами:
   - POST /upload - Загрузка документа (PDF, ≤20MB, максимум 10 документов на пользователя)
   - GET /documents - Список всех документов текущего пользователя
   - DELETE /documents/{doc_id} - удаляет документ текущего пользователя

Модели:
- User: Хранит учетные данные и информацию о пользователях
- Document: Хранит информацию о загруженных документах
- ChatSession: (Импортируется, но не используется в этих конечных точках)
- Message: (Импортируется, но не используется в этих конечных точках)

Зависимости:
- SQLAlchemy для ORM
- Passlib для хэширования паролей
- PyJWT для работы с JWT-токенами
- Утилиты безопасности FastAPI
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
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
from typing import List, Optional
from datetime import datetime
import logging
import os
import shutil

UPLOAD_DIR = "/app/uploads"

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


@app.post("/disapprove_user/{user_id}", response_model=schemas.User)
def disapprove_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_current_admin_user),
):
    """
    POST /disapprove_user/{user_id}
    Отмена одобрения учетной записи пользователя администратором.

    Описание:
        Этот эндпоинт позволяет администратору отменить одобрение учетной записи пользователя.
        После отмены одобрения пользователь не сможет войти в систему.

    Аргументы:
        user_id (int): Идентификатор пользователя, для которого нужно отменить одобрение.
        db (Session): Сессия базы данных для выполнения запросов.
        admin_user (models.User): Аутентифицированный администратор, выполняющий запрос.

    Возвращает:
        models.User: Обновленный объект пользователя с отмененным флагом одобрения.

    Ошибки:
        HTTPException 404: Если пользователь с указанным идентификатором не найден.
        HTTPException 400: Если пользователь уже не одобрен или является администратором.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot disapprove admin users")
    if not user.is_approved:
        raise HTTPException(status_code=400, detail="User already not approved")

    user.is_approved = False
    db.commit()
    db.refresh(user)
    return user


@app.post("/upload", response_model=schemas.Document)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    POST /upload
    Загрузка документа для текущего пользователя.

    Описание:
        Этот эндпоинт позволяет аутентифицированному пользователю загружать PDF-документы.
        Максимальный размер файла: 20MB. Максимум 10 документов на пользователя.

    Аргументы:
        file (UploadFile): Загружаемый файл.
        db (Session): Сессия базы данных для выполнения запросов.
        current_user (models.User): Аутентифицированный пользователь из JWT-токена.

    Возвращает:
        models.Document: Объект загруженного документа.

    Ошибки:
        HTTPException 400: Если превышен лимит документов, размер файла превышает 20MB или файл не является PDF.
    """
    doc_count = (
        db.query(models.Document)
        .filter(models.Document.user_id == current_user.id)
        .count()
    )
    if doc_count >= 10:
        raise HTTPException(
            status_code=400, detail="Document limit reached (10 per user)"
        )

    if file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 20MB limit")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    user_dir = os.path.join(UPLOAD_DIR, f"user_{current_user.id}")
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = models.Document(
        user_id=current_user.id, file_name=file.filename, file_path=file_path
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@app.get("/documents", response_model=List[schemas.Document])
def list_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    GET /documents
    Получение списка всех документов текущего пользователя.

    Описание:
        Этот эндпоинт возвращает список всех загруженных документов для текущего аутентифицированного пользователя.

    Аргументы:
        db (Session): Сессия базы данных для выполнения запросов.
        current_user (models.User): Аутентифицированный пользователь из JWT-токена.

    Возвращает:
        List[models.Document]: Список объектов документов текущего пользователя.
    """
    documents = (
        db.query(models.Document)
        .filter(models.Document.user_id == current_user.id)
        .all()
    )
    return documents


@app.delete("/documents/{doc_id}", response_model=schemas.Document)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    DELETE /documents/{doc_id}
    Удаление документа текущего пользователя.

    Описание:
        Этот эндпоинт позволяет аутентифицированному пользователю удалить загруженный документ.
        Документ удаляется как из базы данных, так и из файловой системы.

    Аргументы:
        doc_id (int): Идентификатор документа, который нужно удалить.
        db (Session): Сессия базы данных для выполнения запросов.
        current_user (models.User): Аутентифицированный пользователь из JWT-токена.

    Возвращает:
        models.Document: Объект удаленного документа.

    Ошибки:
        HTTPException 404: Если документ не найден или не принадлежит текущему пользователю.
    """
    document = (
        db.query(models.Document)
        .filter(
            models.Document.id == doc_id, models.Document.user_id == current_user.id
        )
        .first()
    )
    if not document:
        raise HTTPException(
            status_code=404, detail="Document not found or not owned by user"
        )

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()
    return document


@app.post("/chat_sessions", response_model=schemas.ChatSession)
def create_chat_session(
    chat: schemas.ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Create a new chat session for the current user."""
    new_chat = models.ChatSession(
        user_id=current_user.id,
        session_name=chat.session_name,
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


@app.get("/chat_sessions", response_model=List[schemas.ChatSession])
def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get all chat sessions for the current user."""
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == current_user.id)
        .order_by(models.ChatSession.created_at.desc())
        .all()
    )


@app.patch("/chat_sessions/{session_id}", response_model=schemas.ChatSession)
def update_chat_session(
    session_id: int,
    update_data: schemas.ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Update a chat session's name."""
    chat = (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == current_user.id,
        )
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")

    chat.session_name = update_data.session_name
    db.commit()
    db.refresh(chat)
    return chat


@app.post("/chat_sessions/{session_id}/messages", response_model=schemas.Message)
def create_message(
    session_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Add a new message to a chat session."""
    chat = (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == current_user.id,
        )
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")

    new_message = models.Message(
        session_id=session_id,
        message_text=message.message_text,
        is_user=message.is_user,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@app.delete("/chat_sessions/{session_id}", response_model=schemas.ChatSession)
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Delete a chat session and all its messages."""
    chat = (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == current_user.id,
        )
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")

    db.delete(chat)
    db.commit()
    return chat


@app.get("/view/{file_path:path}")
async def view_document(
    file_path: str,
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    GET /view/{file_path}
    Stream a document file for viewing.

    Description:
        This endpoint allows an authenticated user to view their uploaded documents.
        It validates that the requested document belongs to the current user.

    Arguments:
        file_path (str): The path to the document file.
        current_user (models.User): The authenticated user from JWT token.

    Returns:
        FileResponse: The document file as a stream.

    Errors:
        HTTPException 404: If the document is not found or doesn't belong to the user.
    """
    # Convert the URL-encoded path back to a normal path
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    import os

    # Ensure the file exists and is within the user's directory
    user_dir = os.path.join(UPLOAD_DIR, f"user_{current_user.id}")
    full_path = os.path.join(UPLOAD_DIR, file_path)

    # Security check - ensure the file is within the user's directory
    if not os.path.commonprefix([os.path.abspath(full_path), user_dir]).startswith(
        user_dir
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(
        full_path, media_type="application/pdf", filename=os.path.basename(file_path)
    )
