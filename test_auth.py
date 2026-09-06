from core.auth import authenticate, has_permission


def test_release_engineer_login():
    user = authenticate("release_engineer", "release123")

    assert user is not None
    assert user["role"] == "release_engineer"


def test_operations_admin_login():
    admin = authenticate("operations_admin", "admin123")

    assert admin is not None
    assert admin["role"] == "operations_admin"


def test_wrong_password():
    invalid = authenticate(
        "release_engineer",
        "wrongpassword"
    )

    assert invalid is None


def test_release_engineer_permissions():
    assert has_permission(
        "release_engineer",
        "start_rollout"
    )

    assert not has_permission(
        "release_engineer",
        "configure_rules"
    )


def test_operations_admin_permissions():
    assert has_permission(
        "operations_admin",
        "configure_rules"
    )

    assert has_permission(
        "operations_admin",
        "view_audit_logs"
    )