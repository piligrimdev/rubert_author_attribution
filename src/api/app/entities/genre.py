from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..database.mixins.with_id import WithIDMixin
from ..core import Base


class Genre(Base, WithIDMixin):
    genre_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def __init__(self, genre_name: str):
        self.genre_name = genre_name

    def __str__(self) -> str:
        return self.genre_name