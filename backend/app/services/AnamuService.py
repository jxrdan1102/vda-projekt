from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy import select
from app.models.ANAMU import ANAMU, ANAKOMP, ANAKONST
from app.models.components import Component
from app.models.modell import Modell
from app.schemas.anamu import AnamuCreateR
from app.services.BaseCRUD import BaseCRUD
from app.services.ModellService import get_modell_by_id
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell, TMU_ModellSchema

AnamuCRUD = BaseCRUD(ANAMU)
AnakompCRUD = BaseCRUD(ANAKOMP)
AnakorstCRUD = BaseCRUD(ANAKONST)


async def get_all_anamus(db: AsyncSession, user_id: int, company_id: int | None = None):
    stmt = select(ANAMU).options(selectinload(ANAMU.modell))
    if company_id is not None:
        stmt = stmt.where(ANAMU.fk_company == company_id)
    else:
        stmt = stmt.where(ANAMU.fk_user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_anamu_by_id(db: AsyncSession, id: int, user_id: int, company_id: int | None = None):
    stmt = (
        select(ANAMU)
        .options(
            selectinload(ANAMU.anakomp).selectinload(ANAKOMP.komponente),
            selectinload(ANAMU.modell),
            selectinload(ANAMU.anakonst),
            selectinload(ANAMU.kmg),
        )
        .where(ANAMU.id == id)
    )
    if company_id is not None:
        stmt = stmt.where(ANAMU.fk_company == company_id)
    else:
        stmt = stmt.where(ANAMU.fk_user_id == user_id)
    result = await db.execute(stmt)
    anamu = result.scalar_one_or_none()
    if not anamu:
        raise HTTPException(status_code=404, detail="Analyseprojekt nicht gefunden")
    return anamu

async def get_anakomp(db: AsyncSession, id: int, user_id: int, company_id: int | None = None):
    stmt = select(ANAKOMP).where(ANAKOMP.id == id)
    if company_id is not None:
        stmt = stmt.where(ANAKOMP.fk_company == company_id)
    else:
        stmt = stmt.where(ANAKOMP.fk_user_id == user_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Anakomp nicht gefunden")
    return obj


async def get_anakonst(db: AsyncSession, id: int, user_id: int, company_id: int | None = None):
    stmt = select(ANAKONST).where(ANAKONST.id == id)
    if company_id is not None:
        stmt = stmt.where(ANAKONST.fk_company == company_id)
    else:
        stmt = stmt.where(ANAKONST.fk_user_id == user_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Anakonst nicht gefunden")
    return obj

async def create_anamu_with_dependencies(db: AsyncSession, anamu: AnamuCreateR, user_id: int, company_id: int | None = None):
    new_anamu = ANAMU(
        **anamu.model_dump(),
        fk_user_id=user_id,
        fk_company=company_id,
    )
    db.add(new_anamu)
    await db.commit()
    await db.refresh(new_anamu)
    return new_anamu


async def update_anamu(db: AsyncSession, id: int, data: dict, user_id: int, company_id: int | None = None):
    stmt = select(ANAMU).where(ANAMU.id == id)
    if company_id is not None:
        stmt = stmt.where(ANAMU.fk_company == company_id)
    else:
        stmt = stmt.where(ANAMU.fk_user_id == user_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Analyseprojekt nicht gefunden")
    for key, value in data.items():
        setattr(existing, key, value)
    await db.commit()
    return existing


async def update_anakompr(db: AsyncSession, id: int, data: dict, user_id: int, company_id: int | None = None):
    stmt = select(ANAKOMP).where(ANAKOMP.id == id)
    if company_id is not None:
        stmt = stmt.where(ANAKOMP.fk_company == company_id)
    else:
        stmt = stmt.where(ANAKOMP.fk_user_id == user_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Komponente nicht gefunden")
    for key, value in data.items():
        setattr(existing, key, value)
    await db.commit()
    return existing


async def update_anakonstr(db: AsyncSession, id: int, data: dict, user_id: int, company_id: int | None = None):
    stmt = select(ANAKONST).where(ANAKONST.id == id)
    if company_id is not None:
        stmt = stmt.where(ANAKONST.fk_company == company_id)
    else:
        stmt = stmt.where(ANAKONST.fk_user_id == user_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Konstante nicht gefunden")
    for key, value in data.items():
        setattr(existing, key, value)
    await db.commit()
    return existing


async def delete_anamu(db: AsyncSession, id: int, user_id: int, company_id: int | None = None):
    stmt = select(ANAMU).where(ANAMU.id == id)
    if company_id is not None:
        stmt = stmt.where(ANAMU.fk_company == company_id)
    else:
        stmt = stmt.where(ANAMU.fk_user_id == user_id)
    result = await db.execute(stmt)
    anamu = result.scalar_one_or_none()
    if not anamu:
        raise HTTPException(status_code=404, detail="Analyseprojekt nicht gefunden")
    await db.delete(anamu)
    await db.commit()


async def duplicate_anamu(db: AsyncSession, id: int, user_id: int, company_id: int | None, new_name: str):
    stmt = (
        select(ANAMU)
        .options(
            selectinload(ANAMU.anakomp),
            selectinload(ANAMU.anakonst),
        )
        .where(ANAMU.id == id)
    )
    if company_id is not None:
        stmt = stmt.where(ANAMU.fk_company == company_id)
    else:
        stmt = stmt.where(ANAMU.fk_user_id == user_id)
    result = await db.execute(stmt)
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Analyseprojekt nicht gefunden")

    new_anamu = ANAMU(
        name=new_name,
        fk_modell=original.fk_modell,
        aenderungszustand=original.aenderungszustand,
        identnr=original.identnr,
        partno=original.partno,
        remark=original.remark,
        tolfaktor=original.tolfaktor,
        tsk_aufgabe=original.tsk_aufgabe,
        fk_kmg=original.fk_kmg,
        fk_user_id=user_id,
        fk_company=company_id,
    )
    db.add(new_anamu)
    await db.flush()

    for komp in original.anakomp:
        new_komp = ANAKOMP(
            fk_anamu=new_anamu.id,
            fk_mod_components=komp.fk_mod_components,
            remark=komp.remark,
            terml0=komp.terml0,
            terml1=komp.terml1,
            wertart=komp.wertart,
            freigrad=komp.freigrad,
            frei_n_1=komp.frei_n_1,
            verteilung=komp.verteilung,
            anzahl_messungen=komp.anzahl_messungen,
            messpunkt_anzahl=komp.messpunkt_anzahl,
            fk_user_id=user_id,
            fk_company=company_id,
        )
        db.add(new_komp)

    for konst in original.anakonst:
        new_konst = ANAKONST(
            fk_anamu=new_anamu.id,
            constnum=konst.constnum,
            constval=konst.constval,
            remark=konst.remark,
            fk_user_id=user_id,
            fk_company=company_id,
        )
        db.add(new_konst)

    await db.commit()
    await db.refresh(new_anamu)
    return new_anamu


async def get_anakonst_data(projekt):
    from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants, parameter_mapping
    result = []
    for konst in projekt.anakonst:
        const_enum = None
        for k in TKompConstants:
            if k.value == konst.constnum:
                const_enum = k
                break
        if const_enum and const_enum in parameter_mapping:
            mapping = parameter_mapping[const_enum]
            result.append({
                "name": mapping.get("label", const_enum.name),
                "wert": konst.constval,
                "einheit": mapping.get("einheit", ""),
            })
        else:
            result.append({
                "name": f"Konstante {konst.constnum}",
                "wert": konst.constval,
                "einheit": "",
            })
    return result


async def calc_uncertainty(db: AsyncSession, id: int, user_id: int, company_id: int | None = None):
    anamu = await get_anamu_by_id(db, id, user_id, company_id)
    if not anamu:
        raise HTTPException(status_code=404, detail="ANAMU not found")
    modell = await get_modell_by_id(db, anamu.fk_modell, company_id)
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
    if modell.aufgabe_modell == 3:
        await tmodell.setKMGConstValue(anamu.fk_kmg, db)
    if anamu.tolfaktor == 1:
        tmodell.mit_berechnung_toleranzfaktor = True
    return tmodell.MUPruefverfahren_U()


def map_component_data(tcomponent, source):
    for attr in ['terml0', 'terml1', 'wertart', 'freigrad', 'frei_n_1', 'verteilung',
                 'messpunkt_anzahl', 'anzahl_messungen', 'modltxtid', 'remark']:
        val = getattr(source, attr, None)
        if val is not None:
            tcomponent.setData({attr: val})