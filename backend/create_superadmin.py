"""Ersten Superadmin (Entwickler-Konto) anlegen.

Aufruf im Ordner backend/:
    python create_superadmin.py <benutzername>
Das Passwort wird interaktiv abgefragt.
"""
import asyncio
import getpass
import sys

import app.models  # noqa: F401  – alle Modelle registrieren
from app.database.database import SessionLocal
from app.services.user_service import ensure_superadmin


async def main(username: str, password: str) -> None:
    async with SessionLocal() as db:
        created = await ensure_superadmin(db, username, password)
    print("Superadmin angelegt." if created else "Es gibt bereits einen Superadmin – nichts geändert.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    pw = getpass.getpass("Passwort: ")
    if len(pw) < 8 or pw != getpass.getpass("Passwort wiederholen: "):
        print("Passwörter stimmen nicht überein oder sind kürzer als 8 Zeichen.")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], pw))
