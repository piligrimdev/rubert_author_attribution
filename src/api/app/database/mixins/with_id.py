from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy import Uuid

class WithIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        unique=True,
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
    )
