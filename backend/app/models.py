"""
Модуль ORM-моделей для системы управления пользователями, документами и чат-сессиями.

Модели:
    - User: Модель пользователя системы
    - Document: Модель загруженных документов
    - ChatSession: Модель чат-сессий пользователя
    - Message: Модель сообщений в чат-сессиях

Пример использования:
    # Создание нового пользователя
    new_user = User(
        username="john_doe",
        email="john@example.com",
        hashed_password="hashed_password_here"
    )

    # Добавление документа для пользователя
    user_document = Document(
        user_id=new_user.id,
        file_name="report.pdf",
        file_path="/uploads/report.pdf"
    )

    # Создание чат-сессии
    chat_session = ChatSession(
        user_id=new_user.id,
        session_name="Technical Support"
    )

    # Добавление сообщения в сессию
    message = Message(
        session_id=chat_session.id,
        message_text="Hello, I need help",
        is_user=True
    )
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class User(Base):
    """
    Класс User представляет пользователя системы.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Уникальное имя пользователя.
        email (str): Уникальный адрес электронной почты пользователя.
        hashed_password (str): Хешированный пароль пользователя.
        is_active (bool): Флаг активности пользователя (по умолчанию True).
        is_approved (bool): Флаг одобрения учетной записи (по умолчанию False).
        created_at (datetime): Дата и время создания учетной записи.
        is_admin (bool): Флаг, указывающий, является ли пользователь администратором (по умолчанию False).
        documents (relationship): Связь с документами пользователя.
        chat_sessions (relationship): Связь с чат-сессиями пользователя.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions = relationship("ChatSession", back_populates="user")


class Document(Base):
    """
    Класс Document представляет загруженные документы пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор документа.
        user_id (int): Идентификатор пользователя, загрузившего документ.
        file_name (str): Имя файла документа.
        file_path (str): Путь к файлу документа.
        uploaded_at (datetime): Дата и время загрузки документа.
        user (relationship): Связь с пользователем, загрузившим документ.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")


class ChatSession(Base):
    """
    Класс ChatSession представляет чат-сессии пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор чат-сессии.
        user_id (int): Идентификатор пользователя, создавшего чат-сессию.
        session_name (str): Название чат-сессии.
        created_at (datetime): Дата и время создания чат-сессии.
        user (relationship): Связь с пользователем, создавшим чат-сессию.
        messages (relationship): Связь с сообщениями в чат-сессии.
    """

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.timestamp",
    )


class Message(Base):
    """
    Класс Message представляет сообщения в чат-сессиях.

    Атрибуты:
        id (int): Уникальный идентификатор сообщения.
        session_id (int): Идентификатор чат-сессии, к которой относится сообщение.
        message_text (str): Текст сообщения.
        timestamp (datetime): Дата и время отправки сообщения.
        is_user (bool): Флаг, указывающий, является ли сообщение пользовательским (True) или ботом (False).
        session (relationship): Связь с чат-сессией, к которой относится сообщение.
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    message_text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_user = Column(Boolean)  # True if user message, False if bot

    session = relationship("ChatSession", back_populates="messages")
