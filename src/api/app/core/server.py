import os
from fastapi import FastAPI
from uvicorn import Config, Server
from sqladmin import Admin
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

from app.routes import router, admin_routes, AdminAuthBackend
from .database import database
from .logging_config import UVICORN_LOG_CONFIG
from .metrics import setup_http_metrics
from .request_id_middleware import RequestIdMiddleware
from .access_token_cookie_middleware import AccessTokenCookieMiddleware


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
        setup_http_metrics(self.api)
        self.api.add_middleware(
            SessionMiddleware,
            secret_key="change-me",
        )
        self.api.add_middleware(RequestIdMiddleware)
        self.api.add_middleware(AccessTokenCookieMiddleware)
        self.admin = Admin(
            self.api,
            engine,
            authentication_backend=AdminAuthBackend(database.session),
        )

        access_log = os.getenv("LOG_UVICORN_ACCESS", "1") == "1"
        config = Config(
            self.api,
            host,
            port,
            log_config=UVICORN_LOG_CONFIG,
            access_log=access_log,
        )
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

