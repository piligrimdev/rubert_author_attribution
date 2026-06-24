import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..abstract_crud_db_provider import AbstractCRUDDatabaseProvider
from ...entities.text import Text
from ...entities.author import Author
from ...entities.genre import Genre
from ...entities.user import User


class TextCRUDDatabaseProvider(AbstractCRUDDatabaseProvider):
    model = Text

    async def get_by_author(
            self,
            author_id: uuid.UUID,
            session: Session = None
    ) -> List[Text]:
        stmt = (
            select(Text)
            .where(Text.author_id == author_id)
            .options(joinedload(Text.author), joinedload(Text.genre))
        )
        results = session.scalars(stmt).unique().all()
        for item in results:
            session.expunge(item)
        return results

    async def get_available(
            self,
            author_ids: List[uuid.UUID],
            session: Session = None
    ) -> List[Text]:
        if not author_ids:
            return []
        stmt = (
            select(Text)
            .where(Text.author_id.in_(author_ids))
            .options(joinedload(Text.author), joinedload(Text.genre))
        )
        results = session.scalars(stmt).unique().all()
        for item in results:
            session.expunge(item)
        return results

    async def find_nearest(
            self,
            embedding: list,
            #author_ids: List[uuid.UUID],
            text_ids: List[uuid.UUID],
            k: int = 5,
            session: Session = None
    ) -> list:
        if not text_ids:
            return []

        distance = Text.embedding.cosine_distance(embedding)

        stmt = (
            select(Text, distance.label("distance"))
            .where(Text.id.in_(text_ids))
            .options(joinedload(Text.author))
            .order_by(distance)
            .limit(k)
        )

        results = session.execute(stmt).unique().all()
        output = []
        for row in results:
            text_obj = row[0]
            dist = float(row[1])
            session.expunge(text_obj)
            output.append((text_obj, dist))
        return output

    async def create(
            self,
            text: str,
            author: Author,
            genre: Genre,
            provided_by: User,
            embedding: list,
            session: Session = None
    ) -> Text:
        text_obj = Text(
            text=text,
            author=author,
            genre=genre,
            provided_by_user=provided_by,
            embedding=embedding,
        )

        session.add(text_obj)
        session.commit()
        session.expunge(text_obj)

        return text_obj

    async def get_by_id(
            self, text_id, session: Session = None
    ) -> Author:
        return await self.select_where(
            Text.id == text_id,
            session=session
        )
