from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .attribute import attribute_router
from .user import user_router
from .admin import *
from .authors import authors_routes
from .texts import texts_routes
from .generative import generative_router
from .genres import genre_routes

router = APIRouter(prefix='/api')

def init_docs_router(docs_file_path: str = "static/docs/docs.html") -> APIRouter:
    doc_router = APIRouter()

    def read_file(path: str) -> str:
        with open(path, encoding="utf-8") as file:
            return file.read()

    @doc_router.get("/docs", include_in_schema=False)
    def documentation() -> HTMLResponse:
        """Для кастомной документации по openapi. Например, scalars."""
        return HTMLResponse(read_file(docs_file_path))

    return doc_router

router.include_router(attribute_router)
router.include_router(user_router)
router.include_router(authors_routes)
router.include_router(texts_routes)
router.include_router(genre_routes)
router.include_router(init_docs_router())

admin_routes = [
    UserAdmin, RoleAdmin, AuthorAdmin, GenreAdmin, TextAdmin
]
