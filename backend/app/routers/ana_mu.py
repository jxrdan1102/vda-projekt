from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import os
from app.models import Component, TEXTKAT, ANAMU, ANAKOMP  # Component = mod_components
from app.database.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user, get_company_id, require_write
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
from app.services.ModellService import get_modell_by_id
from app.services.AnamuService import map_component_data
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell, TMU_ModellSchema
import math
from fastapi import HTTPException
router = APIRouter(prefix="/anamu", tags=["anamu"])


@router.get("/r", response_model=list[AnamuGetR])
async def get_all_anamusr(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), company_id: int | None = Depends(get_company_id)):
    return await AnamuService.get_all_anamus(db, current_user.id, company_id)


@router.get("/{id}/r", response_model=AnamuGetIdR)
async def get_anamu_by_idr(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), company_id: int | None = Depends(get_company_id)):
    return await AnamuService.get_anamu_by_id(db, id, current_user.id, company_id)


@router.post("/r")
async def create_anamur(anamu: AnamuCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    anamu = await AnamuService.create_anamu_with_dependencies(db, anamu, current_user.id, company_id)
    return anamu


@router.post("/{id}/r")
async def update_anamu(id: int, anamu: AnamuUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    await AnamuService.update_anamu(db, id, anamu.model_dump(exclude_unset=True), current_user.id, company_id)
    return {"detail": "Analyseprojekt wurde erfolgreich geändert"}


@router.post("/anakomp/{id}/r")
async def update_anakompr(id: int, anakomp: AnakompUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    await AnamuService.update_anakompr(db, id, anakomp.model_dump(exclude_unset=True), current_user.id, company_id)
    return {"detail": "Komponente wurde erfolgreich geändert"}

@router.post("/anakonst/{id}/r")
async def update_anakonstr(id: int, anakonst: AnakonstUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    await AnamuService.update_anakonstr(db, id, anakonst.model_dump(exclude_unset=True), current_user.id, company_id)
async def update_anakonstr(id: int, anakonst: AnakonstUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    await AnamuService.update_anakonstr(db, id, anakonst.model_dump(exclude_unset=True), current_user.id, company_id)
    return {"detail": "Konstante wurde erfolgreich geändert"}


@router.get("/anakomp/{id}", response_model=AnakompForAnamuR)
async def get_anakomp(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), company_id: int | None = Depends(get_company_id)):
    return await AnamuService.get_anakomp(db, id, current_user.id, company_id)


@router.get("/anakonst/{id}", response_model=AnakonstForAnamuR)
async def get_anakonst(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), company_id: int | None = Depends(get_company_id)):
    return await AnamuService.get_anakonst(db, id, current_user.id, company_id)


@router.get("/{id}/calc/r")
async def calc_uncertainty_route(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), company_id: int | None = Depends(get_company_id)):
    return await calc_uncertainty(db, id, current_user.id, company_id)


@router.delete("/{id}")
async def delete_anamu_by_id(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    await AnamuService.delete_anamu(db, id, current_user.id, company_id)
    return {"detail": f"Analyseprojekt mit ID {id} wurde gelöscht"}


@router.post("/{id}/duplicate")
async def duplicate_anamu(id: int, req: DuplicateAnamu, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_write), company_id: int | None = Depends(get_company_id)):
    return await AnamuService.duplicate_anamu(db, id, current_user.id, company_id, req.name)

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

AUFGABE_3D_MAP = {
    1: "Durchmesser",
    2: "Abstand",
    3: "Richtung",
    4: "Koaxialität",
    5: "Form",
    6: "Winkel",
    7: "Position",
}

def asciiformel(formel: str) -> str:
    s = formel
    f = ""

    def test(tok: str) -> bool:
        nonlocal s
        if s[:len(tok)].upper() == tok.upper():
            s = s[len(tok):]
            return True
        return False

    while s:
        if test('<sub>'):
            f += '('
        elif test('</sub>'):
            f += ')'
        elif test('&Delta;'):
            f += 'Delta '
        elif test('&alpha;'):
            f += 'a'
        elif test('&phi;'):
            f += 'Phi'
        elif test('&eta;'):
            f += 'Eta'
        elif test('&psi;'):
            f += 'Psi'
        elif test('&theta;'):
            f += 'Theta'
        else:
            f += s[0]
            s = s[1:]

    if f:
        f = ': ' + f

    return f



def map_value(value, mapping):
    if value in (None, "", "null"):
        return ""
    return mapping.get(value, str(value))

async def get_everything_komp(projekt, db: AsyncSession, uncertainty, tmodell):
    result = []

    CLASSNAME_TO_ID = {
        cls.__name__: comp_id
        for comp_id, cls in ComponentFactory.COMPONENTS.items()
    }

    uncertainty_map = {
        CLASSNAME_TO_ID.get(name): value
        for name, value in uncertainty
    }

    kompids = [
        komp.komponente.kompid
        for komp in projekt.anakomp
        if komp.komponente
    ]

    text_result = await db.execute(
        select(TEXTKAT).where(TEXTKAT.textnum.in_(kompids))
    )
    text_map = {t.textnum: t.deutsch for t in text_result.scalars()}

    formel_map = {tc.id: tc.formel for tc in tmodell if tc.id is not None}

    for komp in projekt.anakomp:
        modcomp = komp.komponente
        if not modcomp:
            continue

        kompid = modcomp.kompid
        formel = formel_map.get(modcomp.id)
        text = text_map.get(str(kompid), text_map.get(kompid, "Unbekannt"))

        if formel:
            result.append({
                "formel": asciiformel(formel),
                "text": text,
                "terml0": komp.terml0,
                "terml1": komp.terml1,
                "wertart": map_value(komp.wertart, WERTART_MAP),
                "freigrad": map_value(komp.freigrad, FREIGRAD_MAP),
                "verteilung": map_value(komp.verteilung, VERTEILUNG_MAP),
                "unsicherheit": uncertainty_map.get(kompid)
            })
    # Sortieren nach Unsicherheit absteigend
    result.sort(key=lambda e: e["unsicherheit"] or 0, reverse=True)

    # Max-Unsicherheit für Balken berechnen
    max_u = max((e["unsicherheit"] for e in result if e["unsicherheit"] is not None), default=1)
    for e in result:
        e["unsicherheit_pct"] = round((e["unsicherheit"] / max_u) * 100, 1) if e["unsicherheit"] is not None else 0

    return result


async def get_formeln_und_legende(projekt, db: AsyncSession, tmodell):
    result = []

    kompids = [
        komp.komponente.kompid
        for komp in projekt.anakomp
        if komp.komponente
    ]

    text_result = await db.execute(
        select(TEXTKAT).where(TEXTKAT.textnum.in_(kompids))
    )
    text_map = {t.textnum: t.deutsch for t in text_result.scalars()}

    formel_map = {tc.id: tc.formel for tc in tmodell if tc.id is not None}

    for komp in projekt.anakomp:
        modcomp = komp.komponente
        if not modcomp:
            continue

        kompid = modcomp.kompid
        formel = formel_map.get(modcomp.id)
        text = text_map.get(str(kompid), text_map.get(kompid, "Unbekannt"))

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
async def generate_report(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user), company_id: int | None = Depends(get_company_id), start_date: str = None, end_date: str = None, extended: bool = False):
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
    projekt = result.scalar_one_or_none()
    if not projekt:
        raise HTTPException(status_code=404, detail="Analyseprojekt nicht gefunden")

    # ── Zentrales TMU_Modell EINMAL bauen ──
    modell_db = await get_modell_by_id(db, projekt.fk_modell, company_id)
    tschema = TMU_ModellSchema.model_validate(modell_db)
    tmodell = TMU_Modell(tschema)

    components_map = {m.lfdnr: m for m in modell_db.components}
    anakomps_map = {a.fk_mod_components: a for a in projekt.anakomp}

    for component in modell_db.components:
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

    await tmodell.setConstValue(projekt.id, db)
    if modell_db.aufgabe_modell == 3:
        await tmodell.setKMGConstValue(projekt.fk_kmg, db)
    if projekt.tolfaktor == 1:
        tmodell.mit_berechnung_toleranzfaktor = True

    uncertainty = tmodell.MUPruefverfahren_U()
    unsicherheit = uncertainty["Unsicherheit"]
    erweiterungsfaktor = uncertainty["Erweiterungsfaktor"]
    uncertainty = uncertainty["Komponenten"]

    formel_data = await get_formeln_und_legende(projekt, db, tmodell)
    formeln = [f["formel"] for f in formel_data]

    if modell_db.aufgabe_modell == 3:
        komp_data = await get_everything_komp_3d(projekt, db, uncertainty, tmodell)
        template_name = "report_3d.html"
    else:
        komp_data = await get_everything_komp(projekt, db, uncertainty, tmodell)
        template_name = "report.html"

    anakonst_data = await get_anakonst_data(projekt)
    BASE_DIR = pathlib.Path(__file__).parents[1]
    TEMPLATES_DIR = BASE_DIR / "templates"
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    if projekt.modell.aufgabe_modell == 3:
        aufgabe = AUFGABE_3D_MAP.get(projekt.modell.aufgabe, "Unbekannt")
    else:
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
        else:
            aufgabe = "Unbekannt"

    if projekt.modell.methode == 1:
        methode = "Direkt"
    elif projekt.modell.methode == 2:
        methode = "Direkt mit Einstellung"
    elif projekt.modell.methode == 3:
        methode = "Substitution"
    elif projekt.modell.methode == 4:
        methode = "Differenziell"
    else:
        methode = "Unbekannt"

    if projekt.modell.geo_me == 1:
        geo_me = "Fläche"
    elif projekt.modell.geo_me == 2:
        geo_me = "Kugel"
    elif projekt.modell.geo_me == 3:
        geo_me = "Zylinder"
    elif projekt.modell.geo_me == 4:
        geo_me = "Bohrung"
    else:
        geo_me = "Unbekannt"

    if projekt.modell.geo_mo == 1:
        geo_mo = "Fläche"
    elif projekt.modell.geo_mo == 2:
        geo_mo = "Kugel"
    elif projekt.modell.geo_mo == 3:
        geo_mo = "Zylinder"
    elif projekt.modell.geo_mo == 4:
        geo_mo = "Bohrung"
    else:
        geo_mo = "Unbekannt"

    extended_data = None
    if extended:
        print("extended ist True, lade extended_data...")
        extended_data = await get_extended_report_data(projekt, db, tmodell)
        print("extended_data Länge:", len(extended_data) if extended_data else 0)

    template = env.get_template(template_name)
    html = template.render(
        projekt=projekt,
        erweiterungsfaktor=erweiterungsfaktor,
        unsicherheit=unsicherheit,
        everything_komp=komp_data,
        anakonst=anakonst_data,
        aufgabe=aufgabe,
        formeln=formeln,
        legende=formel_data,
        start_date=start_date,
        end_date=end_date,
        today=date.today(),
        extended=extended,
        extended_data=extended_data,
    )
    pdf = HTML(string=html).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=report.pdf"}
    )


