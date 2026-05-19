import argparse
import asyncio

from app.core.database import database
from app.core.services import corpus_import_service, user_service


def _progress_cb(current: int, total: int) -> None:
    if total and (current % 25 == 0 or current == total):
        percent = current * 100 // max(total, 1)
        print(f"  Progress: {current}/{total} ({percent}%)")


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--genre_name", default="Russian Literature")
    p.add_argument("--path_to_corpus", required=True)
    args = p.parse_args()

    with database.get_sync_session() as session:
        admins = await user_service.get_admin_users(session=session)
        if not admins:
            print("No admin user found.")
            return
        admin_user = admins[0]
        print(f"Using admin: {admin_user.username}")

        result = await corpus_import_service.import_from_file(
            file_path=args.path_to_corpus,
            genre_name=args.genre_name,
            user_id=admin_user.id,
            session=session,
            progress_cb=_progress_cb,
        )

    print(
        f"\nDone: {result.added} added, "
        f"{result.skipped_empty} skipped, {result.errors} errors. "
        f"Genre: {result.genre_name}"
    )


if __name__ == "__main__":
    asyncio.run(main())
