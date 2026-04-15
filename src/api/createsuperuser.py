"""
Создание суперадмина с рут правами в базу данных
"""


from dotenv import load_dotenv
from sqlalchemy import select

from app.core import database
from app.entities.user import User, Role

import os
from dotenv import load_dotenv

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

stmt = select(User).where(User.username == username)
stmt1 = select(Role).where(Role.role_name == 'admin')

with database.get_sync_session() as session:
    user = session.scalars(stmt).first()
    role = session.scalars(stmt1).first()
    if user:
        pass

    if not role:
        role = Role('admin')
        session.add(role)
        session.commit()

    user = User(username, password, role)
    session.add(user)
    session.commit()

