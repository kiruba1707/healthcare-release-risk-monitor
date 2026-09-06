import hashlib


# --------------------------------------------------
# Demo users
# --------------------------------------------------

USERS = {
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


# --------------------------------------------------
# Login
# --------------------------------------------------

def authenticate(username, password):
    """
    Authenticate a user using a hashed password.
    """

    if username not in USERS:
        return None

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    user = USERS[username]

    if password_hash == user["password_hash"]:
        return {
            "username": username,
            "role": user["role"]
        }

    return None


# --------------------------------------------------
# Permission check
# --------------------------------------------------

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
    """
    Check whether a role has a specific permission.
    """

    permissions = ROLE_PERMISSIONS.get(
        role,
        set()
    )

    return permission in permissions