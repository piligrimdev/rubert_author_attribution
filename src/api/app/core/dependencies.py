from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from .database import database
from ..dependencies.database import create_db_dependency
from ..dependencies.auth import CurrentUserUUID

session_dependency = create_db_dependency(
    database.get_db
)

def allowed_extensions(*exts: str):
    normalized = tuple(e.lower() if e.startswith(".") else f".{e.lower()}" for e in exts)
    async def _validate(file: UploadFile = File(...)) -> UploadFile:
        suf = Path(file.filename or "").suffix.lower()
        if suf not in normalized:
            raise HTTPException(
                status_code=400,
                detail=f"Разрешённые расширения: {', '.join(normalized)}, получено: {suf!r}",
            )
        return file
    return _validate