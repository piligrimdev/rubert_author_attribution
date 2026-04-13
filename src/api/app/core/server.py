import os
from fastapi import FastAPI
from uvicorn import Config, Server
from sqladmin import Admin
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

from app.routes import router, admin_routes, AdminAuthBackend
from .database import database


class API:
    def __init__(
        self,
        engine,
        host="localhost",
        port=2000
    ):
        self.api = FastAPI(
            docs_url=None
        )  # to pass description parameters e.t.c
        self.api.add_middleware(
            SessionMiddleware,
            secret_key="change-me",
        )
        self.admin = Admin(
            self.api,
            engine,
            authentication_backend=AdminAuthBackend(database.session),
        )

        config = Config(self.api, host, port)
        self.server = Server(config)

    def setup(self, router, admin_routes):
        for route in admin_routes:
            self.admin.add_view(route)
        self.api.include_router(router)


load_dotenv()
host = os.getenv("API_HOST", 'localhost')
port = int(os.getenv("API_PORT", '3000'))

api: API = API(database.engine, host=host, port=port)
api.setup(router, admin_routes)

