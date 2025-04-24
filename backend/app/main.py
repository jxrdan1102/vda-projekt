import csv

from app.database.database import create_tables, ping_connection
from app.routers import ana_mu, auth, components, items, modells, KMG
from app.services.component_service.DreiDComponents import TK_3d_ResKMG
from app.services.component_service.DreiDComponents import TK_3d_Wi_DeltaEKMG
from app.services.component_service.DreiDComponents import TK_3d_Wi_WB
from app.services.component_service.DreiDComponents import TK_3d_Wi_WE
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
    TMU_ConstList,
)
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_ModellSchema
from fastapi import FastAPI
from pypxlib import Table

app = FastAPI()
app.include_router(items.router)
app.include_router(components.router)
app.include_router(modells.router)
app.include_router(ana_mu.router)
app.include_router(auth.router)
app.include_router(KMG.router)

table = Table(
    "C:\\Program Files (x86)\\Kistner Messtechnik\\QUEEN VDA5 GUM\\MUDB\\Anamu.DB"
)
fieldnames = list(table.fields.keys())
csv_file = "C:\\Users\\Jason\\Desktop\\testsss.csv"
# CSV-Datei erstellen und Daten schreiben
with open(csv_file, mode="w+", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")  # Semikolon als Trenner

    writer.writerow(fieldnames)  # Spaltenüberschriften schreiben (Fix!)

    for row in table:
        writer.writerow(
            [getattr(row, field) for field in fieldnames]
        )  # Werte als Liste speichern


@app.on_event("startup")
async def startup():
    print("🚀 Erstelle Tabellen in der Datenbank...")
    await create_tables()
    await ping_connection()
    print("🚀 Erstelle Tabellen fertig")

    TMU_ModellSchem = TMU_ModellSchema(aufgabe=1, modell_id=2, iBezug1=1,iGeometrie_EN="Gerade")
    modell = TMU_Modell(TMU_ModellSchem)
    modell.addComponent(1111)
    modell.addComponent(2222)
    modell.addComponent(3333)
    modell.addComponent(4444)
    print("modelc",modell)
    print(modell[3].unsicherheitsbeitrag())

@app.get("/")
def index():
    return {"message": "hello world"}
