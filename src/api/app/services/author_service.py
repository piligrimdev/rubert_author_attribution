from typing import List
import structlog
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import and_
from starlette.status import HTTP_400_BAD_REQUEST

from ..crud.abstract_crud_db_provider import AlreadyExistsInDB, NotFoundInDB
from ..crud.entities.author import AuthorCRUDDatabaseProvider
from ..entities import User, Author

from ..schemas.requests import CreateAuthorForm, GetAuthorForm, EditAuthorForm
from ..schemas.responses import AuthorEditResponse

logger = structlog.get_logger(__name__)

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
            logger.debug("authors.create_entity.not_found", name=name, surname=surname,
                        last_name=last_name)
            user = await self.user_service.get_user_by_id(user_id, session=session)
            result =  await self.crud.create(
                name, surname, last_name, user, session
            )
            logger.info("authors.create_entity.created_object", name=name, surname=surname,
                        last_name=last_name, user_id=user_id)
            return result
        
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
            logger.error("authors.create.author_already_exists", name=form.name, surname=form.surname, last_name=form.last_name)
            raise HTTPException(400, "Author with specified name, surname and last name already exists")


        user = await self.user_service.get_user_by_id(user_id, session=session)

        created_author = await self.crud.create(
            form.name,
            form.surname,
            form.last_name,
            user,
            session,
        )
        logger.info("authors.create.created_object", name=form.name, surname=form.surname,
                     last_name=form.last_name)

        provided_id = user.id if not await self.user_service.is_user_admin(user) else None

        logger.debug("authors.create.provided_id", provided_id=provided_id)

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
            logger.debug("authors.list_available.user_is_admin", user_id=user_id)
        else:
            admin_users = await self._get_admins_and_requester(user_id, session)
            data = await self.crud.list_all_available(admin_users, session=session)
            logger.debug("authors.list_available.user_is_not_admin", user_id=user_id)

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
        logger.warning("authors.list_generative_enabled.not_implemented_method_call", user_id=user_id)
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

    async def get_by_full_name(self, name: str, surname: str, last_name: str, user_id, session):
        admin_users = await self._get_admins_and_requester(user_id, session)


        return await self.crud.get_by_full_name(
            name,
            surname,
            last_name,
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

    async def ensure_author_provided_by_user(
            self, author_id, user_id, session
    ) -> Author:
        user = await self.user_service.get_user_by_id(user_id, session=session)

        if await self.user_service.is_user_admin(user):
            return await self.crud.get_by_id(author_id, session=session)

        try:
            return await self.crud.get_by_id_and_provided_user(
                author_id, user_id, session=session
            )
        except NotFoundInDB:
            logger.error(
                "authors.ensure_author_provided_by_user.not_owner",
                user_id=user_id,
                author_id=author_id,
            )
            raise HTTPException(
                status_code=403,
                detail="Text can be added only to authors you created",
            )

    async def delete_author(self, author_id, user_id, session):
        author = await self.crud.get_by_id(author_id, session=session)
        user = await self.user_service.get_user_by_id(user_id, session=session)

        if await self.user_service.is_user_admin(user):
            await self.crud.delete(author, session=session)
            return

        if author.provided_by_user == user_id:
            await self.crud.delete(author, session=session)
            return

        raise HTTPException(
            403,
            "Author can be deleted only by admin or the user who added them",
        )

    # services/author_service.py

    async def edit_author(
            self,
            author_id,
            form: EditAuthorForm,
            user_id,
            session,
    ) -> GetAuthorForm:
        updates = form.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(HTTP_400_BAD_REQUEST, "No fields to update")

        user = await self.user_service.get_user_by_id(user_id, session=session)

        author = await self.crud.get_by_id(author_id, session=session)

        if not await self.user_service.is_user_admin(user) and not author.provided_by_user == user_id:
            raise HTTPException(
                403,
                "Author can be edited only by admin or the user who added them"
            )

        author = await self.crud.update(author, updates, session=session)

        return AuthorEditResponse(
            id=author.id,
            name=author.name,
            surname=author.surname,
            last_name=author.last_name,
            description=author.description,
        )
