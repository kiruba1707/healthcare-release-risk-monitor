from core.auth import (
    authenticate,
    has_permission
)

from core.audit_log import (
    write_audit_log,
    read_audit_logs
)


print("=" * 70)
print("SECURITY AND MISUSE RESISTANCE TEST")
print("=" * 70)


# ==========================================================
# TEST 1 — Invalid login
# ==========================================================

print("\n[1] Invalid login attempt")

user = authenticate(
    "release_engineer",
    "wrong_password"
)

if user is None:

    print("PASS — Invalid login rejected")

    write_audit_log(
        "release_engineer",
        "release_engineer",
        "LOGIN_ATTEMPT",
        "authentication",
        "DENIED"
    )

else:

    print("FAIL — Invalid login accepted")


# ==========================================================
# TEST 2 — Release Engineer cannot change rules
# ==========================================================

print("\n[2] Unauthorized rule modification")

allowed = has_permission(
    "release_engineer",
    "configure_rules"
)

if not allowed:

    print(
        "PASS — Release Engineer cannot configure rules"
    )

    write_audit_log(
        "release_engineer",
        "release_engineer",
        "CONFIGURE_RULES",
        "risk_thresholds",
        "DENIED"
    )

else:

    print(
        "FAIL — Unauthorized rule modification allowed"
    )


# ==========================================================
# TEST 3 — Unknown role
# ==========================================================

print("\n[3] Unknown role access")

allowed = has_permission(
    "unknown_user",
    "configure_rules"
)

if not allowed:

    print("PASS — Unknown role denied")

else:

    print("FAIL — Unknown role received permission")


# ==========================================================
# TEST 4 — Admin rule configuration permission
# ==========================================================

print("\n[4] Admin rule configuration")

allowed = has_permission(
    "operations_admin",
    "configure_rules"
)

if allowed:

    print("PASS — Admin permission accepted")

    write_audit_log(
        "operations_admin",
        "operations_admin",
        "CONFIGURE_RULES",
        "risk_thresholds",
        "ALLOWED"
    )

else:

    print("FAIL — Admin permission rejected")


# ==========================================================
# TEST 5 — Audit logs
# ==========================================================

print("\n[5] Audit log verification")

logs = read_audit_logs()

print(
    "Total audit events:",
    len(logs)
)

if len(logs) >= 2:

    print("PASS — Audit logging working")

else:

    print("FAIL — Audit logging problem")


# ==========================================================
# FINAL
# ==========================================================

print("\n" + "=" * 70)
print("SECURITY TEST COMPLETED")
print("=" * 70)