from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


async def username_exists(db: AsyncSession, username: str) -> bool:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none() is not None
