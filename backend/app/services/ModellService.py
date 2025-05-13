from app.models.components import Component
from app.models.modell import Modell
from app.services.BaseCRUD import BaseCRUD
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

ModellCRUD = BaseCRUD(Modell)

async def get_all_modells(db: AsyncSession, user_id: int):
    return await ModellCRUD.get_all_by_user(db, user_id)

async def get_modell_by_id(db: AsyncSession, id: int, user_id: int):
    stmt = (
        select(Modell)
        .where(Modell.id == id, Modell.fk_user_id == user_id)
        .options(
            selectinload(Modell.components),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_modell(db: AsyncSession, data: dict, user_id: int):
    data["fk_user_id"] = user_id
    return await ModellCRUD.create(db, data)

async def update_modell(db: AsyncSession, id: int, data: dict, user_id: int):
    return await ModellCRUD.update(db, id, data, user_id)

async def delete_modell_with_components(db: AsyncSession, id: int, user_id: int):
    await ModellCRUD.get_by_id(db, id, user_id)  # Safety check
    await db.execute(delete(Component).where(Component.fk_modell == id))
    return await ModellCRUD.delete(db, id, user_id)