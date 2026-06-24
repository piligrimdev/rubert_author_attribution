from typing import List

from sqlalchemy import and_, or_

from ..abstract_crud_db_provider import AbstractCRUDDatabaseProvider
from sqlalchemy.orm import Session

from ...entities.author import Author
from ...entities.user import User


class AuthorCRUDDatabaseProvider(AbstractCRUDDatabaseProvider):
    model = Author

    async def get_by_name_part(
            self,
            name: str | None = None,
            surname: str | None = None,
            last_name: str | None = None,
            users: List[User] | None = None,
            session: Session = None
    ) -> Author:

        if not any([name, surname, last_name]):
            raise ValueError("name or surname or last_name must be provided")

        if users:
            whereclause = or_(
                Author.name == name,
                Author.surname == surname,
                Author.last_name == last_name,
                Author.provided_by_user.in_([u.id for u in users]),
            )
        else:
            whereclause = or_(
                Author.name == name,
                Author.surname == surname,
                Author.last_name == last_name,
            )

        return await self.select_where(
            whereclause,
            all=True,
            session=session
        )

    async def get_by_provided_user(
            self, user: User, session: Session = None
    ) -> Author:
        return await self.select_where(
            Author.provided_by_user == user.id,
            all=True,
            session=session
        )

    async def get_by_id(
            self, author_id, session: Session = None
    ) -> Author:
        return await self.select_where(
            Author.id == author_id,
            session=session
        )

    async def get_by_full_name(
            self,
            name: str,
            surname: str,
            last_name: str,
            users: List[User] | None = None,
            session: Session = None
    ) -> Author:
        if users:
            whereclause = and_(
                Author.name == name,
                Author.surname == surname,
                Author.last_name == last_name,
                Author.provided_by_user.in_([u.id for u in users]),
            )
        else:
            whereclause = and_(
                Author.name == name,
                Author.surname == surname,
                Author.last_name == last_name,
            )

        return await self.select_where(
            whereclause,
            session=session
        )

    async def list_all_available(
            self,
            users: list[User],
            session: Session = None
    ) -> Author:
        return await self.select_where(
            Author.provided_by_user.in_([u.id for u in users]),
            all=True,
            session=session
        )

    async def create(
            self,
            name: str,
            surname: str,
            last_name: str,
            user: User,
            session: Session = None
    ) -> Author:

        author = Author(
            name,
            surname,
            last_name,
            provided_by=user
        )

        session.add(author)
        session.commit()
        session.expunge(author)

        return author

