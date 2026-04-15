import asyncio
import argparse
import pandas as pd

from app.core.database import database
from app.core.services import model, author_service, text_service, user_service
from app.crud.abstract_crud_db_provider import NotFoundInDB
from app.entities.genre import Genre
from app.entities.user import User


def parse_author_name(full_name: str) -> tuple[str, str, str]:
    # parts = full_name.strip().split()
    # surname = parts[0] if len(parts) > 0 else ""
    # name = parts[1] if len(parts) > 1 else ""
    # last_name = " ".join(parts[2:]) if len(parts) > 2 else ""
    #return name, surname, last_name
    return full_name, "", ""


async def get_or_create_genre(name: str, session) -> Genre:
    try:
        return await text_service.genre_crud.get_by_name(name, session=session)
    except NotFoundInDB:
        genre = Genre(genre_name=name)
        session.add(genre)
        session.commit()
        session.expunge(genre)
        return genre


async def get_or_create_author(name, surname, last_name, admin_user, session):
    try:
        return await author_service.crud.get_by_full_name(
            name, surname, last_name, session=session
        )
    except NotFoundInDB:
        return await author_service.crud.create(
            name, surname, last_name, admin_user, session
        )


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--genre_name", default="Russian Literature")
    p.add_argument("--path_to_corpus", required=True)
    args = p.parse_args()

    df = pd.read_csv(args.path_to_corpus)

    df = df[df['source_type'] == args.genre_name]

    df.drop(columns=['source_type'], inplace=True)

    if "author" not in df.columns or "text" not in df.columns:
        print("CSV must contain 'author' and 'text' columns")
        return

    print(f"{len(df)} rows")

    with database.get_sync_session() as session:
        admin_role = await user_service.role_crud.get_by_name("admin", session=session)
        admins = await user_service.crud.select_where(
            User.role_id == admin_role.id, all=True, session=session
        )
        if not admins:
            print("No admin user found.")
            return
        admin_user = admins[0]
        print(f"Using admin: {admin_user.username}")

        genre = await get_or_create_genre(args.genre_name, session)
        print(f"Using genre: {genre.genre_name}")

        author_cache: dict[str, object] = {}
        added, skipped, errors = 0, 0, 0

        for i, row in df.iterrows():
            try:
                author_str = str(row["author"]).strip()
                text_content = str(row["text"]).strip()

                if not author_str or not text_content:
                    skipped += 1
                    continue

                if author_str not in author_cache:
                    name, surname, last_name = parse_author_name(author_str)
                    author_cache[author_str] = await get_or_create_author(
                        name, surname, last_name, admin_user, session
                    )
                    print(f"  Author: {author_str}")

                author = author_cache[author_str]

                embedding = model.generate_embedding(text_content)
                if isinstance(embedding[0], list):
                    embedding = embedding[0]

                await text_service.crud.create(
                    text=text_content,
                    author=author,
                    genre=genre,
                    provided_by=admin_user,
                    embedding=embedding,
                    session=session,
                )
                added += 1

                if added % 25 == 0:
                    print(f"  Progress: {added} texts added ...")

            except Exception as e:
                errors += 1
                print(f"  Error at row {i}: {e}")

        print(f"\nDone: {added} added, {skipped} skipped, {errors} errors.")


if __name__ == "__main__":
    asyncio.run(main())
