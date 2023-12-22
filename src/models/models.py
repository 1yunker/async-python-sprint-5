from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, unique=True)
    hashed_password = Column(String(150), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    files = relationship('File', backref='user')


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(150), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    path = Column(String(255), nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, default=False)
