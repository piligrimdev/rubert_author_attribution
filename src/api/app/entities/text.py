from ..database.mixins.with_id import WithIDMixin

from ..core.database import Base
from .genre import Genre
from .author import Author
from .user import User


from sqlalchemy import Enum, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import VECTOR
import uuid

class Text(Base, WithIDMixin):
    text: Mapped[str] = mapped_column(String, unique=False, nullable=False)

    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("author.id"))
    author: Mapped["Author"] = relationship()

    genre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("genre.id"))
    genre: Mapped["Genre"] = relationship()

    provided_by_user: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    provided_by: Mapped["User"] = relationship()

    is_visible: Mapped[bool] = mapped_column(Boolean, unique=False, nullable=False, default=False)

    embedding: Mapped[list] = mapped_column(VECTOR(256))

    def __init__(self, text: str, author: Author, genre: Genre, provided_by_user: User, embedding):
        self.text = text

        self.author = author
        self.genre = genre
        self.provided_by = provided_by_user

        self.embedding = embedding

        self.author_id = author.id
        self.genre_id = genre.id
        self.provided_by_user = provided_by_user.id
