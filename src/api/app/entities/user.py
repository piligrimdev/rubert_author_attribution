from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from ..database.mixins.with_id import WithIDMixin
from ..core import Base


class Role(Base, WithIDMixin):
    role_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def __init__(self, name: str):
        self.role_name = name

    def __str__(self) -> str:
        return self.role_name


class User(Base, WithIDMixin):
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship()

    def __init__(self, username, password_hash, role):
        self.username = username
        self.password_hash = password_hash

        self.role = role
        self.role_id = role.id

    def __str__(self) -> str:
        return self.username
