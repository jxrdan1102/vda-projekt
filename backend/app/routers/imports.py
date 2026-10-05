from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import xml.etree.ElementTree as ET
import base64
from datetime import datetime
from collections import defaultdict
from sqlalchemy import select
from app.database.database import get_db
from app.models import Modell, Component
from app.models.user import User
from app.routers.auth import get_current_user
from app.models.ANAMU import ANAMU, ANAKOMP, ANAKONST
router = APIRouter(prefix="/import", tags=["import"])

AUFGABE_MAP = {
    0: 1,  # Durchmesser
    1: 2,  # Abstand
    2: 3,  # Richtung
    3: 4,  # Symmetrie → Koaxialität (nächste passende)
    4: 4,  # Koaxialität
    5: 4,  # KoaxialitätAchse → Koaxialität
    6: 5,  # Form
    7: 6,  # Winkel
    8: 7,  # Position
}

ELEMENT_MAP = {
    0: None,
    1: "Punkt",
    2: "Gerade",
    3: "Ebene",
    4: "Kreis",
    5: "Halbkugel",
    6: "Zylinder",
    7: "Kegel",
}

AUFGABE_MODELL_MAP = {
    0: 1,
    1: 2,
    2: 3,
}


def decode_field(field_el) -> str | None:
    if field_el is None:
        return None
    size = field_el.get("size")
    if size == "-1":
        return None
    value = field_el.get("value")
    if value is not None:
        return value
    cdata = field_el.text
    if cdata:
        cdata = cdata.strip()
        try:
            return base64.b64decode(cdata).decode("latin-1")
        except Exception:
            return cdata
    return None


def get_field(row, name: str) -> str | None:
    for field in row.findall("field"):
        if field.get("name") == name:
            return decode_field(field)
    return None


def parse_int(val) -> int | None:
    try:
        v = int(val) if val is not None else None
        return v if v else None
    except (ValueError, TypeError):
        return None


def parse_int_raw(val) -> int:
    try:
        return int(val) if val is not None else 0
    except (ValueError, TypeError):
        return 0


