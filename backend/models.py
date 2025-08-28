# # backend/models.py
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from .database import Base  # <-- IMPORTANT

# class Chat(Base):
#     __tablename__ = "chats"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
#     title = Column(String(200), nullable=False)
#     modality = Column(String(20), nullable=False)  # "text" | "image" | "audio" | "video"
#     created_at = Column(DateTime, server_default=func.now(), nullable=False)

#     user = relationship("User", back_populates="chats")
#     messages = relationship("Message", back_populates="chat", cascade="all,delete")

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     email = Column(String(255), unique=True, nullable=False)
#     password_hash = Column(String(255), nullable=False)
#     chats = relationship("Chat", back_populates="user", cascade="all,delete")

# class Message(Base):
#     __tablename__ = "messages"
#     id = Column(Integer, primary_key=True)
#     chat_id = Column(Integer, ForeignKey("chats.id"), index=True, nullable=False)
#     role = Column(String(20), nullable=False)        # "user" | "assistant"
#     content = Column(Text, nullable=False)
#     media_type = Column(String(20), nullable=True)   # "image" | "audio" | "video" (optional)
#     media_path = Column(String(512), nullable=True)  # path under /media (optional)
#     created_at = Column(DateTime, server_default=func.now(), nullable=False)

#     chat = relationship("Chat", back_populates="messages")


from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    modality = Column(String(20), nullable=False)  # "text" | "image" | "audio" | "video"
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all,delete")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Optional profile fields
    name = Column(String(120), nullable=True)
    phone = Column(String(30), nullable=True)

    chats = relationship("Chat", back_populates="user", cascade="all,delete")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), index=True, nullable=False)
    role = Column(String(20), nullable=False)        # "user" | "assistant"
    content = Column(Text, nullable=False)
    media_type = Column(String(20), nullable=True)   # "image" | "audio" | "video" (optional)
    media_path = Column(String(512), nullable=True)  # path under /media (optional)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    chat = relationship("Chat", back_populates="messages")



