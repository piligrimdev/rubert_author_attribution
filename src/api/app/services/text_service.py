import uuid
from typing import List

from fastapi import HTTPException

from ..crud.entities.text import TextCRUDDatabaseProvider
from ..crud.entities.genre import GenreCRUDDatabaseProvider
from ..crud.abstract_crud_db_provider import NotFoundInDB
from ..entities.author import Author
from ..models.abstract_model_provider import AbstractModelProvider
from ..schemas.requests import CreateTextForm
from ..schemas.responses import TextItemResponse, NearestTextItem, NearestTextsResponse


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

    async def add_text(
            self, form: CreateTextForm, user_id, session
    ) -> TextItemResponse:
        available_ids = await self._get_available_author_ids(user_id, session)

        if form.author_id not in available_ids:
            raise HTTPException(
                status_code=403, detail="Author is not available to you"
            )

        try:
            genre = await self.genre_crud.get_by_name(
                form.genre_name, session=session
            )
        except NotFoundInDB:
            raise HTTPException(status_code=404, detail="Genre not found")

        author = await self.author_service.crud.select_where(
            Author.id == form.author_id, session=session
        )

        user = await self.user_service.get_user_by_id(user_id, session=session)

        embedding = self.model.generate_embedding(form.text)
        if isinstance(embedding[0], list):
            embedding = embedding[0]

        text_obj = await self.crud.create(
            text=form.text,
            author=author,
            genre=genre,
            provided_by=user,
            embedding=embedding,
            session=session,
        )

        return TextItemResponse(
            text_id=text_obj.id,
            text=text_obj.text,
            author_id=author.id,
            author=str(author),
            genre=str(genre),
        )

    async def find_nearest(
            self, text: str, user_id, k: int, session
    ) -> NearestTextsResponse:
        author_ids = await self._get_available_author_ids(user_id, session)

        if not author_ids:
            return NearestTextsResponse(items=[])

        embedding = self.model.generate_embedding(text)
        if isinstance(embedding[0], list):
            embedding = embedding[0]

        results = await self.crud.find_nearest(
            embedding=embedding,
            author_ids=author_ids,
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

        return NearestTextsResponse(items=items)
