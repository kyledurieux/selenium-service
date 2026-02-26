import json
from pathlib import Path
from app.crypto_utils import encrypt_text, decrypt_text


USERS_FILE = Path(__file__).parent / "users.json"


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