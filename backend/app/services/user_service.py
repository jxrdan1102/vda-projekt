from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


async def username_exists(db: AsyncSession, username: str) -> bool:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none() is not None


async def ensure_superadmin(db: AsyncSession, username: str, password: str) -> bool:
    """Legt einen Superadmin an, falls es noch keinen gibt. Gibt True zurück, wenn angelegt."""
    from app.core import roles
    from app.routers.auth import bcrypt_context

    result = await db.execute(select(User).where(User.role == roles.SUPERADMIN))
    if result.scalars().first() is not None:
        return False
    if await username_exists(db, username):
        raise ValueError(f"Benutzername '{username}' existiert bereits")

    db.add(User(
        username=username,
        hashed_password=bcrypt_context.hash(password),
        role=roles.SUPERADMIN,
        fk_company=None,
        is_active=True,
    ))
    await db.commit()
    return True