EINHEIT_MAP = {k: v.get("einheit", "") for k, v in parameter_mapping.items()}
LABEL_MAP = {k.name: v.get("übersetzung", k.name) for k, v in parameter_mapping.items()}
def _format_wert(value, einheit: str = "", digits: int = 6):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        rounded = round(value, digits)
        formatted = f"{rounded:.{digits}f}".rstrip('0').rstrip('.')
        formatted = formatted.replace('.', ',')
        if einheit:
            return f"{formatted} {einheit}"
        return formatted
    except Exception:
        return str(value).replace('.', ',') if value is not None else None

def _safe_round(value, digits: int = 6):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        rounded = round(value, digits)
        formatted = f"{rounded:.{digits}f}".rstrip('0').rstrip('.')
        return formatted.replace('.', ',')
    except Exception:
        return str(value).replace('.', ',') if value is not None else None

async def get_extended_report_data(projekt, db: AsyncSession, tmodell):
    kompids = [tcomponent.komp_id for tcomponent in tmodell]
    text_result = await db.execute(
        select(TEXTKAT).where(TEXTKAT.textnum.in_(kompids))
    )
    text_map = {t.textnum: t.deutsch for t in text_result.scalars()}

    extended_components = []
    for komp in tmodell:
        try:
            verteilung = komp.data.Verteilung.name if hasattr(komp.data.Verteilung, "name") else str(komp.data.Verteilung)
            kennwertart = komp.data.KennwertArt.name if hasattr(komp.data.KennwertArt, "name") else str(komp.data.KennwertArt)
            freiheitsgrad = komp.data.Freiheitsgrad.name if hasattr(komp.data.Freiheitsgrad, "name") else str(komp.data.Freiheitsgrad)

            benoetigte_konstanten = []
            for const in komp.ConstNeeded:
                try:
                    wert = komp.modell.const_list.const_map[const]
                except Exception:
                    wert = None

                if isinstance(const, TKompConstants):
                    mapping_entry = parameter_mapping.get(const, {})
                else:
                    try:
                        enum_val = TKompConstants[str(const)]
                        mapping_entry = parameter_mapping.get(enum_val, {})
                    except (KeyError, Exception):
                        mapping_entry = {}

                einheit = mapping_entry.get("einheit", "")
                label = mapping_entry.get("übersetzung", "") or (const.name if hasattr(const, "name") else str(const))

                benoetigte_konstanten.append({        # ← muss hier drin sein
                    "name": label,
                    "wert": _format_wert(wert, einheit) if wert is not None else None
                })

            # a und b — Einheit µm da Längenabweichung
            a = komp.a_val() if not isinstance(komp.a_val(), property) else None
            b = komp.b_val()
            su_l0 = komp.std_unsicherheit_l0() if hasattr(komp, "std_unsicherheit_l0") else None
            su_l1 = komp.std_unsicherheit_l1() if hasattr(komp, "std_unsicherheit_l1") else None
            c1 = komp.sensititivty_c1()
            c2 = komp.sensititivty_c2() if hasattr(komp, "sensititivty_c2") else None
            eff_freiheitsgrad = komp.effektiver_freiheitsgrad
            unsicherheitsbeitrag_l0 = komp.unsicherheitsbeitrag_l0() if hasattr(komp, "unsicherheitsbeitrag_l0") else None
            unsicherheitsbeitrag_l1 = komp.unsicherheitsbeitrag_l1() if hasattr(komp, "unsicherheitsbeitrag_l1") else None
            unsicherheitsbeitrag = komp.unsicherheitsbeitrag
            varianz = komp.varianz()

            text_name = text_map.get(str(komp.komp_id), text_map.get(komp.komp_id, "Unbekannt"))

            extended_components.append({
                "name": text_name,
                "formel": asciiformel(komp.formel) if komp.formel else "",
                "klassenname": komp.__class__.__name__,
                "anzahl_im_modell": sum(1 for k in tmodell if k.__class__.__name__ == komp.__class__.__name__),
                "verteilung": verteilung,
                "freiheitsgrad": freiheitsgrad,
                "streuungsparameter": kennwertart,
                "bemerkung": getattr(komp, "remark", "") or "",
                "benoetigte_konstanten": benoetigte_konstanten,
                "a": _format_wert(a, "µm"),
                "b": _format_wert(b, "µm"),
                "standardunsicherheit_l0": _format_wert(su_l0, "µm"),
                "standardunsicherheit_l1": _format_wert(su_l1, "µm"),
                "sensitivitaetskoeffizient_c1": _safe_round(c1),
                "sensitivitaetskoeffizient_c2": _safe_round(c2),
                "effektiver_freiheitsgrad": _safe_round(eff_freiheitsgrad),
                "unsicherheitsbeitrag_l0": _format_wert(unsicherheitsbeitrag_l0, "µm"),
                "unsicherheitsbeitrag_l1": _format_wert(unsicherheitsbeitrag_l1, "µm"),
                "unsicherheitsbeitrag": _format_wert(unsicherheitsbeitrag, "µm"),
                "varianz": _format_wert(varianz, "µm²"),
            })
        except Exception as e:
            print(f"Fehler bei extended_data für Komponente {komp}: {e}")
            continue

    return extended_components



