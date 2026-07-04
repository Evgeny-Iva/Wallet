from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from api.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment='Уникальный номер пользователя')
    first_name = Column(String, nullable=False, comment='Имя пользователя')
    last_name = Column(String, nullable=False, comment='Фамилия пользователя')
    middle_name = Column(String, nullable=True, comment='Отчество пользователя')
    email = Column(String, unique=True, index=True, nullable=False, comment='Электронная почта пользователя')
    created_at = Column(DateTime, server_default=func.now(), comment='Дата создания профиля')
    password_hash = Column(String, nullable=False, comment='Хеш пароля')

    wallets = relationship("Wallet", back_populates="user")