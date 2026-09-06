from core.auth import (
    authenticate,
    has_permission
)


print("=" * 70)
print("ROLE-BASED ACCESS CONTROL TEST")
print("=" * 70)


# --------------------------------------------------
# Test 1 — Release Engineer login
# --------------------------------------------------

user = authenticate(
    "release_engineer",
    "release123"
)

print("\nRelease Engineer login:")
print(user)


# --------------------------------------------------
# Test 2 — Operations Admin login
# --------------------------------------------------

admin = authenticate(
    "operations_admin",
    "admin123"
)

print("\nOperations Admin login:")
print(admin)


# --------------------------------------------------
# Test 3 — Wrong password
# --------------------------------------------------

invalid = authenticate(
    "release_engineer",
    "wrongpassword"
)

print("\nWrong password:")
print(invalid)


# --------------------------------------------------
# Test permissions
# --------------------------------------------------

print("\nPermissions:")

print(
    "Release Engineer → start rollout:",
    has_permission(
        "release_engineer",
        "start_rollout"
    )
)

print(
    "Release Engineer → configure rules:",
    has_permission(
        "release_engineer",
        "configure_rules"
    )
)

print(
    "Operations Admin → configure rules:",
    has_permission(
        "operations_admin",
        "configure_rules"
    )
)

print(
    "Operations Admin → audit logs:",
    has_permission(
        "operations_admin",
        "view_audit_logs"
    )
)


# --------------------------------------------------
# Security test
# --------------------------------------------------

print("\nSecurity test:")

assert invalid is None

assert has_permission(
    "release_engineer",
    "start_rollout"
)

assert not has_permission(
    "release_engineer",
    "configure_rules"
)

assert has_permission(
    "operations_admin",
    "configure_rules"
)

print("All RBAC tests PASSED")