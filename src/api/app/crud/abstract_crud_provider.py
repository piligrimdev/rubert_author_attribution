from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session

from ..database.base import Base

# Type variable for generic CRUD provider
T = TypeVar("T", bound=Base)


class AbstractCRUDProvider(Generic[T], ABC):
    """
    Generic  CRUD provider that handles database operations.
    """

    model: Type[T]

    @abstractmethod
    async def raise_if_exists(
        self, *whereclause: ColumnElement[bool], session: Session
    ) -> None:
        """
        Check if a record matching the whereclause exists.

        Returns:
            None if exists
        Raises:
            AlreadyExistsInDB:
                If the record exists (when used in creation flows)
        """
        pass

    @abstractmethod
    async def list_all(self, session: Session) -> list[T]:
        """
        Lists all records of specific class.

        Returns:
           List of objects of type `model`
        """
        pass

    @abstractmethod
    async def delete(self, deleting_object: T, session: Session) -> None:
        pass

    @abstractmethod
    async def create(self, form: BaseModel, session: Session = None) -> T:
        pass
