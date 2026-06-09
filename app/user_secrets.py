import json
from pathlib import Path
from crypto_utils import encrypt_text, decrypt_text
import os


USERS_FILE = Path(os.getenv("USERS_PATH", "users.json"))


def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_zhealth_credentials(username: str, z_username: str, z_password: str):
    users = load_users()

    if username not in users:
        raise ValueError(f"User '{username}' not found")

    if z_password:
        encrypted_password = encrypt_text(z_password)
    else:
        encrypted_password = ""

    users[username].setdefault("software_credentials", {})
    users[username]["software_credentials"].setdefault("zhealthehr", {})

    users[username]["software_credentials"]["zhealthehr"]["username"] = z_username
    users[username]["software_credentials"]["zhealthehr"]["password"] = encrypted_password

    save_users(users)


def get_zhealth_credentials(username: str):
    users = load_users()

    if username not in users:
        raise ValueError(f"User '{username}' not found")

    z_user = users[username]["software_credentials"]["zhealthehr"]["username"]
    encrypted_password = users[username]["software_credentials"]["zhealthehr"]["password"]

    if not encrypted_password:
        return z_user, None

    decrypted = decrypt_text(encrypted_password)
    return z_user, decrypted

def get_zhealth_status(username: str):
    """
    Safe status only: returns saved zHealth username and whether a password token exists.
    Never decrypts and never returns the password.
    """
    users = load_users()

    if username not in users:
        raise ValueError(f"User '{username}' not found")

    z = users[username].get("software_credentials", {}).get("zhealthehr", {})
    z_user = z.get("username", "") or ""
    z_pass = z.get("password", "") or ""

    return {"zhealth_username": z_user, "has_password": bool(z_pass)}