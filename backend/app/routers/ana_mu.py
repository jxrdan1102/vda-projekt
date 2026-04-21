from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import os
from app.models import Component, TEXTKAT, ANAMU, ANAKOMP  # Component = mod_components
from app.database.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.anakomp import AnakompUpdateR, AnakompForAnamuR
from app.schemas.anakonst import AnakonstUpdateR, AnakonstForAnamuR
from app.schemas.anamu import AnamuCreateR, AnamuUpdate, DuplicateAnamu
from app.schemas.anamu import AnamuGetIdR
from app.schemas.anamu import AnamuGetR
from app.services import AnamuService
from app.services.AnamuService import calc_uncertainty
from sqlalchemy import select
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML   # <-- hier
from datetime import date
import pathlib
from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants, parameter_mapping
from sqlalchemy.orm import selectinload
from app.services.component_service.component_factory import ComponentFactory

router = APIRouter(prefix="/anamu", tags=["anamu"])


@router.get("/r", response_model=list[AnamuGetR])
async def get_all_anamusr(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnamuService.get_all_anamus(db, current_user.id)


@router.get("/{id}/r", response_model=AnamuGetIdR)
async def get_anamu_by_idr(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnamuService.get_anamu_by_id(db, id, current_user.id)


@router.post("/r")
async def create_anamur(anamu: AnamuCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    anamu = await AnamuService.create_anamu_with_dependencies(db, anamu, current_user.id)
    return anamu

@router.post("/{id}/r")
async def update_anamu(id: int, anamu: AnamuUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.update_anamu(db, id, anamu.model_dump(exclude_unset=True), current_user.id)
    return {"detail": "Analyseprojekt wurde erfolgreich geändert"}

@router.post("/anakomp/{id}/r")
async def update_anakompr(id: int, anakomp: AnakompUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.update_anakompr(db, id, anakomp.model_dump(exclude_unset=True), current_user.id)
    return {"detail": "Komponente wurde erfolgreich geändert"}


@router.post("/anakonst/{id}/r")
async def update_anakonstr(id: int, anakonst: AnakonstUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.update_anakonstr(db, id, anakonst.model_dump(exclude_unset=True), current_user.id)
    return {"detail": "Konstante wurde erfolgreich geändert"}
@router.get("/anakomp/{id}", response_model=AnakompForAnamuR)
async def get_anakomp(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnamuService.get_anakomp(db, id, current_user.id)

@router.get("/anakonst/{id}", response_model=AnakonstForAnamuR)
async def get_anakonst(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnamuService.get_anakonst(db, id, current_user.id)

@router.get("/{id}/calc/r")
async def calc_uncertainty_route(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await calc_uncertainty(db, id, current_user.id)


@router.delete("/{id}")
async def delete_anamu_by_id(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.delete_anamu(db, id, current_user.id)
    return {"detail": f"Analyseprojekt mit ID {id} wurde gelöscht"}

@router.post("/{id}/duplicate")
async def duplicate_anamu(id: int, req: DuplicateAnamu, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnamuService.duplicate_anamu(db, id, current_user.id, req.name)

def get_id_by_classname(name: str):
    for comp_id, cls in ComponentFactory.COMPONENTS.items():
        if cls.__name__ == name:
            return comp_id
    return None

VERTEILUNG_MAP = {
    1: "Rechteckverteilung",
    2: "Normalverteilung",
    3: "Dreieckverteilung",
}

WERTART_MAP = {
    1: "Halbweite",
    2: "Spannweite",
    3: "Standardabweichung",
}

FREIGRAD_MAP = {
    1: "Unbegrenzt",
    2: "N-1",
}

def map_value(value, mapping):
    if value in (None, "", "null"):
        return ""
    return mapping.get(value, str(value))

async def get_everything_komp(projekt, db: AsyncSession, uncertainty):
    result = []

    CLASSNAME_TO_ID = {
        cls.__name__: comp_id
        for comp_id, cls in ComponentFactory.COMPONENTS.items()
    }

    uncertainty_map = {
        CLASSNAME_TO_ID.get(name): value
        for name, value in uncertainty
    }
        
    # 🔥 Alle kompids sammeln
    kompids = [
        komp.komponente.kompid
        for komp in projekt.anakomp
        if komp.komponente
    ]

    # 🔥 ALLE Texte in EINER Query holen
    text_result = await db.execute(
        select(TEXTKAT).where(TEXTKAT.textnum.in_(kompids))
    )
    text_map = {t.textnum: t.deutsch for t in text_result.scalars()}

    # 🔥 Durchgehen ohne DB Calls
    for komp in projekt.anakomp:
        modcomp = komp.komponente
        if not modcomp:
            continue

        kompid = modcomp.kompid

        instance = ComponentFactory.get_component(
            modell=None,
            type_name=kompid,
            lfdnr=0
        )

        formel = getattr(instance, "formel", None) if instance else None

        text = text_map.get(str(kompid), "Unbekannt")

        if formel:
            result.append({
                "formel": formel,
                "text": text,
                "terml0": komp.terml0,
                "terml1": komp.terml1,
                "wertart": map_value(komp.wertart, WERTART_MAP),
                "freigrad": map_value(komp.freigrad, FREIGRAD_MAP),
                "verteilung": map_value(komp.verteilung, VERTEILUNG_MAP),
                "unsicherheit": uncertainty_map.get(kompid)
            })
    return result


async def get_formeln_und_legende(projekt, db: AsyncSession):
    result = []

    # 🔥 Alle kompids sammeln
    kompids = [
        komp.komponente.kompid
        for komp in projekt.anakomp
        if komp.komponente
    ]

    # 🔥 ALLE Texte in EINER Query holen
    text_result = await db.execute(
        select(TEXTKAT).where(TEXTKAT.textnum.in_(kompids))
    )
    text_map = {t.textnum: t.deutsch for t in text_result.scalars()}
    # 🔥 Durchgehen ohne DB Calls
    for komp in projekt.anakomp:
        modcomp = komp.komponente
        if not modcomp:
            continue

        kompid = modcomp.kompid
        instance = ComponentFactory.get_component(
            modell=None,
            type_name=kompid,
            lfdnr=0
        )

        formel = getattr(instance, "formel", None) if instance else None
        text = text_map.get(str(kompid), "Unbekannt")

        if formel:
            result.append({
                "formel": formel,
                "text": text
            })

    return result





async def get_anakonst_data(projekt):
    result = []

    for konst in projekt.anakonst:
        try:
            enum_key = TKompConstants(konst.constnum)
            mapping = parameter_mapping.get(enum_key, {})

            name = mapping.get("übersetzung") or enum_key.name.replace("TC_", "").replace("_", " ")
            einheit = mapping.get("einheit", "")

        except ValueError:
            name = "Unbekannt"
            einheit = ""

        result.append({
            "name": name,
            "wert": konst.constval,
            "einheit": einheit
        })

    return result

@router.get("/{id}/report")
async def generate_report(    id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), start_date: str = None, end_date: str = None):
    # 🔥 ALLES in einem Load holen
    result = await db.execute(
        select(ANAMU)
        .options(
            selectinload(ANAMU.anakomp)
            .selectinload(ANAKOMP.komponente),
            selectinload(ANAMU.modell),
            selectinload(ANAMU.anakonst)

        )
        .where(ANAMU.id == id)
    )
    uncertainty = await calc_uncertainty(db, id, current_user.id)
    unsicherheit = uncertainty["Unsicherheit"]
    erweiterungsfaktor = uncertainty["Erweiterungsfaktor"]
    uncertainty = uncertainty["Komponenten"]
    projekt = result.scalar_one_or_none()

    # 🔥 Formeln + Legende holen (ohne N+1)
    formel_data = await get_formeln_und_legende(projekt, db)

    komp_data = await get_everything_komp(projekt, db, uncertainty)

    formeln = [f["formel"] for f in formel_data]

    anakonst_data = await get_anakonst_data(projekt)
    # Templates
    BASE_DIR = pathlib.Path(__file__).parents[1]
    TEMPLATES_DIR = BASE_DIR / "templates"
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    if projekt.modell.tsk_ausenmessung:
        aufgabe = "Außenmessung"
    elif projekt.modell.tsk_innenmessung:
        aufgabe = "Innenmessung"
    elif projekt.modell.tsk_tiefenmessung:
        aufgabe = "Tiefenmessung"
    elif projekt.modell.tsk_hoehenmessung:
        aufgabe = "Höhenmessung"
    elif projekt.modell.tsk_stufenmessung:
        aufgabe = "Stufenmessung"

    if projekt.modell.methode == 1:
        methode = "Direkt"
    elif projekt.modell.methode == 2:
        methode = "Direkt mit Einstellung"
    elif projekt.modell.methode == 3:
        methode = "Substitution"
    elif projekt.modell.methode == 4:
        methode = "Differenziell"


    if projekt.modell.geo_me:
        geo_me = "Fläche"
    elif projekt.modell.geo_me:
        geo_me = "Kugel"
    elif projekt.modell.geo_me:
        geo_me = "Zylinder"
    elif projekt.modell.geo_me:
        geo_me = "Bohrung"


    if projekt.modell.geo_mo:
        geo_mo = "Fläche"
    elif projekt.modell.geo_mo:
        geo_mo = "Kugel"
    elif projekt.modell.geo_mo:
        geo_mo = "Zylinder"
    elif projekt.modell.geo_mo:
        geo_mo = "Bohrung"

    template = env.get_template("report.html")
    html = template.render(
        projekt=projekt,
        erweiterungsfaktor=erweiterungsfaktor,
        unsicherheit=unsicherheit,
        everything_komp=komp_data,
        anakonst=anakonst_data,
        aufgabe=aufgabe,
        methode=methode,
        messeinrichtung=geo_me,
        messobjekt= geo_mo,
        formeln=formeln,
        legende=formel_data,
        start_date=start_date,
        end_date=end_date,
        today=date.today()
    )

    pdf = HTML(string=html).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=report.pdf"}
    )

    