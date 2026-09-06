import hashlib
import json
import os


USERS_FILE = "data/users.json"


DEFAULT_USERS = {
    "release_engineer": {
        "password_hash": hashlib.sha256(
            "release123".encode()
        ).hexdigest(),
        "role": "release_engineer"
    },

    "operations_admin": {
        "password_hash": hashlib.sha256(
            "admin123".encode()
        ).hexdigest(),
        "role": "operations_admin"
    }
}


def _load_users():
    if not os.path.exists(USERS_FILE):
        return DEFAULT_USERS.copy()

    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)

        if isinstance(users, dict):
            return users

    except (json.JSONDecodeError, OSError):
        pass

    return DEFAULT_USERS.copy()


def _save_users(users):
    os.makedirs("data", exist_ok=True)

    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def authenticate(username, password):
    users = _load_users()

    if username not in users:
        return None

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    user = users[username]

    if password_hash == user["password_hash"]:
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

    current_hash = hashlib.sha256(
        current_password.encode()
    ).hexdigest()

    if users[current_username]["password_hash"] != current_hash:
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

    new_hash = hashlib.sha256(
        new_password.encode()
    ).hexdigest()

    user_data = users.pop(current_username)

    user_data["password_hash"] = new_hash

    users[target_username] = user_data

    _save_users(users)

    return True, target_username


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


def has_permission(role, permission):
    permissions = ROLE_PERMISSIONS.get(
        role,
        set()
    )

    return permission in permissions