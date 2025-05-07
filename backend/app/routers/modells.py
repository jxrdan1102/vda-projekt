from app.database.database import get_db
from app.database.generic_methods import (
    create_entity_with_children,
    generic_child_builder,
    get_by_foreign_key,
    get_by_id,
    update_model,
)
from app.models.components import Component
from app.models.modell import Modell
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.component import ComponentAddR
from app.schemas.component import ComponentGet, ComponentGetModell
from app.schemas.component import ComponentGetR
from app.schemas.modell import (
    ModellBase,
    ModellCreate,
    ModellIDResponse,
    ModellNameDescription,
    ModellUpdate,
)
from app.schemas.modell import ModellCreateR
from app.schemas.modell import ModellGetAllR
from app.schemas.modell import ModellGetIdR
from app.schemas.modell import ModellUpdateR
from app.services.component_service.EverythinForComponents.TMU_Modell import (
    TMU_Modell,
    TMU_ModellSchema,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/modells", tags=["modells"])





@router.get("/r", response_model=list[ModellGetAllR])
async def get_modellsr(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 👈 Benutzer ziehen
):
    stmt = select(Modell).where(Modell.fk_user_id == current_user.id)
    result = await db.execute(stmt)
    modells = result.scalars().all()  # 👈 alle Modelle als Liste extrahieren
    return modells




@router.get("/{id}/components/r", response_model=list[ComponentGetR])
async def get_modell_componentsr(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Component).where(Component.fk_modell == id)
    result = await db.execute(stmt)
    return result.scalars().all()




@router.post("{id}/addComponent")
async def addComponent(id: int, component=ComponentAddR, db: AsyncSession = Depends(get_db)):
    db_component = Modell(**component.model_dump(), fk_modell=id)
    db.add(db_component)
    await db.commit()
    await db.refresh(db_component)
    return "Komponente wurde erfolgreich hinzugefügt"





@router.get("/{id}/r", response_model=ModellGetIdR)
async def get_modell_by_idr(
    id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = (select(Modell).options(joinedload(Modell.components)).where(Modell.id == id, Modell.fk_user_id == current_user.id))

    result = await db.execute(stmt)
    db_modell = result.unique().scalar_one_or_none()

    if db_modell is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_modell




@router.post("/r")
async def create_modellr(modell: ModellCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_modell = Modell(**modell.model_dump(), fk_user_id = current_user.id)
    db.add(db_modell)
    await db.commit()
    await db.refresh(db_modell)
    return "Modell wurde erfolgreich erstellt"




@router.put("/{id}/r")
async def update_modellr(id:int, modell: ModellUpdateR, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Modell).where(Modell.id == id))
    db_modell = result.scalar_one_or_none()

    if db_modell is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = modell.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_modell, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_modell)

    return "Modell wurde erfolgreich geändert"




@router.delete("/{id}")
async def delete_modell_by_id(id: int, db: AsyncSession = Depends(get_db)):
    modell = await get_by_id(Modell, id, db, ModellBase)
    if not modell:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    await db.execute(delete(Component).where(Component.fk_modell == id))

    await db.delete(modell)
    await db.commit()

    return {"detail": f"Modell mit ID {id} wurde gelöscht"}
