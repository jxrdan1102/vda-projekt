import base64
from http.client import HTTPException

from app.database.database import get_db
from app.models import Component
from app.models import Modell
from app.models.item import Item
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.item import ItemCreate, ItemUpdate
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items


@router.get("/{id}")
async def get_item(id: int, db: AsyncSession = Depends(get_db)):
    db_item = await db.execute(select(Item).where(Item.id == id))
    db_item.scalar_one_or_none()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_item


@router.post("/")
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.put("/{id}")
async def update_item(id: int, item: ItemUpdate, db: AsyncSession = Depends(get_db)):
    # Item aus der Datenbank holen
    result = await db.execute(select(Item).where(Item.id == id))
    db_item = result.scalar_one_or_none()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Nur die übergebenen Felder aktualisieren
    # Nur vorhandene Werte nehmen
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_item)

    return db_item


@router.delete("/{id}")
async def delete_item(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == id))
    db_item = result.scalar_one_or_none()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(db_item)
    await db.commit()
    return {"message": f"Item with id {id} has been deleted"}



@router.post("/r")
async def importXMLModell(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    import xml.etree.ElementTree as ET

    # XML-Datei einlesen
    tree = ET.parse(r"C:\Users\Jason\Desktop\M2500001.XML")
    root = tree.getroot()

    mapping = {
        'MODNAME': 'name',
        'MODDESC': 'description',
        'GEO_ME': 'geo_me',
        'GEO_MO': 'geo_mo',
        'GEO_GN': 'geo_gn',
        'GEO_BN': 'geo_bn',
        'TOL_FAK': 'tol_fak',
        'AUFGABE': 'aufgabe',
        'METHODE': 'methode',
        'GEGENSTAND': 'gegenstanf',
        'MODCREAT': 'modcreation',
        'MODMOD': 'modmod',
        'TSK_AUSSENMESSUNG': 'tsk_ausenmessung',
        'TSK_INNNENMESSUNG': 'tsk_innenmessung',
        'TSK_TIEFENMESSUNG': 'tsk_tiefenmessung',
        'TSK_HOEHENMESSUNG': 'tsk_hoehenmessung',
        'TSK_STUFENMESSUNG': 'tsk_stufenmessung',
        'FORMEL': 'formel',
        'FORMELDESC': 'formeldesc'
    }
    for row in root.find('recorddata').findall('row'):
        data = {k: "" for k in mapping.values()}  # init leere Strings
        data['messeinsatz'] = "69"
        data['einstellmass'] = "69"
        data['fk_user_id'] = current_user.id

        for field in row.findall('field'):
            field_name = field.attrib.get('name')
            if field_name in mapping:
                if 'value' in field.attrib:
                    data[mapping[field_name]] = field.attrib['value']
                elif field.text:
                    # Base64-decode versuchen
                    try:
                        decoded = base64.b64decode(field.text.strip()).decode('latin-1')
                        data[mapping[field_name]] = decoded
                    except Exception as e:
                        print(f"Fehler beim Decodieren von {field_name}: {e}")
                        data[mapping[field_name]] = field.text.strip()

    db_modell = Modell(**data)
    db.add(db_modell)
    await db.commit()
    await db.refresh(db_modell)

    mapping = {
        'LFDNR': 'lfdnr',
        'KOMPID': 'kompid',
        'MODLTXTID': 'modltxtid',
        'TERML0': 'terml0',
        'TERML1': 'terml1',
        'WERTART': 'wertart',
        'FREIGRAD': 'freigrad',
        'FREI_N_1': 'frei_n_1',
        'VERTEILUNG': 'verteilung',
        'KFLAGS': 'kflags',
    }
    for row in root.find('recorddata').findall('row'):
        data = {k: "" for k in mapping.values()}  # init leere Strings
        data['fk_modell'] = db_modell.id
        for field in row.findall('field'):
            field_name = field.attrib.get('name')
            if field_name in mapping:
                if 'value' in field.attrib:
                    data[mapping[field_name]] = field.attrib['value']
                elif field.text:
                    # Base64-decode versuchen
                    try:
                        decoded = base64.b64decode(field.text.strip()).decode('latin-1')
                        data[mapping[field_name]] = decoded
                    except Exception as e:
                        print(f"Fehler beim Decodieren von {field_name}: {e}")
                        data[mapping[field_name]] = field.text.strip()
        db_comp = Component(**data)
        db.add(db_comp)
        await db.commit()
        await db.refresh(db_comp)

    return "Modell wurde erfolgreich importiert"