def parse_float(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def parse_date(val) -> datetime | None:
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d") if val else None
    except (ValueError, TypeError):
        return None


def decode_winkel(winkel_l: int) -> dict:
    """
    TSK_AUSSENMESSUNG = Winkel.l (packed record, 4 Byte-Felder).
    WinkelX_3d = Winkel_ElementX + 1 → 1-basiert im neuen System.
    """
    e1 = ((winkel_l >> 0) & 0xFF) + 1
    e2 = ((winkel_l >> 8) & 0xFF) + 1
    b1 = ((winkel_l >> 16) & 0xFF) + 1
    b2 = ((winkel_l >> 24) & 0xFF) + 1
    return {
        "winkelE1": e1,
        "winkelE2": e2,
        "winkelB1": b1,
        "winkelB2": b2,
    }


def decode_methode_3d(methode: int) -> dict:
    """
    METHODE Bitfeld:
    Bit 0 (& 1):  abstand       0=Schwerpunkt, 1=Nullebene
    Bit 1 (& 2):  artdesmasses  0=Stufenmaß, 1=Innen/Außenmaß
    Bit 2 (& 4):  taster1       1=derselbe, 2=verschiedene
    Bit 3 (& 8):  tasterschaft1 1=senkrecht, 2=parallel
    Bit 4 (& 16): tasterschaft2 1=senkrecht, 2=parallel
    Bit 5 (& 32): taster2       1=derselbe, 2=verschiedene
    """
    return {
        "abstand":       1 if (methode & 1) == 1 else 0,
        "artdesmasses":  1 if (methode & 2) == 2 else 0,
        "taster1":       2 if (methode & 4) == 4 else 1,
        "tasterschaft1": 2 if (methode & 8) == 8 else 1,
        "tasterschaft2": 2 if (methode & 16) == 16 else 1,
        "taster2":       2 if (methode & 32) == 32 else 1,
    }

def decode_punktmuster_richtung(tsk_aussen: int) -> dict:
    return {
        "punktmusterR1": (tsk_aussen & 0xFFFF)+1,
        "punktmusterR2": ((tsk_aussen >> 16) & 0xFFFF)+1,
    }

@router.post("/modell-xml")
async def import_modell_xml(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige XML-Datei: {e}")

    rows = root.findall(".//recorddata/row")
    if not rows:
        raise HTTPException(status_code=400, detail="Keine Datensätze gefunden")

    modell_rows: dict[str, list] = defaultdict(list)
    for row in rows:
        mid = get_field(row, "MODELLID")
        if mid:
            modell_rows[mid].append(row)

    imported = []

    for old_id, rows_for_modell in modell_rows.items():
        first = rows_for_modell[0]

        geo_gn         = parse_int_raw(get_field(first, "GEO_GN"))
        aufgabe_modell = AUFGABE_MODELL_MAP.get(geo_gn, 1)
        methode_raw    = parse_int_raw(get_field(first, "METHODE"))
        aufgabe_raw    = parse_int_raw(get_field(first, "AUFGABE"))
        is_3d          = aufgabe_modell == 3

        if is_3d:
            # Geometrie
            # iGeometrie_EN = GEO_BN → Element1
            # iGeometrie_MO = GEO_MO → Element2
            # iGeometrie_ME = GEO_ME → merkmal/element
            geo_bn_raw = parse_int_raw(get_field(first, "GEO_BN"))
            geo_mo_raw = parse_int_raw(get_field(first, "GEO_MO"))
            geo_me_raw = parse_int_raw(get_field(first, "GEO_ME"))

            # iBezug1 = TSK_TIEFENMESSUNG → Bezug1
            # iBezug2 = TSK_HOEHENMESSUNG → Bezug2
            bezug1_raw = parse_int_raw(get_field(first, "TSK_TIEFENMESSUNG"))
            bezug2_raw = parse_int_raw(get_field(first, "TSK_HOEHENMESSUNG"))

            # Winkel: TSK_AUSSENMESSUNG = Winkel.l (packed integer)
            winkel_raw = parse_int_raw(get_field(first, "TSK_AUSSENMESSUNG"))
            winkel     = decode_winkel(winkel_raw)

            winkel_raw = parse_int_raw(get_field(first, "TSK_AUSSENMESSUNG"))

            # Für Richtung (aufgabe_raw=2) → Punktmuster
            # Für andere Aufgaben → Winkel
            if aufgabe_raw == 2:  # Richtung im alten System
                pm = decode_punktmuster_richtung(winkel_raw)
                punktmusterR1 = pm["punktmusterR1"]
                punktmusterR2 = pm["punktmusterR2"]
                winkelE1 = winkelE2 = winkelB1 = winkelB2 = None
            elif aufgabe_raw == 7:  # Winkel → direktes punktmuster
                punktmuster = winkel_raw+1 or None
                punktmusterR1 = punktmusterR2 = None
                winkelE1 = winkelE2 = winkelB1 = winkelB2 = None
            else:
                w = decode_winkel(winkel_raw)
                winkelE1 = w["winkelE1"]
                winkelE2 = w["winkelE2"]
                winkelB1 = w["winkelB1"]
                winkelB2 = w["winkelB2"]
                punktmusterR1 = punktmusterR2 = None
                # punktmuster aus METHODE Bit 0 für Durchmesser
                punktmuster = 2 if (methode_raw & 1) == 1 else 1

            if aufgabe_raw == 1 or aufgabe_raw == 4 or aufgabe_raw == 8:  # Abstand im alten System
                m = decode_methode_3d(methode_raw)
                taster_val = m["taster1"]  # Bit 2 → taster Feld
            else:
                taster_val = None
            # METHODE entpacken
            m = decode_methode_3d(methode_raw)



            modell = Modell(
                name=get_field(first, "MODNAME"),
                description=get_field(first, "MODDESC"),
                aufgabe_modell=3,
                aufgabe=AUFGABE_MAP.get(aufgabe_raw),
                Element1=ELEMENT_MAP.get(geo_bn_raw),
                Element2="Punkt" if aufgabe_raw == 8 else ELEMENT_MAP.get(geo_mo_raw),
                Bezug1=ELEMENT_MAP.get(bezug1_raw),
                Bezug2=ELEMENT_MAP.get(bezug2_raw),
                merkmal=geo_me_raw or None,
                element=geo_me_raw or None,
                punktmuster=punktmuster,
                punktmusterR1=punktmusterR1,   # nicht im XML gespeichert
                punktmusterR2=punktmusterR2,   # nicht im XML gespeichert
                punktmusterB1=None,   # nicht im XML gespeichert
                winkelE1=winkel["winkelE1"],
                winkelE2=winkel["winkelE2"],
                winkelB1=winkel["winkelB1"],
                winkelB2=winkel["winkelB2"],
                abstand=m["abstand"],
                artdesmasses=m["artdesmasses"],
                taster=taster_val,
                taster1=m["taster1"],
                taster2=m["taster2"],
                tasterschaft1=m["tasterschaft1"],
                tasterschaft2=m["tasterschaft2"],
                tol_fak=parse_int(get_field(first, "TOL_FAK")),
                gegenstand=parse_int(get_field(first, "GEGENSTAND")),
                messeinsatz=parse_int(get_field(first, "MESSEINSATZ")),
                modcreation=parse_date(get_field(first, "MODCREAT")),
                modmod=parse_date(get_field(first, "MODMOD")),
                formel=get_field(first, "FORMEL"),
                formeldesc=get_field(first, "FORMELDESC"),
                is_builtin=True,
                fk_user_id=current_user.id,
                fk_company=current_user.fk_company,
                old_import_id=int(old_id),
            )

        else:
            modell = Modell(
                name=get_field(first, "MODNAME"),
                description=get_field(first, "MODDESC"),
                aufgabe_modell=aufgabe_modell,
               aufgabe=AUFGABE_MAP.get(aufgabe_raw),
                geo_me=parse_int(get_field(first, "GEO_ME")),
                geo_mo=parse_int(get_field(first, "GEO_MO")),
                geo_bn=parse_int(get_field(first, "GEO_BN")),
                methode=methode_raw or None,
                gegenstand=parse_int(get_field(first, "GEGENSTAND")),
                messeinsatz=parse_int(get_field(first, "MESSEINSATZ")),
                tol_fak=parse_int(get_field(first, "TOL_FAK")),
                tsk_ausenmessung=parse_int_raw(get_field(first, "TSK_AUSSENMESSUNG")),
                tsk_innenmessung=parse_int_raw(get_field(first, "TSK_INNNENMESSUNG")),
                tsk_tiefenmessung=parse_int_raw(get_field(first, "TSK_TIEFENMESSUNG")),
                tsk_hoehenmessung=parse_int_raw(get_field(first, "TSK_HOEHENMESSUNG")),
                tsk_stufenmessung=parse_int_raw(get_field(first, "TSK_STUFENMESSUNG")),
                modcreation=parse_date(get_field(first, "MODCREAT")),
                modmod=parse_date(get_field(first, "MODMOD")),
                formel=get_field(first, "FORMEL"),
                formeldesc=get_field(first, "FORMELDESC"),
                is_builtin=True,
                fk_user_id=current_user.id,
                fk_company=current_user.fk_company,
                old_import_id=int(old_id),
            )

        db.add(modell)
        await db.flush()

        for row in rows_for_modell:
            lfdnr  = parse_int_raw(get_field(row, "LFDNR"))
            kompid = parse_int_raw(get_field(row, "KOMPID"))
            if not kompid:
                continue

            component = Component(
                fk_modell=modell.id,
                lfdnr=lfdnr,
                kompid=kompid,
                modltxtid=parse_int_raw(get_field(row, "MODLTXTID")),
                terml0=parse_float(get_field(row, "TERML0")),
                terml1=parse_float(get_field(row, "TERML1")),
                wertart=parse_int_raw(get_field(row, "WERTART")),
                freigrad=parse_int_raw(get_field(row, "FREIGRAD")),
                frei_n_1=parse_int_raw(get_field(row, "FREI_N_1")),
                verteilung=parse_int_raw(get_field(row, "VERTEILUNG")),
                kflags=parse_int_raw(get_field(row, "KFLAGS")) or 1,
                fk_user_id=current_user.id,
                fk_company=current_user.fk_company,
            )
            db.add(component)

        imported.append({
            "old_id": old_id,
            "new_id": modell.id,
            "name": modell.name,
            "typ": "3D" if is_3d else "Standard",
            "komponenten": len(rows_for_modell),
        })

    await db.commit()

    return {
        "detail": f"{len(imported)} Modell(e) erfolgreich importiert",
        "modelle": imported
    }


@router.post("/anamu-xml")
async def import_anamu_xml(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige XML-Datei: {e}")

    rows = root.findall(".//recorddata/row")
    if not rows:
        raise HTTPException(status_code=400, detail="Keine Datensätze gefunden")

    # Gruppieren nach ANAMUID
    anamu_groups: dict[str, list] = defaultdict(list)
    for row in rows:
        anamuid = get_field(row, "ANAMUID")
        if anamuid:
            anamu_groups[anamuid].append(row)

    imported = []
    skipped = []

    for old_anamu_id, rows_for_anamu in anamu_groups.items():
        first = rows_for_anamu[0]
        old_modell_id = parse_int_raw(get_field(first, "MODELLID"))

        # Neues Modell über old_import_id finden (innerhalb derselben Company)
        modell_result = await db.execute(
            select(Modell).where(
                Modell.old_import_id == old_modell_id,
                Modell.fk_company == current_user.fk_company,
            )
        )
        new_modell = modell_result.scalar_one_or_none()

        if not new_modell:
            skipped.append({
                "old_anamu_id": old_anamu_id,
                "grund": f"Kein Modell für alte ID={old_modell_id} gefunden"
            })
            continue

        # ANAMU erstellen
        anamu = ANAMU(
            fk_modell=new_modell.id,
            name=get_field(first, "NAME"),
            aenderungszustand=get_field(first, "NMBR"),
            identnr=parse_int(get_field(first, "IDENTNR")),
            partno=parse_int(get_field(first, "PARTNO")),
            remark=get_field(first, "REMARK"),
            creation=parse_date(get_field(first, "CREAT")),
            modify=parse_date(get_field(first, "MODIF")),
            tolfaktor=parse_int_raw(get_field(first, "TOLFAKTOR")),
            tsk_aufgabe=parse_int(get_field(first, "TSK_AUFGABE")),
            fk_user_id=current_user.id,
            fk_company=current_user.fk_company,
        )
        db.add(anamu)
        await db.flush()

        for row in rows_for_anamu:
            konst = parse_int_raw(get_field(row, "KONST"))

            if konst == 0:
                # ANAKOMP — Lookup über lfdnr
                lfdnr = parse_int_raw(get_field(row, "LFDNR"))
                comp_result = await db.execute(
                    select(Component).where(
                        Component.fk_modell == new_modell.id,
                        Component.lfdnr == lfdnr,
                    )
                )
                comp = comp_result.scalar_one_or_none()

                # Ist es ein 3D-Modell?
                is_3d = new_modell.aufgabe_modell == 3

                anakomp = ANAKOMP(
                    fk_anamu=anamu.id,
                    fk_mod_components=comp.id if comp else None,
                    remark=get_field(row, "REMARK"),
                    terml0=parse_float(get_field(row, "TERML0")),
                    terml1=None if is_3d else parse_float(get_field(row, "TERML1")),
                    wertart=parse_int_raw(get_field(row, "WERTART")),
                    freigrad=parse_int_raw(get_field(row, "FREIGRAD")),
                    frei_n_1=None if is_3d else parse_int_raw(get_field(row, "FREI_N_1")),
                    verteilung=parse_int_raw(get_field(row, "VERTEILUNG")),
                    messpunkt_anzahl=parse_int_raw(get_field(row, "FREI_N_1")) if is_3d else 0,
                    anzahl_messungen=parse_int(get_field(row, "TERML1")) if is_3d else None,
                    fk_user_id=current_user.id,
                    fk_company=current_user.fk_company,
                )
                db.add(anakomp)

            elif konst == 1:
                # ANAKONST — MODKOMPID ist constnum
                constnum = parse_int_raw(get_field(row, "MODKOMPID"))
                constval = parse_float(get_field(row, "TERML0"))  # Wert steht in TERML0

                anakonst = ANAKONST(
                    fk_anamu=anamu.id,
                    constnum=constnum,
                    constval=constval,
                    remark=get_field(row, "REMARK"),
                    fk_user_id=current_user.id,
                    fk_company=current_user.fk_company,
                )
                db.add(anakonst)

        imported.append({
            "old_id": old_anamu_id,
            "new_id": anamu.id,
            "name": anamu.name,
            "komponenten": len([r for r in rows_for_anamu if parse_int_raw(get_field(r, "KONST")) == 0]),
            "konstanten": len([r for r in rows_for_anamu if parse_int_raw(get_field(r, "KONST")) == 1]),
        })

    await db.commit()

    return {
        "detail": f"{len(imported)} Analyseprojekt(e) importiert, {len(skipped)} übersprungen",
        "importiert": imported,
        "uebersprungen": skipped,
    }