async def get_everything_komp_3d(projekt, db: AsyncSession, uncertainty, tmodell):
    result = []

    CLASSNAME_TO_ID = {
        cls.__name__: comp_id
        for comp_id, cls in ComponentFactory.COMPONENTS.items()
    }

    uncertainty_map = {
        CLASSNAME_TO_ID.get(name): value
        for name, value in uncertainty
    }

    kompids = [tc.komp_id for tc in tmodell]
    text_result = await db.execute(
        select(TEXTKAT).where(TEXTKAT.textnum.in_(kompids))
    )
    text_map = {t.textnum: t.deutsch for t in text_result.scalars()}

    for komp in tmodell:
        try:
            text = text_map.get(str(komp.komp_id), text_map.get(komp.komp_id, "Unbekannt"))
            methode = "A" if komp.data.KennwertArt.name == "M3D_MethodeA" else "B"
            freiheitsgrad = komp.data.Freiheitsgrad.name if hasattr(komp.data.Freiheitsgrad, "name") else str(komp.data.Freiheitsgrad)
            verteilung = komp.data.Verteilung.name if hasattr(komp.data.Verteilung, "name") else str(komp.data.Verteilung)

            ub = uncertainty_map.get(komp.komp_id)
            if ub is None:
                ub = komp.unsicherheitsbeitrag

            result.append({
                "formel": asciiformel(komp.formel) if komp.formel else "",
                "text": text,
                "standardabweichung": _safe_round(komp.data.TermL0),
                "anzahl_messpunkte": komp.messpunkt_anzahl,
                "methode": methode,
                "freiheitsgrad": freiheitsgrad,
                "verteilung": verteilung,
                "unsicherheit": ub,
            })
        except Exception as e:
            print(f"Fehler bei get_everything_komp_3d für Komponente {komp}: {e}")
            continue

    # Sortieren nach Unsicherheit absteigend
    result.sort(key=lambda e: e["unsicherheit"] or 0, reverse=True)
    
    # Max-Unsicherheit für Balken berechnen
    max_u = max((e["unsicherheit"] for e in result if e["unsicherheit"] is not None), default=1)
    for e in result:
        e["unsicherheit_pct"] = round((e["unsicherheit"] / max_u) * 100, 1) if e["unsicherheit"] is not None else 0

    return result