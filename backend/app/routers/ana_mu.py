from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from app.database.database import get_db
from app.models import ANAMU
from app.schemas.anamu import Anamu
from app.schemas.anamu import AnamuCreate
from app.models.ANAMU import ANAKOMP
from app.schemas.anakomp import Anakomp,AnakompUpdate
from app.schemas.anakonst import Anakonst
from app.models.ANAMU import ANAKONST
from app.schemas.anakonst import AnakonstUpdate
from app.database.generic_methods import create_entity_with_children, generic_child_builder, update_model, get_all_generic

from app.database.generic_methods import get_by_foreign_key, get_by_id
from app.models import Modell
from app.schemas.anamu import AnamuBase

from app.models import Component
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_ModellSchema, TMU_Modell

from app.schemas.anamu import AnamuModellidOnly
from app.schemas.component import ComponentKompidOnly

from app.schemas.modell import ModellBase

from app.database.generic_methods import calc_uncertainty

router = APIRouter(prefix="/anamu", tags=["anamu"])

@router.get("", response_model=List[Anamu])
async def get_all_ana_mu(db: AsyncSession = Depends(get_db)):
    return await get_all_generic(
        ANAMU,  # Das ORM-Modell ANAMU
        db,  # Die Datenbank-Sitzung
        pydantic_model=Anamu  # Das Pydantic-Modell, das als Antwortmodell dient
    )

@router.post("")
async def create_anamu(anamu: AnamuCreate, db: AsyncSession = Depends(get_db)):
    db_anamu = ANAMU(**anamu.model_dump(exclude={"anakomps", "anakonst"}))

    await create_entity_with_children(
        db=db,
        entity=db_anamu,
        child_data_list=anamu.anakomps,
        child_builder=generic_child_builder(ANAKOMP, "fk_anamu")
    )

    await create_entity_with_children(
        db=db,
        entity=db_anamu,
        child_data_list=anamu.anakonst,
        child_builder=generic_child_builder(ANAKONST, "fk_anamu")
    )

    return db_anamu

@router.put("/component/{id}")
async def update_anakomp(id: int, anakomp: AnakompUpdate, db: AsyncSession = Depends(get_db)):
    update_data = anakomp.model_dump(exclude_unset=True)
    updated_anakomp = await update_model(db, ANAKOMP, id=id, update_data=update_data)
    return updated_anakomp

@router.put("/constant/{id}")
async def update_anakonst(id: int, anakonst: AnakonstUpdate, db: AsyncSession = Depends(get_db)):
    update_data = anakonst.model_dump(exclude_unset=True)
    updated_anakonst = await update_model(db, ANAKONST, id=id, update_data=update_data)
    return updated_anakonst

@router.get("/{id}")
async def calculate_uncertainty(id: int, db: AsyncSession = Depends(get_db)):
    ana_mu = await get_by_id(ANAMU, id, db, AnamuModellidOnly)
    if not ana_mu:
        return {"error": "ANAMU nicht gefunden"}

    result = await calc_uncertainty(id,ana_mu.fk_modell, db)
    if result is None:
        return {"error": "Modell nicht gefunden"}

    return result
