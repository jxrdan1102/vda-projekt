from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.database.generic_methods import (
    calc_uncertainty,
    create_entity_with_children,
    generic_child_builder,
    get_all_generic,
    get_by_id,
    update_model,
)
from app.models import ANAMU
from app.models.ANAMU import ANAKOMP, ANAKONST
from app.routers.modells import get_modell_by_id
from app.schemas.anakomp import AnakompUpdate
from app.schemas.anakonst import AnakonstUpdate
from app.schemas.anamu import (
    Anamu,
    AnamuBase,
    AnamuCreate,
    AnamuIdGet,
    AnamuModellidOnly,
)

router = APIRouter(prefix="/anamu", tags=["anamu"])


@router.get("", response_model=list[Anamu])
async def get_all_ana_mu(db: AsyncSession = Depends(get_db)):
    return await get_all_generic(
        ANAMU,  # Das ORM-Modell ANAMU
        db,  # Die Datenbank-Sitzung
        pydantic_model=Anamu,  # Das Pydantic-Modell, das als Antwortmodell dient
    )


@router.get("/test", response_model=AnamuIdGet)
async def get_ana_mu_by_id(id: int, db: AsyncSession = Depends(get_db)):
    ana_mu = await get_by_id(ANAMU, id, db, AnamuBase)
    if not ana_mu:
        raise HTTPException(status_code=404, detail="AnaMU nicht gefunden")

    # 🧠 Logik aus dem anderen Modell-Endpunkt nutzen
    modell_response = await get_modell_by_id(ana_mu.fk_modell, db)
    if isinstance(modell_response, dict) and "error" in modell_response:
        raise HTTPException(status_code=404, detail="Zugehöriges Modell nicht gefunden")

    return AnamuIdGet(
        name=ana_mu.name,
        aenderungszustand=ana_mu.aenderungszustand,
        identnr=ana_mu.identnr,
        modell=modell_response,
    )


@router.post("")
async def create_anamu(anamu: AnamuCreate, db: AsyncSession = Depends(get_db)):
    db_anamu = ANAMU(**anamu.model_dump(exclude={"anakomps", "anakonst"}))

    await create_entity_with_children(
        db=db,
        entity=db_anamu,
        child_data_list=anamu.anakomps,
        child_builder=generic_child_builder(ANAKOMP, "fk_anamu"),
    )

    await create_entity_with_children(
        db=db,
        entity=db_anamu,
        child_data_list=anamu.anakonst,
        child_builder=generic_child_builder(ANAKONST, "fk_anamu"),
    )

    return db_anamu


@router.put("/component/{id}")
async def update_anakomp(
    id: int, anakomp: AnakompUpdate, db: AsyncSession = Depends(get_db)
):
    update_data = anakomp.model_dump(exclude_unset=True)
    updated_anakomp = await update_model(db, ANAKOMP, id=id, update_data=update_data)
    return updated_anakomp


@router.put("/constant/{id}")
async def update_anakonst(
    id: int, anakonst: AnakonstUpdate, db: AsyncSession = Depends(get_db)
):
    update_data = anakonst.model_dump(exclude_unset=True)
    updated_anakonst = await update_model(db, ANAKONST, id=id, update_data=update_data)
    return updated_anakonst


@router.get("/{id}")
async def calculate_uncertainty(id: int, db: AsyncSession = Depends(get_db)):
    ana_mu = await get_by_id(ANAMU, id, db, AnamuModellidOnly)
    if not ana_mu:
        return {"error": "ANAMU nicht gefunden"}

    result = await calc_uncertainty(id, ana_mu.fk_modell, db)
    if result is None:
        return {"error": "Modell nicht gefunden"}

    return result


@router.delete("/{id}")
async def delete_modell_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ANAMU).where(ANAMU.id == id))
    anamu = result.scalar_one_or_none()
    if not anamu:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    await db.execute(delete(ANAKOMP).where(ANAKOMP.fk_anamu == id))
    await db.execute(delete(ANAKONST).where(ANAKONST.fk_anamu == id))

    await db.delete(anamu)
    await db.commit()

    return {"detail": f"Analyseprojekt mit ID {id} wurde gelöscht"}
