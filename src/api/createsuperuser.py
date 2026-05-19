"""
Создание суперадмина с рут правами в базу данных
"""


from dotenv import load_dotenv
from sqlalchemy import select

from app.core.database import database
from app.entities.user import User, Role
from app.utils.auth import hash_password

import os
from dotenv import load_dotenv

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

stmt = select(User).where(User.username == username)
stmt1 = select(Role).where(Role.role_name == 'admin')
with database.get_sync_session() as session:
    user = session.scalars(stmt).first()
    role = session.scalars(stmt1).first()

    if not role:
        print("No admin role  founded. Creating admin role...")
        role = Role('admin')
        session.add(role)
        session.commit()
        print("Role created")
    if not user:
        print("No user with specified username founded. Creating new admin user...")
        password_hash = hash_password(password)
        user = User(username, password_hash, role)
        session.add(user)
        session.commit()
        print("User created")

