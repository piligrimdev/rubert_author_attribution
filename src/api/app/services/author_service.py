from typing import List

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import and_
from starlette.status import HTTP_400_BAD_REQUEST

from ..crud.abstract_crud_db_provider import AlreadyExistsInDB, NotFoundInDB
from ..crud.entities.author import AuthorCRUDDatabaseProvider
from ..entities import User, Author

from ..schemas.requests import CreateAuthorForm, GetAuthorForm


class AuthorService:
    def __init__(
            self,
            author_crud: AuthorCRUDDatabaseProvider,
            user_service,
    ):
        self.crud = author_crud
        self.user_service = user_service

    async def get_or_create_entity(
        self,
        name: str,
        surname: str,
        last_name: str,
        user_id,
        session,
    ) -> Author:
        # вернет orm, а не схему, чтобы далее работать с бд
        try:
            return await self.crud.get_by_full_name(
                name, surname, last_name, session=session
            )
        except NotFoundInDB:
            user = await self.user_service.get_user_by_id(user_id, session=session)
            return await self.crud.create(
                name, surname, last_name, user, session
            )
        
    async def _get_admins_and_requester(self, user_id, session) -> List[User]:
        admin_users = await self.user_service.get_admin_users(session=session)
        user = await self.user_service.get_user_by_id(user_id, session=session)
        admin_users.append(user)
        return admin_users


    async def create(
        self, form: CreateAuthorForm, user_id, session
    ) -> GetAuthorForm:
        """
        """
        try:
            await self.crud.raise_if_exists(
                and_(
                    Author.name == form.name,
                    Author.surname == form.surname,
                    Author.last_name == form.last_name,
                ),
                session=session,
            )
        except AlreadyExistsInDB:
            raise HTTPException(400, "Author with specified name, surname and last name already exists")


        user = await self.user_service.get_user_by_id(user_id, session=session)

        created_author = await self.crud.create(
            form.name,
            form.surname,
            form.last_name,
            user,
            session,
        )

        provided_id = user.id if not await self.user_service.is_user_admin(user) else None

        return GetAuthorForm(
            name=created_author.name,
            surname=created_author.surname,
            last_name=created_author.last_name,
            description=created_author.description,
            provided_by=provided_id,
            id=created_author.id,
        )

    async def list_available(self, user_id, session):

        user = await self.user_service.get_user_by_id(user_id, session=session)

        if await self.user_service.is_user_admin(user):
            data = await self.crud.list_all(session)
        else:
            admin_users = await self._get_admins_and_requester(user_id, session)
            data = await self.crud.list_all_available(admin_users, session=session)

        result = []

        for author in data:
            # todo make eager join request

            prov_user =  await self.user_service.get_user_by_id(author.provided_by_user, session=session)
            provided_id = prov_user.id\
                if not await self.user_service.is_user_admin(prov_user) \
                else None
            result.append(
                GetAuthorForm(
                    name=author.name,
                    surname=author.surname,
                    last_name=author.last_name,
                    description=author.description,
                    provided_by=provided_id,
                    id=author.id,
                )
            )
        return result

    async def list_generative_enabled(self, user_id, session):
        """Authors whose style can be used for text generation (subset of list_available)."""
        return await self.list_available(user_id=user_id, session=session)

    async def get_by_full_name(self, form: GetAuthorForm, user_id, session):
        admin_users = await self._get_admins_and_requester(user_id, session)


        return await self.crud.get_by_full_name(
            form.name,
            form.surname,
            form.last_name,
            admin_users,
            session=session
        )

    async def get_by_part_name(self, form: GetAuthorForm, user_id, session):

        if not any([form.name, form.surname, form.last_name]):
            raise ValueError("name or surname or last_name must be provided")

        admin_users = await self._get_admins_and_requester(user_id, session)

        return await self.crud.get_by_name_part(
            form.name,
            form.surname,
            form.last_name,
            admin_users,
            session=session
        )

    async def get_by_provided_user(self, user_id, session):
        user = await self.user_service.get_user_by_id(user_id, session=session)

        return await self.crud.get_by_provided_user(
            user,
            session=session
        )