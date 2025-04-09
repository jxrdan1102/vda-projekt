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

from app.routers.components import update_model

router = APIRouter(prefix="/anamu", tags=["anamu"])


@router.get("",response_model=List[Anamu])
async def get_all_ana_mu(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ANAMU))
    anamu = result.scalars().all()
    return anamu

@router.post("")
async def create_anamu(anamu: AnamuCreate, db: AsyncSession = Depends(get_db)):
    db_anamu = ANAMU(fk_modell = anamu.fk_modell,
                     name = anamu.name,
                     aenderungszustand = anamu.aenderungszustand,
                     identnr = anamu.identnr,
                     partno = anamu.identnr,
                     remark = anamu.remark,
                     creation = anamu.creation,
                     modify = anamu.modify,
                     user = anamu.user,
                     tolfaktor = anamu.tolfaktor,
                     tsk_aufgabe = anamu.tsk_aufgabe,
                     kmg_ident = anamu.kmg_ident
                     )
    db.add(db_anamu)
    await db.commit()
    await db.refresh(db_anamu)  # Holt die ID nach dem Commit

    # Komponenten mit der Modell-ID erstellen
    db_anakomps = [
        Anakomp(
    fk_anamu = anakomp.fk_anamu,
    fk_mod_components = anakomp.fk_mod_components,
    remark = anakomp.fk_remark,
    terml0 = anakomp.terml0,
    terml1 = anakomp.terml1,
    wertart = anakomp.wertart,
    freigrad = anakomp.freigrad,
    frei_n_1 = anakomp.frei_n_1,
    verteilung = anakomp.verteilung,
        )for anakomp in anamu.anakomps
    ]
    db.add_all(db_anakomps)
    await db.commit()

    db_anakonst = [
        Anakonst(
            fk_anamu = anakonst.fk_anamu,
            constnum = anakonst.constnum,
            constval = anakonst.constval,
            remark = anakonst.remark,
        ) for anakonst in anamu.anakonst
    ]
    db.add_all(db_anakomps)
    await db.commit()

    return db_anamu


@router.put("/component/{id}")
async def update_anakomp(id: int, anakomp: AnakompUpdate, db: AsyncSession = Depends(get_db)):
    # Model-Daten extrahieren
    update_data = anakomp.model_dump(exclude_unset=True)

    # Allgemeine Update-Funktion aufrufen
    updated_anakomp = await update_model(db, ANAKOMP, id, update_data)

    return updated_anakomp

@router.put("/constant/{id}")
async def update_anakonst(id: int,anakonst: AnakonstUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ANAKONST).where(ANAKONST.id == id))
    db_anakonst = result.scalar_one_or_none()

    if db_anakonst is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Nur die übergebenen Felder aktualisieren
    update_data = anakonst.model_dump(exclude_unset=True)  # Nur vorhandene Werte nehmen
    for key, value in update_data.items():
        setattr(db_anakonst, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_anakonst)

    return db_anakonst