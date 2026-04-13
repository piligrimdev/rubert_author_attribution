from typing import List

from ..crud.entities.user import UserCRUDDatabaseProvider, RoleCRUDDatabaseProvider
from ..entities.user import User

from ..schemas.requests import RegisterForm, LoginForm

from ..utils.auth import hash_password, check_password, create_access_token, create_refresh_token


class UserService:
    def __init__(
            self,
            crud: UserCRUDDatabaseProvider,
            role_crud: RoleCRUDDatabaseProvider,
            basic_role_name: str,
            admin_role_name: str,
    ):
        self.crud = crud
        self.role_crud = role_crud
        self.basic_role_name = basic_role_name
        self.admin_role_name = admin_role_name

    async def register(self, form: RegisterForm, session) -> tuple[str, str]:
        await self.crud.raise_if_exists_with_username(form.username, session=session)

        basic_role = await self.role_crud.get_by_name(self.basic_role_name, session=session)

        hashed_password = hash_password(form.password)

        user = await self.crud.create(
            form.username,
            hashed_password,
            basic_role,
            session=session,
        )

        return create_access_token(user.id), create_refresh_token(user.id)

    async def login(self, form: LoginForm, session) -> tuple[str, str]:
        try:
            user = await self.crud.get_by_username(form.username, session=session)
        except ValueError:
            raise ValueError("Invalid username or password")

        try:
            check_password(form.password, user.password_hash)
        except ValueError:
            raise ValueError("Invalid username or password")

        return create_access_token(user.id), create_refresh_token(user.id)

    async def get_admin_users(self, session) -> List[User]:
        admin_role = await self.role_crud.get_by_name(self.admin_role_name, session=session)

        return await self.crud.select_where(
            User.role_id == admin_role.id,
            all=True,
            session=session,
        )

    async def get_user_by_id(self, user_id, session) -> User:
        return await self.crud.get_by_id(user_id, session=session)

    async def is_user_admin(self, user: User) -> bool:
        return user.role.role_name == self.admin_role_name
