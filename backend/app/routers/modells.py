from typing import List

from fastapi import APIRouter, HTTPException, Depends
from app.database.database import get_db
from sqlalchemy.future import select
from app.models.modell import Modell
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.modell import ModellCreate

from app.models.components import Component

from app.services.component_service.component_factory import ComponentFactory

from app.schemas.modell import ModellNameDescription

from app.schemas.modell import ModellIDResponse

from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_ModellSchema
from app.database.generic_methods import get_by_foreign_key, get_all_generic, create_entity_with_children, \
    generic_child_builder

from app.schemas.component import ComponentGet

from app.database.generic_methods import get_by_id
from app.schemas.component import ComponentKompidOnly
from app.schemas.modell import ModellBase

from app.database.generic_methods import calc_uncertainty

router = APIRouter(prefix="/modells", tags=["modells"])


@router.get("", response_model=List[ModellNameDescription])
async def get_modells(db: AsyncSession = Depends(get_db)):
    return await get_all_generic(
        Modell,  # Das ORM-Modell
        db,  # Die Datenbank-Sitzung
        pydantic_model=ModellNameDescription  # Das Pydantic-Modell, das als Antwortmodell dient
    )


@router.get("/{id}/components", response_model=List[ComponentGet])
async def get_modell_components(id: int, db: AsyncSession = Depends(get_db)):
    components = await get_by_foreign_key(
        Component,
        Component.fk_modell,
        id,
        db,
        ComponentGet
    )
    return components

@router.get("/{id}", response_model=ModellIDResponse)
async def get_modell_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Modell).filter(Modell.id == id))
    modell = result.scalar_one_or_none()

    if not modell:
        return {"error": "Modell nicht gefunden"}

    # 👉 Komponenten holen per FK
    component_objs = await get_by_foreign_key(Component, Component.fk_modell, id, db)
    component_ids = [comp.kompid for comp in component_objs]


    tmu_modell = TMU_Modell.from_schema_params(aufgabe=modell.aufgabe, modell_id=modell.id)

    for component_id in component_ids:
        tmu_modell.addComponent(component_id)

    # 👉 Response
    return ModellIDResponse(
        name=modell.name,
        description=modell.description,
        constants=tmu_modell.const_needed,
        constantsValue=tmu_modell.const_list
    )


@router.post("")
async def create_modell(modell: ModellCreate, db: AsyncSession = Depends(get_db)):
    db_modell = Modell(**modell.model_dump(exclude={"components"}))

    return await create_entity_with_children(
        db=db,
        entity=db_modell,
        child_data_list=modell.components,
        child_builder=generic_child_builder(Component, "fk_modell")
    )