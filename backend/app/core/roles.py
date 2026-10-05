"""Rollen und Rechte.

superadmin  – Entwickler / Betreiber: darf alles (Firmen, Admins, alle Daten)
admin       – Firmen-Admin: verwaltet die Nutzer seiner eigenen Firma
user        – normaler Nutzer: arbeitet mit dem Programm
readonly    – darf nur lesen
"""

SUPERADMIN = "superadmin"
ADMIN = "admin"
USER = "user"
READONLY = "readonly"

ALL_ROLES = (SUPERADMIN, ADMIN, USER, READONLY)
COMPANY_ROLES = (ADMIN, USER, READONLY)
# Rollen, die ein Firmen-Admin vergeben darf
ADMIN_ASSIGNABLE_ROLES = (USER, READONLY)


def is_admin(role: str | None) -> bool:
    return role in (SUPERADMIN, ADMIN)


def assignable_roles(actor_role: str) -> tuple[str, ...]:
    if actor_role == SUPERADMIN:
        return ALL_ROLES
    if actor_role == ADMIN:
        return ADMIN_ASSIGNABLE_ROLES
    return ()
