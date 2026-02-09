from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models import Component
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.component import ComponentAddR, ComponentGet
from app.schemas.modell import ModellCreateR, DuplicateRequest
from app.schemas.modell import ModellGetAllR
from app.schemas.modell import ModellGetIdR
from app.schemas.modell import ModellUpdateR
from app.services import ModellService

router = APIRouter(prefix="/modells", tags=["modells"])

@router.get("/r", response_model=list[ModellGetAllR])
async def get_modellsr(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await ModellService.get_all_modells(db, current_user.id)

@router.get("/{id}/r", response_model=ModellGetIdR)
async def get_modell_by_idr(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await ModellService.get_modell_by_id(db, id, current_user.id)

@router.post("/r")
async def create_modellr(modell: ModellCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    modell = await ModellService.create_modell(db, modell.model_dump(), current_user.id)
    return modell

@router.post("/{id}/r")
async def update_modellr(id: int, modell: ModellUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(modell.model_dump(exclude_unset=True))
    await ModellService.update_modell(db, id, modell.model_dump(exclude_unset=True), current_user.id)
    if modell.aufgabe_modell == 3:
        stmt = delete(Component).where(Component.fk_modell == id)
        await db.execute(stmt)
        await db.commit()

        components = await alterModell(modell)
        for component in components:
            db.add(Component(**component.model_dump(), fk_modell=id))

        await db.commit()

    return {"detail": "Modell wurde erfolgreich geändert"}

@router.post("/{id}/addComponent")
async def addComponent(id: int, component: ComponentAddR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await ModellService.add_component(db, id, component.model_dump(), current_user.id)
    print (component.model_dump())
    return {"detail": "Component wurde erfolgreich erstellt"}
@router.delete("/{id}")
async def delete_modell_by_id(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await ModellService.delete_modell_with_components(db, id, current_user.id)
    print ("testiei")
    return {"detail": f"Modell mit ID {id} wurde gelöscht"}



@router.post("/{id}/duplicate")
async def duplicate_modell(id: int, req: DuplicateRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await ModellService.duplicate_modell(db, id, current_user.id, req.name)



@router.post("/{id}/alterModell")
async def alterModell(modell: ModellUpdateR):
    komp_liste = []
    alle_komp = False #((modell.admin_mode == True ) and  (modell.allComponents == True)) Testweise auf False gesetzt

    def add(id_):
        komp_liste.append(str(id_))


    # -------------------------------------------------------------
    # DURCHMESSER
    # -------------------------------------------------------------
    if modell.aufgabe == 1:#Durchmesser
        add(1301)
        add(1320)
        add(1303)
        add(1304)
        add(1323)
        add(1324)
        add(1325)
        add(1326)
        add(1377)

    # -------------------------------------------------------------
    # ABSTAND
    # -------------------------------------------------------------
    elif modell.aufgabe == 2: #Abstand
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

    result = []

    for kompid in komp_liste:
        entry = ComponentGet(kompid=int(kompid),wertart=5,kflags=1,terml0=0,messpunkt_anzahl=0)
        result.append(entry)

    return result
