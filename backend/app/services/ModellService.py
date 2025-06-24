from fastapi import HTTPException
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.components import Component
from app.models.modell import Modell
from app.services.BaseCRUD import BaseCRUD

ModellCRUD = BaseCRUD(Modell)
ComponentCRUD = BaseCRUD(Component)

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

async def add_component(db: AsyncSession, id: int, data: dict, user_id: int):
    data["fk_user_id"] = user_id
    data["fk_modell"] = id

    # Hole aktuelle max. lfdnr innerhalb des Modells
    result = await db.execute(
        select(func.max(Component.lfdnr)).where(Component.fk_modell == id)
    )
    max_lfdnr = result.scalar() or 0
    data["lfdnr"] = max_lfdnr + 1  # Neue laufende Nummer

    return await ComponentCRUD.create(db, data)

async def delete_modell_with_components(db: AsyncSession, id: int, user_id: int):
    await ModellCRUD.get_by_id(db, id, user_id)  # Safety check
    await db.execute(delete(Component).where(Component.fk_modell == id))
    return await ModellCRUD.delete(db, id, user_id)


def clone_instance(instance, exclude: set[str] = None) -> dict:
    exclude = exclude or set()
    return {
        key: value
        for key, value in vars(instance).items()
        if not key.startswith("_") and key not in exclude
    }


async def duplicate_modell(db: AsyncSession, id: int, user_id: int, new_name: str):
    # Originalmodell mit Komponenten laden
    stmt = (
        select(Modell)
        .where(Modell.id == id, Modell.fk_user_id == user_id)
        .options(selectinload(Modell.components))
    )
    result = await db.execute(stmt)
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden oder nicht erlaubt")

    # Alle Felder kopieren außer name und id
    base_data = clone_instance(original, exclude={"id", "name", "components"})
    base_data["name"] = new_name
    base_data["fk_user_id"] = user_id

    new_modell = Modell(**base_data)
    db.add(new_modell)
    await db.flush()

    # Komponenten duplizieren (alle Felder außer id und fk_modell)
    for comp in original.components:
        comp_data = clone_instance(comp, exclude={"id", "fk_modell"})
        comp_data["fk_modell"] = new_modell.id
        comp_data["fk_user_id"] = user_id
        new_comp = Component(**comp_data)
        db.add(new_comp)

    await db.commit()
    await db.refresh(new_modell)
    return new_modell