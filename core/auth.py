import hashlib
import hmac
import json
import os
import secrets


USERS_FILE = "data/users.json"


DEFAULT_USERS = {
    "release_engineer": {
        "password_hash": None,
        "role": "release_engineer"
    },
    "operations_admin": {
        "password_hash": None,
        "role": "operations_admin"
    }
}


ROLE_PERMISSIONS = {
    "release_engineer": {
        "view_releases",
        "evaluate_release",
        "start_rollout",
        "stop_rollout"
    },
    "operations_admin": {
        "view_releases",
        "evaluate_release",
        "start_rollout",
        "stop_rollout",
        "configure_rules",
        "view_audit_logs",
        "view_system_status"
    }
}


def _hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    )

    return (
        salt.hex(),
        password_hash.hex()
    )


def _verify_password(password, stored_hash):
    try:
        salt_hex, expected_hash = stored_hash.split("$", 1)

        salt = bytes.fromhex(salt_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        ).hex()

        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )

    except (ValueError, TypeError):
        return False


def _make_stored_hash(password):
    salt_hex, password_hash = _hash_password(password)

    return f"{salt_hex}${password_hash}"


def _load_users():
    if not os.path.exists(USERS_FILE):
        users = {}

        for username, data in DEFAULT_USERS.items():
            default_password = (
                "release123"
                if username == "release_engineer"
                else "admin123"
            )

            users[username] = {
                "password_hash": _make_stored_hash(
                    default_password
                ),
                "role": data["role"]
            }

        _save_users(users)
        return users

    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)

        if isinstance(users, dict):
            return users

    except (json.JSONDecodeError, OSError):
        pass

    return {}


def _save_users(users):
    os.makedirs("data", exist_ok=True)

    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def authenticate(username, password):
    users = _load_users()

    if username not in users:
        return None

    user = users[username]

    if _verify_password(
        password,
        user["password_hash"]
    ):
        return {
            "username": username,
            "role": user["role"]
        }

    return None


def change_credentials(
    current_username,
    current_password,
    new_username=None,
    new_password=None
):
    users = _load_users()

    if current_username not in users:
        return False, "Current username not found."

    if not _verify_password(
        current_password,
        users[current_username]["password_hash"]
    ):
        return False, "Current password is incorrect."

    target_username = (
        new_username.strip()
        if new_username and new_username.strip()
        else current_username
    )

    if target_username != current_username:
        if target_username in users:
            return False, "New username already exists."

    if not new_password:
        new_password = current_password

    user_data = users.pop(current_username)

    user_data["password_hash"] = _make_stored_hash(
        new_password
    )

    users[target_username] = user_data

    _save_users(users)

    return True, target_username


def has_permission(role, permission):
    permissions = ROLE_PERMISSIONS.get(
        role,
        set()
    )

    return permission in permissions