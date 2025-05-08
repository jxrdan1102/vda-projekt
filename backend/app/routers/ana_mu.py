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
from app.models import Component
from app.models import Modell
from app.models.ANAMU import ANAKOMP, ANAKONST
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.anakomp import AnakompUpdate
from app.schemas.anakomp import AnakompUpdateR
from app.schemas.anakonst import AnakonstUpdate
from app.schemas.anakonst import AnakonstUpdateR
from app.schemas.anamu import (
    Anamu,
    AnamuBase,
    AnamuCreate,
    AnamuIdGet,
    AnamuModellidOnly,
)
from app.schemas.anamu import AnamuCreateR
from app.schemas.anamu import AnamuGetIdR
from app.schemas.anamu import AnamuGetR
from app.schemas.component import TMU_Komponente_Pydantic
from app.schemas.modell import ModellForAnamuR
from app.schemas.modell import TMU_Modell_Pydantic
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_ModellSchema, TMU_Modell
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/anamu", tags=["anamu"])


@router.get("/r", response_model=list[AnamuGetR])
async def get_all_anamusr(db: AsyncSession = Depends(get_db)):
    stmt = select(ANAMU)
    result = await db.execute(stmt)
    anamus = result.scalars().all()  # 👈 alle Modelle als Liste extrahieren
    return anamus




@router.get("/{id}/r", response_model=AnamuGetIdR)
async def get_ana_mu_by_idr(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ANAMU).options(joinedload(ANAMU.modell),joinedload(ANAMU.anakomp),joinedload(ANAMU.anakonst)).where(ANAMU.id == id)
    result = await db.execute(stmt)
    anamu = result.unique().scalar_one_or_none()
    return anamu




async def addAnakomps(fk_anamu: int, fk_modell: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Component.id, Component.terml0, Component.terml1, Component.verteilung, Component.wertart,Component.freigrad,Component.frei_n_1).where(Component.fk_modell == fk_modell)
    result = await db.execute(stmt)
    components = result.all()
    anakomps = [ANAKOMP(fk_anamu=fk_anamu,fk_mod_components=c.id,terml0=c.terml0,terml1=c.terml1,verteilung=c.verteilung,wertart=c.wertart,freigrad=c.freigrad,frei_n_1=c.frei_n_1,) for c in components]
    db.add_all(anakomps)
    await db.commit()
    return


async def addAnakonsts(fk_anamu: int, fk_modell: int, db: AsyncSession):
    stmt = select(Component.kompid,Component.lfdnr).where(Component.fk_modell == fk_modell)
    result = await db.execute(stmt)
    components = result.all()
    stmt = select(Modell.id, Modell.aufgabe).where(Modell.id == fk_modell)
    result = await db.execute(stmt)
    row = result.first()
    if row:
        modell_id, aufgabe = row
        tschema = TMU_ModellSchema(id=modell_id, aufgabe=aufgabe)
    else:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")
    tmodell = TMU_Modell(tschema)
    for component in components:
        tmodell.addComponent(component.kompid,component.lfdnr)
    constants = tmodell.const_needed
    print("KONSTANTEN", constants)
    anakonsts = [ANAKONST(fk_anamu=fk_anamu, constnum=c.value, constval=None,remark=0 ) for c in constants]
    db.add_all(anakonsts)
    await db.commit()
    return


@router.post("/r")
async def create_anamur(anamu: AnamuCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_anamu = ANAMU(**anamu.model_dump(), fk_user=current_user.id)
    db.add(db_anamu)
    await db.commit()
    await db.refresh(db_anamu)
    await addAnakomps(db_anamu.id,db_anamu.fk_modell, db)
    await addAnakonsts(db_anamu.id,db_anamu.fk_modell, db)
    return "Analyseprojekt wurde erfolgreich erstellt"




@router.put("/anakomp/{id}/r")
async def update_anakompr(id: int, anakomp: AnakompUpdateR, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ANAKOMP).where(ANAKOMP.id == id))
    db_modell = result.scalar_one_or_none()

    if db_modell is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = anakomp.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_modell, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_modell)

    return "Konstante wurde erfolgreich geändert"



@router.put("/anakonst/{id}/r")
async def update_anakonstr(id: int, anakonst: AnakonstUpdateR, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ANAKONST).where(ANAKONST.id == id))
    db_anakonst = result.scalar_one_or_none()

    if db_anakonst is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = anakonst.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_anakonst, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_anakonst)

    return "Konstante wurde erfolgreich geändert"


def map_component_data(tcomponent, source):
    tcomponent.setData({
        'KennwertArt': source.wertart,
        'Freiheitsgrad': source.freigrad,
        'FreiN_minus_1': source.frei_n_1,
        'TermL0': source.terml0,
        'TermL1': source.terml1,
        'Verteilung': source.verteilung
    })
    tcomponent.messpunkt_anzahl = source.messpunkt_anzahl

@router.get("/{id}/calc/r")
async def calc_uncertainty(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ANAMU).options(
        joinedload(ANAMU.anakonst),
        joinedload(ANAMU.anakomp)
    ).where(ANAMU.id == id)
    result = await db.execute(stmt)
    anamu = result.unique().scalar_one_or_none()
    if anamu is None:
        raise HTTPException(status_code=404, detail="Item not found")

    stmt = select(Modell).options(
        joinedload(Modell.components)
    ).where(Modell.id == anamu.fk_modell)
    result = await db.execute(stmt)
    modell = result.unique().scalar_one_or_none()
    if modell is None:
        raise HTTPException(status_code=404, detail="Item not found")

    tschema = TMU_ModellSchema.model_validate(modell)
    tmodell = TMU_Modell(tschema)

    components_map = {m.lfdnr: m for m in modell.components}
    anakomps_map = {a.fk_mod_components: a for a in anamu.anakomp}

    for component in modell.components:
        tmodell.addComponent(component.kompid, component.lfdnr)

    for tcomponent in tmodell:
        mcomponent = components_map.get(tcomponent.lfdnr)
        if mcomponent:
            tcomponent.id = mcomponent.id
            map_component_data(tcomponent, mcomponent)
            tcomponent.setData({'Flags': mcomponent.kflags})

        acomp = anakomps_map.get(tcomponent.id)
        if acomp:
            map_component_data(tcomponent, acomp)

    await tmodell.setConstValue(anamu.id, db)

    return tmodell.MUPruefverfahren_U()


@router.delete("/{id}")
async def delete_anamu_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ANAMU).where(ANAMU.id == id))
    anamu = result.scalar_one_or_none()
    if not anamu:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    await db.execute(delete(ANAKOMP).where(ANAKOMP.fk_anamu == id))
    await db.execute(delete(ANAKONST).where(ANAKONST.fk_anamu == id))

    await db.delete(anamu)
    await db.commit()

    return {"detail": f"Analyseprojekt mit ID {id} wurde gelöscht"}
