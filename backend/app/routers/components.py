from typing import TypeVar, Type

from fastapi import APIRouter, HTTPException, Depends
from app.services.component_service.component_factory import ComponentFactory

from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell

from app.schemas.component import ComponentRefCreate

from app.schemas.component import ComponentBack
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.component import ComponentRefUpdate

from app.models import Component

router = APIRouter(prefix="/components", tags=["components"])


@router.get("")
def get_components():
    components = ComponentFactory.get_all_components()

    return [ComponentBack(data=k.data,ConstNeeded=k.ConstNeeded) for k in components]


T = TypeVar('T')  # Typ-Variable für alle Modelle

async def update_model(
    db: AsyncSession,
    model_class: Type[T],  # Die Klasse des Modells, z.B. Component, ANAKOMP
    model_id: int,
    update_data: dict
) -> T:
    """
    Allgemeine Update-Funktion für Modelle.
    """
    # Hole die Modellinstanz aus der DB
    result = await db.execute(select(model_class).where(model_class.id == model_id))
    db_instance = result.scalar_one_or_none()

    if db_instance is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Nur die übergebenen Felder aktualisieren
    for key, value in update_data.items():
        setattr(db_instance, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_instance)

    return db_instance


@router.put("/{id}")
async def update_component(id: int, component: ComponentRefUpdate, db: AsyncSession = Depends(get_db)):
    # Model-Daten extrahieren
    update_data = component.model_dump(exclude_unset=True)

    # Allgemeine Update-Funktion aufrufen
    updated_component = await update_model(db, Component, id, update_data)

    return updated_component

@router.get("/{id}")
async def get_component_db(id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Component).filter(Component.id == id))
    component = result.scalar_one_or_none()

    if not component:
        return {"error": "Modell nicht gefunden"}

    return component