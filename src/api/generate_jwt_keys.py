import argparse
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keypair(
    private_path: Path,
    public_path: Path,
    key_size: int = 4096,
    comment: str = "jwt@app",
    force: bool = False,
) -> None:
    if not force:
        for path in (private_path, public_path):
            if path.exists():
                raise FileExistsError(
                    f"{path} already exists; pass --force to overwrite"
                )

    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )

    private_path.write_bytes(private_bytes)
    private_path.chmod(0o600)

    public_path.write_bytes(public_bytes + b" " + comment.encode("ascii") + b"\n")
    public_path.chmod(0o644)


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    default_dir = repo_root / "src" / "api" / "keys"

    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=default_dir)
    parser.add_argument("--private-name", default="jwt_private.pem")
    parser.add_argument("--public-name", default="jwt_private.pem.pub")
    parser.add_argument("--key-size", type=int, default=4096)
    parser.add_argument("--comment", default="jwt@app")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    private_path = args.out_dir / args.private_name
    public_path = args.out_dir / args.public_name

    try:
        generate_keypair(
            private_path=private_path,
            public_path=public_path,
            key_size=args.key_size,
            comment=args.comment,
            force=args.force,
        )
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {private_path}")
    print(f"wrote {public_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
