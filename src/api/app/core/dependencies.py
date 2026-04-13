from .database import database
from ..dependencies.database import create_db_dependency
from ..dependencies.auth import CurrentUserUUID

session_dependency = create_db_dependency(
    database.get_db
)
