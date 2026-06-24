import os
from typing import Any, Type
import uuid

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from ..entities import Author, Genre, Role, Text, User
from ..utils.auth import check_password, hash_password


def _as_pk(value: Any) -> uuid.UUID | None:
    if value is None or value == "":
        return None
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


def _resolve_related(session, model: Type, value: Any):
    if value is None:
        return None
    if isinstance(value, model):
        return value
    return session.get(model, _as_pk(value))


class AdminAuthBackend(AuthenticationBackend):
    def __init__(self, session_maker: sessionmaker):
        super().__init__(secret_key=os.getenv("ADMIN_SECRET_KEY", "change-me"))
        self.session_maker = session_maker

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        with self.session_maker() as session:
            user = session.query(User).filter(User.username == username).first()
            if user is None or user.role is None:
                return False

            try:
                check_password(password, user.password_hash)
            except ValueError:
                return False

            if user.role.role_name.lower() != "admin":
                return False

        request.session.update({"admin_username": username})
        return True

    async def authenticate(self, request: Request) -> bool:
        username = request.session.get("admin_username")
        if not username:
            return False

        with self.session_maker() as session:
            user = session.query(User).filter(User.username == username).first()
            return bool(
                user is not None
                and user.role is not None
                and user.role.role_name.lower() == "admin"
            )

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.username, User.role]
    form_columns = ["username", "password_hash", "role"]
    form_args = {
        "password_hash": {
            "label": "Password",
        }
    }
    form_create_rules = ["username", "password_hash", "role"]
    form_edit_rules = ["username", "password_hash", "role"]

    async def insert_model(self, request: Request, data: dict) -> User:
        username = data["username"]
        password = data.get("password_hash")
        role = data.get("role") or data.get("role_id")

        if not password:
            raise ValueError("Password is required for user creation")
        if role is None:
            raise ValueError("Role is required for user creation")

        with self.session_maker() as session:
            role = _resolve_related(session, Role, role)
            user_password_hash  = hash_password(password)
            model = User(username=username, password_hash=user_password_hash, role=role)
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    async def update_model(self, request: Request, pk: Any, data: dict) -> User:
        with self.session_maker() as session:
            model = session.get(User, _as_pk(pk))
            if model is None:
                raise ValueError("User not found")

            model.username = data.get("username", model.username)

            role_value = data.get("role")
            if role_value is None:
                role_value = data.get("role_id")

            if role_value is not None:
                role = _resolve_related(session, Role, role_value)
                model.role = role
                model.role_id = role.id

            if data.get("password_hash"):
                updated = User(
                    username=model.username,
                    password_hash=data["password_hash"],
                    role=model.role,
                )
                model.password_hash = updated.password_hash

            session.add(model)
            session.commit()
            session.refresh(model)
            return model


class AuthorAdmin(ModelView, model=Author):
    name = "Author"
    name_plural = "Authors"
    column_list = [Author.id, Author.surname, Author.name, Author.last_name]
    form_columns = [Author.surname, Author.name, Author.last_name, Author.description]

    async def insert_model(self, request: Request, data: dict) -> Author:
        with self.session_maker() as session:
            model = Author(
                surname=data["surname"],
                name=data["name"],
                last_name=data["last_name"],
                description=data["description"],
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    async def update_model(self, request: Request, pk: Any, data: dict) -> Author:
        with self.session_maker() as session:
            model = session.get(Author, _as_pk(pk))
            if model is None:
                raise ValueError("Author not found")

            model.surname = data.get("surname", model.surname)
            model.name = data.get("name", model.name)
            model.last_name = data.get("last_name", model.last_name)
            model.description = data.get("description", model.description)
            session.add(model)
            session.commit()
            session.refresh(model)
            return model


class GenreAdmin(ModelView, model=Genre):
    name = "Genre"
    name_plural = "Genres"
    column_list = [Genre.id, Genre.genre_name]
    form_columns = [Genre.genre_name]

    async def insert_model(self, request: Request, data: dict) -> Genre:
        with self.session_maker() as session:
            model = Genre(genre_name=data["genre_name"])
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    async def update_model(self, request: Request, pk: Any, data: dict) -> Genre:
        with self.session_maker() as session:
            model = session.get(Genre, _as_pk(pk))
            if model is None:
                raise ValueError("Genre not found")

            model.genre_name = data["genre_name"]
            session.add(model)
            session.commit()
            session.refresh(model)
            return model


class RoleAdmin(ModelView, model=Role):
    name = "Role"
    name_plural = "Roles"
    column_list = [Role.id, Role.role_name]

    async def insert_model(self, request: Request, data: dict) -> Role:
        with self.session_maker() as session:
            model = Role(name=data["role_name"])
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    async def update_model(self, request: Request, pk: Any, data: dict) -> Role:
        with self.session_maker() as session:
            model = session.get(Role, _as_pk(pk))
            if model is None:
                raise ValueError("Role not found")

            model.role_name = data["role_name"]
            session.add(model)
            session.commit()
            session.refresh(model)
            return model


class TextAdmin(ModelView, model=Text):
    name = "Text"
    name_plural = "Texts"
    column_list = [Text.id, Text.text, Text.author, Text.genre, Text.provided_by]
    column_details_list = [
        Text.id,
        Text.text,
        Text.author,
        Text.genre,
        Text.provided_by,
        Text.is_visible,
    ]
    column_export_exclude_list = [Text.embedding]
    form_columns = [Text.text, Text.author, Text.genre, Text.provided_by]

    async def insert_model(self, request: Request, data: dict) -> Text:
        with self.session_maker() as session:
            author = _resolve_related(session, Author, data["author"])
            genre = _resolve_related(session, Genre, data["genre"])
            provided_by = _resolve_related(session, User, data["provided_by"])



            result = session.execute(
                insert(Text).values(
                    text=data["text"],
                    author_id=author.id,
                    genre_id=genre.id,
                    provided_by_user=provided_by.id,
                )
            )
            session.commit()
            model = session.get(Text, result.inserted_primary_key[0])
            return model

    async def update_model(self, request: Request, pk: Any, data: dict) -> Text:
        with self.session_maker() as session:
            model = session.get(Text, _as_pk(pk))
            if model is None:
                raise ValueError("Text not found")

            model.text = data.get("text", model.text)

            if data.get("author") is not None:
                author = _resolve_related(session, Author, data["author"])
                model.author = author
                model.author_id = author.id

            if data.get("genre") is not None:
                genre = _resolve_related(session, Genre, data["genre"])
                model.genre = genre
                model.genre_id = genre.id

            if data.get("provided_by") is not None:
                provided_by = _resolve_related(session, User, data["provided_by"])
                model.provided_by = provided_by
                model.provided_by_user = provided_by.id

            session.add(model)
            session.commit()
            session.refresh(model)
            return model