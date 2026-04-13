import os

from ..database.database import Database
from ..database.base import Base  # noqa

from dotenv import load_dotenv

load_dotenv()

database = Database(os.getenv("DATABASE_URL", ''))
