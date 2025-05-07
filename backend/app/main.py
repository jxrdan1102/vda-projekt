import base64
import csv

from app.database.database import SessionLocal
from app.database.database import create_tables, ping_connection
from app.database.database import get_db
from app.database.database import get_db
from app.models import Modell
from app.routers import KMG, ana_mu, auth, components, items, modells
from app.services.component_service.EverythinForComponents.TMU_Modell import (
    TMU_Modell,
    TMU_ModellSchema,
)
from fastapi import FastAPI
from pypxlib import Table
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(items.router)
app.include_router(components.router)
app.include_router(modells.router)
app.include_router(ana_mu.router)
app.include_router(auth.router)
app.include_router(KMG.router)

table = Table(
    "C:\\Program Files (x86)\\Kistner Messtechnik\\QUEEN VDA5 GUM\\MUDB\\modkomp.DB"
)
fieldnames = list(table.fields.keys())
csv_file = "C:\\Users\\Jason\\Desktop\\testssss.csv"
# CSV-Datei erstellen und Daten schreiben
with open(csv_file, mode="w+", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")  # Semikolon als Trenner

    writer.writerow(fieldnames)  # Spaltenüberschriften schreiben (Fix!)

    for row in table:
        writer.writerow(
            [getattr(row, field) for field in fieldnames]
        )  # Werte als Liste speichern




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
    data['messeinsatz'] = ""
    data['einstellmass'] = ""
    data['fk_user_id'] = "13"

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
print(data)
async def main(dat):
    db = SessionLocal()
    model = Modell(**dat)
    await db.add(model)
    await db.commit()

origins = [
    "http://localhost:3000",  # Hier den richtigen Frontend-Link angeben
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    print("🚀 Erstelle Tabellen in der Datenbank...")
    await create_tables()
    await ping_connection()
    print("🚀 Erstelle Tabellen fertig")


@app.get("/")
def index():
    return {"message": "hello world"}

from fastapi import Response
import matplotlib.pyplot as plt
import io
@app.get("/unsicherheiten")
def plot_unsicherheiten(namen: str, werte: str):
    namen = "Tests, Testss, Testsss, Testssss, tests, testss, mehrs,mehr"
    werte = "0.5,0.4,0.3,0.65,0.6,0.9,0.11,0.09"
    komponenten = [k.strip() for k in namen.split(",")]
    unsicherheiten = [float(w) for w in werte.split(",")]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.bar(komponenten, unsicherheiten, color="skyblue")
    ax.set_title("Messunsicherheiten der Komponenten")
    ax.set_ylabel("Standardunsicherheit")
    ax.set_xlabel("Komponente")
    for i, v in enumerate(unsicherheiten):
        ax.text(i, v + 0.01, f"{v:.2f}", ha='center', va='bottom')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    return Response(content=buf.read(), media_type="image/png")