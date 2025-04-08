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

router = APIRouter(prefix="/modells", tags=["modells"])


@router.get("", response_model=List[ModellNameDescription])
async def get_modells(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Modell.name, Modell.description))
    rows = result.all()

    # Manuell umwandeln in Pydantic-Objekte (weil select() keine ORM-Modelle gibt)
    return [ModellNameDescription(name=row[0], description=row[1]) for row in rows]

@router.get("/{id}", response_model=ModellIDResponse)
async def get_modell_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Modell).filter(Modell.id == id))
    modell = result.scalar_one_or_none()

    if not modell:
        return {"error": "Modell nicht gefunden"}

    comp_result = await db.execute(select(Component.kompid).filter(Component.fk_modell == id))
    component_ids = comp_result.scalars().all()  # Liste der Komponenten-IDs

    tmu_modell = TMU_Modell(
        aufgabe=modell.aufgabe,
        modell_id=modell.id)
    for component_id in component_ids:
        tmu_modell.addComponent(component_id)

    #constants = tmu_modell.getConstantNeededList()
    constants = tmu_modell.const_needed
    constants_names = [c.name for c in constants]
    return ModellIDResponse(
        name=modell.name,
        description=modell.description,
        constants=sorted(constants_names)
    )

@router.get("/{id}/berechnung")
async def calculate_uncertainty(id : int ,db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Modell).filter(Modell.id == id))
    modell = result.scalar_one_or_none()

    if not modell:
        return {"error": "Modell nicht gefunden"}

    comp_result = await db.execute(select(Component.kompid).filter(Component.fk_modell == id))
    component_ids = comp_result.scalars().all()  # Liste der Komponenten-IDs


    tmu_modell = TMU_Modell(
        aufgabe=modell.aufgabe,
        modell_id=modell.id)
    for component_id in component_ids:
        tmu_modell.append(ComponentFactory.get_component(component_id))

    return tmu_modell.MUPruefverfahren_U()

@router.post("")
async def create_modell(modell: ModellCreate, db: AsyncSession = Depends(get_db)):
    # Erstellt ein neues `Modell` SQLAlchemy-Objekt
    db_modell = Modell(
        name=modell.name,
        description=modell.description,
        geo_me=modell.geo_me,
        geo_mo=modell.geo_mo,
        geo_gn=modell.geo_gn,
        geo_bn=modell.geo_bn,
        tol_fak=modell.tol_fak,
        aufgabe=modell.aufgabe,
        methode=modell.methode,
        gegenstanf=modell.gegenstanf,
        messeinsatz=modell.messeinsatz,
        einstellmass=modell.einstellmass,
        modcreation=modell.modcreation,
        modmod=modell.modmod,
        tsk_ausenmessung=modell.tsk_ausenmessung,
        tsk_innenmessung=modell.tsk_innenmessung,
        tsk_tiefenmessung=modell.tsk_tiefenmessung,
        tsk_hoehenmessung=modell.tsk_hoehenmessung,
        tsk_stufenmessung=modell.tsk_stufenmessung,
        formel=modell.formel,
        formeldesc=modell.formeldesc
    )

    db.add(db_modell)
    await db.commit()
    await db.refresh(db_modell)  # Holt die ID nach dem Commit

    # Komponenten mit der Modell-ID erstellen
    db_components = [
        Component(
            fk_modell=db_modell.id,  # Jetzt ist die ID bekannt
            lfdnr=comp.lfdnr,
            kompid=comp.kompid,
            modltxtid=comp.modltxtid,
            terml0=comp.terml0,
            terml1=comp.terml1,
            wertart=comp.wertart,
            freigrad=comp.freigrad,
            frei_n_1=comp.frei_n_1,
            verteilung=comp.verteilung,
            kflags=comp.kflags
        ) for comp in modell.components
    ]

    db.add_all(db_components)
    await db.commit()

    # Rückgabe des erstellten Modells inklusive Komponenten
    return db_modell