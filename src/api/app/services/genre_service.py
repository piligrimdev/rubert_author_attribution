from typing import List
import structlog
from ..crud.entities.genre import GenreCRUDDatabaseProvider
from ..crud.abstract_crud_db_provider import NotFoundInDB
from ..entities.genre import Genre
from ..schemas.requests import CreateGenreForm
from ..schemas.responses import GenreResponse

logger = structlog.get_logger(__name__)

class GenreService:
    def __init__(
            self,
            genre_crud: GenreCRUDDatabaseProvider
    ):
        self.crud = genre_crud

    async def list_all(
            self, session
    ) -> List[GenreResponse]:
        genres = await self.crud.list_all(session)

        return [
            GenreResponse(
                id=x.id,
                name=x.genre_name
            ) for x in genres
        ]

    async def get_by_name(
            self,
            name: str,
            session
    ) -> GenreResponse:
        genre = await self.get_by_name_entity(name, session=session)

        return GenreResponse(
            id=genre.id,
            name=genre.genre_name
        )

    async def get_by_name_entity(
            self,
            name: str,
            session
    ) -> Genre:
        # вернет orm, а не схему, чтобы далее работать с бд
        return await self.crud.get_by_name(name, session=session)


    async def get_or_create(
        self,
        name: str,
        session
    ) -> GenreResponse:
        try:
            return await self.get_by_name(name, session=session)
        except NotFoundInDB:
            logger.debug('genre.get_or_create.not_found', name=name)
            result =  await self.add_genre(
                CreateGenreForm(name=name),
                session=session
            )
            logger.info('genre.get_or_create.created', name=name)
            return result

    async def get_or_create_entity(self, name: str, session) -> Genre:
        # вернет orm, а не схему, чтобы далее работать с бд
        try:
            return await self.crud.get_by_name(name, session=session)
        except NotFoundInDB:
            logger.debug('genre.get_or_create_entity.not_found', name=name)
            logger.info('genre.get_or_create_entity.created', name=name)
            result =  await self.crud.create(name, session=session)
            logger.info('genre.get_or_create_entity.created', name=name)
            return result


    async def add_genre(
            self, form: CreateGenreForm, session
    ) -> GenreResponse:

        genre_obj = await self.crud.create(
            name=form.name,
            session=session,
        )
        logger.info('genre.get_or_create_entity.created', name=form.name)

        return GenreResponse(
            id=genre_obj.id,
            name=genre_obj.genre_name
        )
