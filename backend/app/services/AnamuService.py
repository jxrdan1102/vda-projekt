from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ANAMU import ANAMU, ANAKOMP, ANAKONST
from app.models.components import Component
from app.models.modell import Modell
from app.schemas.anamu import AnamuCreateR
from app.services.BaseCRUD import BaseCRUD
from app.services.ModellService import get_modell_by_id
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell, TMU_ModellSchema

AnamuCRUD = BaseCRUD(ANAMU)
AnakompCRUD = BaseCRUD(ANAKOMP)
AnakonstCRUD = BaseCRUD(ANAKONST)


async def get_anamu_by_id(db: AsyncSession, id: int, user_id: int):
    stmt = (
        select(ANAMU)
        .where(ANAMU.id == id, ANAMU.fk_user_id == user_id)
        .options(
            selectinload(ANAMU.modell),
            selectinload(ANAMU.anakomp),
            selectinload(ANAMU.anakonst),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_anamu_with_dependencies(db: AsyncSession, anamu: AnamuCreateR, user_id: int):
    # AnAMU anlegen
    data = anamu.model_dump()
    data["fk_user"] = user_id
    created_anamu = await AnamuCRUD.create(db, data)

    # Abgeleitete Daten erzeugen
    await add_anakomps(db, created_anamu.id, created_anamu.fk_modell)
    await add_anakonsts(db, created_anamu.id, created_anamu.fk_modell)
    return created_anamu



def build_anakomp(component: Component, fk_anamu: int) -> ANAKOMP:
    return ANAKOMP(
        fk_anamu=fk_anamu,
        fk_mod_components=component.id,
        terml0=component.terml0,
        terml1=component.terml1,
        verteilung=component.verteilung,
        wertart=component.wertart,
        freigrad=component.freigrad,
        frei_n_1=component.frei_n_1
    )


async def add_anakomps(db: AsyncSession, fk_anamu: int, fk_modell: int) -> list[ANAKOMP]:
    stmt = select(Component).where(Component.fk_modell == fk_modell)
    result = await db.execute(stmt)
    components = result.scalars().all()

    if not components:
        raise HTTPException(status_code=404, detail="Keine Komponenten im Modell gefunden")

    anakomps = [build_anakomp(comp, fk_anamu) for comp in components]

    db.add_all(anakomps)
    await db.commit()
    return anakomps


async def add_anakonsts(db: AsyncSession, fk_anamu: int, fk_modell: int) -> list[ANAKONST]:
    # Modell validieren
    stmt = select(Modell).where(Modell.id == fk_modell)
    result = await db.execute(stmt)
    modell = result.scalar_one_or_none()

    if modell is None:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    stmt = select(Component.kompid, Component.lfdnr).where(Component.fk_modell == fk_modell)
    result = await db.execute(stmt)
    components = result.all()

    if not components:
        raise HTTPException(status_code=404, detail="Keine Komponenten für Konstantenberechnung gefunden")

    schema = TMU_ModellSchema(id=modell.id, aufgabe=modell.aufgabe)
    tmodell = TMU_Modell(schema)

    for komp in components:
        tmodell.addComponent(komp.kompid, komp.lfdnr)

    constants = tmodell.const_needed
    if not constants:
        raise HTTPException(status_code=400, detail="Keine Konstanten benötigt laut TMU-Modell")

    anakonsts = [ANAKONST(fk_anamu=fk_anamu, constnum=c.value, constval=None, remark=0) for c in constants]

    db.add_all(anakonsts)
    await db.commit()
    return anakonsts


async def update_anakompr(db: AsyncSession, id: int, data: dict, user_id: int):
    return await AnakompCRUD.update(db, id, data, user_id)


async def update_anakonstr(db: AsyncSession, id: int, data: dict, user_id: int):
    return await AnakonstCRUD.update(db, id, data, user_id)


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
    tcomponent.anzahl_messungen = source.anzahl_messungen


async def calc_uncertainty(db: AsyncSession, id: int, user_id: int):
    anamu = await get_anamu_by_id(db, id, user_id)
    if not anamu:
        raise HTTPException(status_code=404, detail="ANAMU not found")

    modell = await get_modell_by_id(db, anamu.fk_modell, user_id)
    if not modell:
        raise HTTPException(status_code=404, detail="Modell not found")

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
    print (tmodell.const_list)
    return tmodell.MUPruefverfahren_U()

async def delete_anamu(db: AsyncSession, id: int, user_id: int):
    await AnamuCRUD.get_by_id(db, id, user_id)  # Safety check
    await db.execute(delete(ANAKOMP).where(ANAKOMP.fk_anamu == id))
    await db.execute(delete(ANAKONST).where(ANAKONST.fk_anamu == id))
    return await AnamuCRUD.delete(db, id, user_id)