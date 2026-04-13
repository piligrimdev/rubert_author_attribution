from typing import Annotated, Callable, Type

from fastapi import Depends
from sqlalchemy.orm import Session

def create_db_dependency(
    db_object_call: Callable,
) -> Annotated[Type[Session], Callable]:
    return Annotated[
        Session,
        Depends(db_object_call),
    ]
