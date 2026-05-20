import uuid
from typing import List, Optional
import structlog
from fastapi import HTTPException

from ..crud.entities.text import TextCRUDDatabaseProvider
from ..crud.entities.genre import GenreCRUDDatabaseProvider
from ..crud.abstract_crud_db_provider import NotFoundInDB
from ..entities.author import Author
from ..entities.genre import Genre
from ..entities.text import Text
from ..models.abstract_model_provider import AbstractModelProvider
from ..schemas.requests import CreateTextForm
from ..schemas.responses import TextItemResponse, NearestTextItem, NearestTextsResponse


logger = structlog.get_logger(__name__)

class TextService:
    def __init__(
            self,
            text_crud: TextCRUDDatabaseProvider,
            genre_crud: GenreCRUDDatabaseProvider,
            author_service,
            user_service,
            model: AbstractModelProvider,
    ):
        self.crud = text_crud
        self.genre_crud = genre_crud
        self.author_service = author_service
        self.user_service = user_service
        self.model = model

    async def _get_available_author_ids(self, user_id, session) -> List[uuid.UUID]:
        user = await self.user_service.get_user_by_id(user_id, session=session)

        if await self.user_service.is_user_admin(user):
            authors = await self.author_service.crud.list_all(session)
        else:
            admin_users = await self.user_service.get_admin_users(session=session)
            admin_users.append(user)
            authors = await self.author_service.crud.list_all_available(
                admin_users, session=session
            )

        return [a.id for a in authors]

    async def list_available(self, user_id, session) -> List[TextItemResponse]:
        author_ids = await self._get_available_author_ids(user_id, session)
        texts = await self.crud.get_available(author_ids, session=session)

        return [
            TextItemResponse(
                text_id=t.id,
                text=t.text,
                author_id=t.author_id,
                author=str(t.author),
                genre=str(t.genre),
            )
            for t in texts
        ]

    async def get_texts_of_author(
            self, author_id: uuid.UUID, user_id, session
    ) -> List[TextItemResponse]:
        available_ids = await self._get_available_author_ids(user_id, session)

        if author_id not in available_ids:
            logger.error("texts.get_texts_of_author.not_available", user_id=user_id, author_id=author_id)
            raise HTTPException(
                status_code=403, detail="Author is not available to you"
            )

        texts = await self.crud.get_by_author(author_id, session=session)

        return [
            TextItemResponse(
                text_id=t.id,
                text=t.text,
                author_id=t.author_id,
                author=str(t.author),
                genre=str(t.genre),
            )
            for t in texts
        ]

    def _embed(self, text: str) -> list:
        embedding = self.model.generate_embedding(text)
        if isinstance(embedding[0], list):
            embedding = embedding[0]
        logger.debug("texts.embedding.generated")
        return embedding

    async def add_text_entity(
            self,
            text: str,
            author: Author,
            genre: Genre,
            user_id,
            session,
    ) -> Text:
        # без проверки на доступность автора юзеру для загрузки из csv

        user = await self.user_service.get_user_by_id(user_id, session=session)
        embedding = self._embed(text)

        result =  await self.crud.create(
            text=text,
            author=author,
            genre=genre,
            provided_by=user,
            embedding=embedding,
            session=session,
        )

        logger.info("texts.created", user_id=user.id, author_id=author.id)
        return result

    async def add_text(
            self, form: CreateTextForm, user_id, session
    ) -> TextItemResponse:
        available_ids = await self._get_available_author_ids(user_id, session)

        if form.author_id not in available_ids:
            logger.error("texts.add_text_for_author.not_available", user_id=user_id, author_id=form.author_id)
            raise HTTPException(
                status_code=403, detail="Author is not available to you"
            )

        try:
            genre = await self.genre_crud.get_by_name(
                form.genre_name, session=session
            )
        except NotFoundInDB:
            logger.error("texts.add_text_for_author.genre_not_found", user_id=user_id, genre=form.genre_name)
            raise HTTPException(status_code=404, detail="Genre not found")

        author = await self.author_service.crud.select_where(
            Author.id == form.author_id, session=session
        )

        user = await self.user_service.get_user_by_id(user_id, session=session)

        embedding = self._embed(form.text)

        text_obj = await self.crud.create(
            text=form.text,
            author=author,
            genre=genre,
            provided_by=user,
            embedding=embedding,
            session=session,
        )
        logger.info("texts.created", user_id=user_id, author_id=author.id)

        return TextItemResponse(
            text_id=text_obj.id,
            text=text_obj.text,
            author_id=author.id,
            author=str(author),
            genre=str(genre),
        )

    async def find_nearest(
            self,
            text: str,
            user_id,
            k: int,
            session,
            author_ids: Optional[List[uuid.UUID]] = None,
    ) -> NearestTextsResponse:
        available_ids = await self._get_available_author_ids(user_id, session)

        if not available_ids:
            logger.info("texts.find_nearest.no_author_available_for_user", user_id=user_id)
            return NearestTextsResponse(items=[])

        if author_ids is None:
            logger.debug("texts.find_nearest.no_author_list_provided_in_request", user_id=user_id)
            search_author_ids = available_ids
        elif not author_ids:
            logger.info("texts.find_nearest.empty_author_list_provided_in_request", user_id=user_id)
            return NearestTextsResponse(items=[])
        else:
            available_set = set(available_ids)
            missing = [aid for aid in author_ids if aid not in available_set]
            if missing:
                logger.error("texts.find_nearest.authors_not_available_for_user", user_id=user_id)
                raise HTTPException(
                    status_code=403,
                    detail="One or more authors are not available to you",
                )
            search_author_ids = author_ids

        embedding = self._embed(text)

        results = await self.crud.find_nearest(
            embedding=embedding,
            author_ids=search_author_ids,
            k=k,
            session=session,
        )

        items = [
            NearestTextItem(
                text_id=text_obj.id,
                text=text_obj.text,
                author_id=text_obj.author_id,
                author=str(text_obj.author),
                distance=dist,
            )
            for text_obj, dist in results
        ]

        logger.info("texts.find_nearest.finished")

        return NearestTextsResponse(items=items)
