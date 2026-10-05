# app/routers/modells.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models import ANAMU, Modell, Component, ModellText
from app.models.user import User
from app.routers.auth import get_current_user, get_company_id, require_write
from app.schemas.component import ComponentAddR, ComponentGet
from app.schemas.modell import ModellCreateR, DuplicateRequest
from app.schemas.modell import ModellGetAllR
from app.schemas.modell import ModellGetIdR
from app.schemas.modell import ModellUpdateR
import app.services.ModellService as ModellService
from sqlalchemy import select, func
from fastapi import HTTPException

router = APIRouter(prefix="/modells", tags=["modells"])


@router.get("/r", response_model=list[ModellGetAllR])
async def get_modellsr(
    db: AsyncSession = Depends(get_db),
    company_id: int | None = Depends(get_company_id)
):
    return await ModellService.get_all_modells(db, company_id)


@router.get("/{id}/r", response_model=ModellGetIdR)
async def get_modell_by_idr(
    id: int,
    db: AsyncSession = Depends(get_db),
    company_id: int | None = Depends(get_company_id)
):
    return await ModellService.get_modell_by_id(db, id, company_id)


@router.post("/r")
async def create_modellr(
    modell: ModellCreateR,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    modell = await ModellService.create_modell(db, modell.model_dump(), current_user.id, company_id)
    return modell


@router.post("/{id}/r")
async def update_modellr(
    id: int,
    modell: ModellUpdateR,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    print(modell.model_dump(exclude_unset=True))
    usage_count = await db.scalar(
        select(func.count()).where(ANAMU.fk_modell == id)
    )
    from fastapi.responses import JSONResponse
    if usage_count and usage_count > 0:
        return JSONResponse(
            status_code=409,
            content={
                "detail": {
                    "code": "FK_IN_USE",
                    "count": usage_count,
                    "message": f"Modell wird in {usage_count} Datensatz/Datensätzen verwendet."
                }
            }
        )
    await ModellService.update_modell(db, id, modell.model_dump(exclude_unset=True), company_id)
    if modell.aufgabe_modell == 3:
        stmt = delete(Component).where(Component.fk_modell == id)
        await db.execute(stmt)
        await db.commit()
        components = await alterModell(modell)
        for component in components:
            db.add(Component(**component.model_dump(), fk_modell=id, fk_user_id=current_user.id, fk_company=company_id))
        await db.commit()
    return {"detail": "Modell wurde erfolgreich geändert"}


@router.post("/{id}/copy")
async def copy_modell(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    original = await db.get(Modell, id)
    if not original:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")
    data = {c.name: getattr(original, c.name) for c in Modell.__table__.columns if c.name != "id"}
    data["name"] = f"{original.name} (Kopie)"
    data["fk_user_id"] = current_user.id
    data["fk_company"] = company_id
    new_modell = Modell(**data)
    db.add(new_modell)
    await db.flush()
    old_components = (await db.execute(
        select(Component).where(Component.fk_modell == id)
    )).scalars().all()
    for comp in old_components:
        comp_data = {c.name: getattr(comp, c.name) for c in Component.__table__.columns if c.name != "id"}
        comp_data["fk_modell"] = new_modell.id
        comp_data["fk_user_id"] = current_user.id
        comp_data["fk_company"] = company_id
        db.add(Component(**comp_data))
    await db.commit()
    return {"detail": "Kopie erstellt", "new_id": new_modell.id}


@router.post("/{id}/addComponent")
async def addComponent(
    id: int,
    component: ComponentAddR,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    await ModellService.add_component(db, id, component.model_dump(), current_user.id, company_id)
    print(component.model_dump())
    return {"detail": "Component wurde erfolgreich erstellt"}


@router.delete("/{id}")
async def delete_modell_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    await ModellService.delete_modell_with_components(db, id, company_id)
    print("testiei")
    return {"detail": f"Modell mit ID {id} wurde gelöscht"}


@router.post("/{id}/duplicate")
async def duplicate_modell(
    id: int,
    req: DuplicateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    return await ModellService.duplicate_modell(db, id, current_user.id, company_id, req.name)


@router.post("/{id}/alterModell")
async def alterModell(modell: ModellUpdateR):
    komp_liste = []
    alle_komp = False

    def add(id_):
        komp_liste.append(str(id_))

    e1 = modell.Element1 or ""
    e2 = modell.Element2 or ""
    b1 = modell.Bezug1 or ""
    b2 = modell.Bezug2 or ""

    if modell.aufgabe == 1:
        add(1301)
        add(1320)
        add(1303)
        add(1304)
        add(1323)
        add(1324)
        add(1325)
        add(1326)
        add(1377)
    elif modell.aufgabe == 2:
        add(1312)
        if alle_komp or (modell.abstand == 1 and modell.Element1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]):
            add(1313)
        add(1314)
        if alle_komp or (
                (modell.Element1 in ["Gerade", "Ebene", "Punkt"] and modell.Element2 in ["Gerade", "Ebene", "Punkt"]) or
                (modell.Element1 in ["Gerade", "Ebene", "Punkt"] and modell.Element2 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"])
        ):
            add(1315)
        add(1316)
        if alle_komp or modell.abstand == 1:
            add(1317)
        if alle_komp or modell.taster == 1:
            add(1318)
        if alle_komp or (
                (modell.Element1 in ["Gerade", "Ebene", "Punkt"] and modell.Element2 in ["Gerade", "Ebene", "Punkt"]) or
                (modell.Element1 in ["Gerade", "Ebene", "Punkt"] and modell.Element2 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"]) or
                (modell.Element1 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"] and modell.Element2 in ["Gerade", "Ebene", "Punkt"])
        ):
            add(1319)
        if alle_komp or (
                (modell.Element1 in ["Gerade", "Ebene", "Punkt"] and modell.Element2 in ["Gerade", "Ebene", "Punkt"]) or
                (modell.Element1 in ["Gerade", "Ebene", "Punkt"] and modell.Element2 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"])
        ):
            add(1320)
        add(1321)
        add(1368)
        add(1322)
        add(1323)
        add(1324)
        add(1325)
        add(1326)
        add(1377)
    elif modell.aufgabe == 3:
        if alle_komp or modell.Element1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
            add(1327)
        if alle_komp or modell.Element1 in ["Punkt", "Kreis"]:
            add(1328)
            add(1329)
        if alle_komp or (modell.Element1 in ["Punkt", "Kreis"] and modell.taster1 == 2):
            add(1330)
        if alle_komp or (modell.Element2 in ["Punkt", "Kreis"] and modell.taster1 == 2):
            add(1331)
        if alle_komp or modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
            add(1332)
        if alle_komp or modell.Bezug1 in ["Punkt", "Kreis"]:
            add(1333)
        if alle_komp or modell.Bezug2 in ["Punkt", "Kreis"]:
            add(1334)
        if alle_komp or (modell.Bezug1 in ["Punkt", "Kreis"] and modell.taster2 == 2):
            add(1335)
        if alle_komp or (modell.Bezug2 in ["Punkt", "Kreis"] and modell.taster2 == 2):
            add(1336)
        if alle_komp or modell.taster1 == 2:
            add(1371)
            add(1372)
        add(1338)
        add(1376)
    elif modell.aufgabe == 4:
        add(1350)
        add(1351)
        add(1352)
        add(1353)
        if alle_komp or modell.Bezug2:
            add(1355)
        add(1356)
        add(1374)
        add(1357)
    elif modell.aufgabe == 5:
        if alle_komp or modell.element in [4, 5, 6, 7]:
            add(1310)
        add(1311)
        add(1376)
    elif modell.aufgabe == 6:
        add(1378)
        add(1379)
        add(1380)
        add(1381)
    elif modell.aufgabe == 7:
        add(1391)
        add(1392)
        add(1393)
        add(1394)
        add(1395)
        add(1396)
        add(1397)
        add(1398)
        add(1399)

    result = []
    for kompid in komp_liste:
        entry = ComponentGet(kompid=int(kompid), wertart=5, kflags=1, terml0=0, messpunkt_anzahl=0)
        result.append(entry)
    return result


@router.get("/modell-texts")
async def get_modell_texts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModellText))
    texts = result.scalars().all()
    return texts