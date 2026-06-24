from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.sql._typing import _ColumnExpressionArgument


from .abstract_crud_provider import AbstractCRUDProvider, T

class NotFoundInDB(Exception):
    def __init__(
        self, whereclause: _ColumnExpressionArgument[bool], class_name: str
    ):
        super().__init__(
            f"Not found {class_name} in database where ({whereclause})"
        )

class AlreadyExistsInDB(Exception):
    def __init__(
        self, whereclause: _ColumnExpressionArgument[bool], class_name: str
    ):
        super().__init__(
            f"Already exists {class_name}"
            f" item in database where ({whereclause})"
        )

class AbstractCRUDDatabaseProvider(AbstractCRUDProvider):
    """
    Generic  CRUD provider that handles database operations.
    """

    async def select_where(
        self,
        *whereclause: ColumnElement[bool],
        all: bool = False,  # noqa
        options: ExecutableOption | None = None,
        session: Session = None,
    ) -> T | list[T]:
        """
        Query the database with the given where clause.

        Args:
            *whereclause: SQLAlchemy filter conditions
            all: If True, return all matching records;
                if False, return first match
            options:
                Optional SQLAlchemy query
                options (like joinedload, selectinload)
            session: Database session

        Returns:
            Single model instance or list of instances

        Raises:
            NotFoundInDB: If no matching record is found
        """
        stmt = select(self.model).where(*whereclause)

        if options is not None:
            stmt = stmt.options(options)

        # result = await session.scalars(stmt) may use async later?
        result = session.scalars(stmt)

        if all:
            items = result.all()
            # Expunge to detach from session so they can be returned safely
            for item in items:
                session.expunge(item)
            return items
        else:
            item = result.first()

            if item is None:
                raise NotFoundInDB(*whereclause, self.model.__name__)

            # Expunge to detach from session
            session.expunge(item)
            return item

    async def raise_if_exists(
        self, *whereclause: ColumnElement[bool], session: Session
    ) -> None:
        """
        Check if a record matching the whereclause exists.

        Returns:
            None if exists
        Raises:
            AlreadyExistsInDB: If the record exists
             (when used in creation flows)
        """
        try:
            await self.select_where(*whereclause, session=session)
        except NotFoundInDB:
            pass
        else:
            raise AlreadyExistsInDB(*whereclause, self.model.__name__)

    async def list_all(self, session: Session) -> list[T]:
        return await self.select_where(all=True, session=session)

    async def delete(self, deleting_object: T, session: Session) -> None:
        session.delete(deleting_object)
        session.commit()

    async def create(self, form: BaseModel, session: Session = None) -> T:
        created_obj = self.model(form)

        session.add(created_obj)
        session.commit()

        return created_obj

    async def update(
            self,
            entity,
            updates: dict,
            session: Session,
    ) -> T:
        # # stmt = select(self.model).where(self.model.id == entity_id)
        # #
        # # result = session.scalars(stmt)
        # # obj = result.first()
        #
        # obj = session.get(self.model, entity_id)

        entity = session.merge(entity)

        for field, value in updates.items():
            setattr(entity, field, value)

        session.commit()
        session.refresh(entity)
        session.expunge(entity)
        return entity
