import uuid

from ..database.mixins.with_id import WithIDMixin

from ..core import Base

from sqlalchemy import Enum, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Author(Base, WithIDMixin):

    name: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    surname: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    last_name: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    provided_by_user: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=True)
    provided_by: Mapped["User"] = relationship()

    def __init__(self, name, surname, last_name, provided_by):

        self.name = name
        self.surname = surname
        self.last_name = last_name

        self.provided_by = provided_by
        self.provided_by_user = provided_by.id


    def __str__(self) -> str:
        return f"{self.surname} {self.name} {self.last_name}"
