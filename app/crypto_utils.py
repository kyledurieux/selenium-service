import os
from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    key = os.getenv("CNH_FERNET_KEY")
    if not key:
        raise RuntimeError(
            "CNH_FERNET_KEY is not set. "
            "Set it in app/.env (for docker/app runtime) or export it in your shell."
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_text(plain: str) -> str:
    """
    Encrypt a plaintext string and return a URL-safe base64 string.
    """
    if plain is None:
        raise ValueError("plain cannot be None")
    f = _get_fernet()
    token = f.encrypt(plain.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(token: str) -> str:
    """
    Decrypt a previously-encrypted token string and return plaintext.
    """
    if token is None:
        raise ValueError("token cannot be None")
    f = _get_fernet()
    plain = f.decrypt(token.encode("utf-8"))
    return plain.decode("utf-8")