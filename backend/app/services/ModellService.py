from fastapi import HTTPException
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.components import Component
from app.models.modell import Modell
from app.services.BaseCRUD import BaseCRUD

ModellCRUD = BaseCRUD(Modell)
ComponentCRUD = BaseCRUD(Component)

# Felder, die über die normale Bearbeitung nicht gesetzt werden dürfen
PROTECTED_FIELDS = ("is_builtin", "fk_company", "fk_user_id")


async def ensure_modell_writable(db: AsyncSession, modell_id: int) -> None:
    """Eingebaute Modelle (is_builtin) sind schreibgeschützt – samt ihren Komponenten."""
    modell = await db.get(Modell, modell_id)
    if modell is not None and modell.is_builtin:
        raise HTTPException(
            status_code=403,
            detail="Dieses Modell ist schreibgeschützt und kann nicht geändert werden.",
        )


async def get_all_modells(db: AsyncSession, company_id: int | None):
    return await ModellCRUD.get_all_by_company(db, company_id)


async def get_modell_by_id(db: AsyncSession, id: int, company_id: int | None = None):
    stmt = (
        select(Modell)
        .where(Modell.id == id)
        .options(selectinload(Modell.components))
    )
    if company_id is not None:
        stmt = stmt.where(Modell.fk_company == company_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_modell(db: AsyncSession, data: dict, user_id: int, company_id: int | None):
    data.pop("is_builtin", None)  # eingebaute Modelle kommen nur über den Import
    data["fk_user_id"] = user_id
    data["fk_company"] = company_id
    return await ModellCRUD.create(db, data)


async def update_modell(db: AsyncSession, id: int, data: dict, company_id: int | None = None):
    await ensure_modell_writable(db, id)
    data = {k: v for k, v in data.items() if k not in PROTECTED_FIELDS}
    return await ModellCRUD.update(db, id, data, company_id)


async def add_component(db: AsyncSession, id: int, data: dict, user_id: int, company_id: int | None):
    await ModellCRUD.get_by_id(db, id, company_id)
    await ensure_modell_writable(db, id)
    data["fk_user_id"] = user_id
    data["fk_company"] = company_id
    data["fk_modell"] = id
    result = await db.execute(
        select(func.max(Component.lfdnr)).where(Component.fk_modell == id)
    )
    max_lfdnr = result.scalar() or 0
    data["lfdnr"] = max_lfdnr + 1
    return await ComponentCRUD.create(db, data)


async def delete_modell_with_components(db: AsyncSession, id: int, company_id: int | None = None):
    await ModellCRUD.get_by_id(db, id, company_id)
    await ensure_modell_writable(db, id)
    await db.execute(delete(Component).where(Component.fk_modell == id))
    return await ModellCRUD.delete(db, id, company_id)


def clone_instance(instance, exclude: set[str] = None) -> dict:
    exclude = exclude or set()
    return {
        key: value
        for key, value in vars(instance).items()
        if not key.startswith("_") and key not in exclude
    }


async def duplicate_modell(db: AsyncSession, id: int, user_id: int, company_id: int | None, new_name: str):
    stmt = (
        select(Modell)
        .where(Modell.id == id)
        .options(selectinload(Modell.components))
    )
    if company_id is not None:
        stmt = stmt.where(Modell.fk_company == company_id)
    result = await db.execute(stmt)
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden oder nicht erlaubt")

    base_data = clone_instance(original, exclude={"id", "name", "components"})
    base_data["name"] = new_name
    base_data["fk_user_id"] = user_id
    base_data["fk_company"] = company_id

    new_modell = Modell(**base_data)
    db.add(new_modell)
    await db.flush()

    for comp in original.components:
        comp_data = clone_instance(comp, exclude={"id", "fk_modell"})
        comp_data["fk_modell"] = new_modell.id
        comp_data["fk_user_id"] = user_id
        comp_data["fk_company"] = company_id
        db.add(Component(**comp_data))

    await db.commit()
    await db.refresh(new_modell)
    return new_modell