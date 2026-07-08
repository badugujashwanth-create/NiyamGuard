import hashlib
import hmac
import os

try:
    import bcrypt
except ImportError:  # pragma: no cover - fallback supports dev envs before install.
    bcrypt = None


def hash_password(password: str, salt: str | None = None) -> str:
    if bcrypt is not None and salt is None:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    salt_hex = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        210_000,
    ).hex()
    return f"pbkdf2_sha256${salt_hex}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("$2") and bcrypt is not None:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    try:
        algorithm, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(candidate, expected)
