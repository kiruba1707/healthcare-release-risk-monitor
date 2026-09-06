from core.auth import authenticate, has_permission


def test_valid_release_engineer_authentication():
    user = authenticate("release_engineer", "release123")

    assert user is not None
    assert user["role"] == "release_engineer"


def test_invalid_password_rejected():
    user = authenticate("release_engineer", "wrongpassword")

    assert user is None


def test_release_engineer_cannot_configure_rules():
    assert not has_permission(
        "release_engineer",
        "configure_rules"
    )


def test_operations_admin_can_configure_rules():
    assert has_permission(
        "operations_admin",
        "configure_rules"
    )


def test_operations_admin_can_view_audit_logs():
    assert has_permission(
        "operations_admin",
        "view_audit_logs"
    )
