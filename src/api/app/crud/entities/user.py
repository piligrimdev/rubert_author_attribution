from ..abstract_crud_db_provider import AbstractCRUDDatabaseProvider
from sqlalchemy.orm import Session, joinedload

from ...entities.user import User, Role


class UserCRUDDatabaseProvider(AbstractCRUDDatabaseProvider):
    model = User

    async def get_by_username(
        self, username: str, session: Session = None
    ) -> User:
        return await self.select_where(
            User.username == username, session=session
        )

    async def get_by_id(
            self, user_id: str, session: Session = None
    ) -> User:
        return await self.select_where(
            User.id == user_id, session=session,
            options=joinedload(User.role)
        )

    async def raise_if_exists_with_username(
        self, username: str, session: Session = None
    ) -> None:
        ent = await self.raise_if_exists(User.username == username, session=session)

    async def create(
        self, username: str, password_hash: str, role: Role, session: Session = None
    ) -> User:
        user = User(
            username,
            password_hash,
            role
        )

        session.add(user)
        session.commit()
        session.expunge(user)

        return user

class RoleCRUDDatabaseProvider(AbstractCRUDDatabaseProvider):
    model = Role

    async def get_by_name(
        self, name: str, session: Session = None
    ) -> User:
        return await self.select_where(
            Role.role_name == name, session=session
        )
