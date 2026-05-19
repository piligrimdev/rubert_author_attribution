from ..abstract_crud_db_provider import AbstractCRUDDatabaseProvider
from sqlalchemy.orm import Session

from ...entities.genre import Genre


class GenreCRUDDatabaseProvider(AbstractCRUDDatabaseProvider):
    model = Genre

    async def get_by_name(
            self,
            name: str,
            session: Session = None
    ) -> Genre:
        return await self.select_where(
            Genre.genre_name == name,
            session=session
        )

    async def create(
            self,
            name: str,
            session: Session = None
    ) -> Genre:
        genre_obj = Genre(genre_name=name)

        session.add(genre_obj)
        session.commit()
        session.expunge(genre_obj)

        return genre_obj
