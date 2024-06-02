import enum
from datetime import date

from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy import String, Integer, String, DateTime, func, Enum

# from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(50))
    birthday: Mapped[str] = mapped_column(String(10), nullable=True, default=None)
    addition: Mapped[str] = mapped_column(String(250), nullable=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(250))
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, onupdate=func.now(), nullable=True, default=None
    )
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=True
    )
