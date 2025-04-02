import csv

from fastapi import FastAPI
from app.routers import items, components
from app.database.database import create_tables
from pypxlib import Table
app = FastAPI()
app.include_router(items.router)
app.include_router(components.router)

table = Table("C:\Program Files (x86)\Kistner Messtechnik\QUEEN VDA5 GUM\MUDB\modkomp.DB")
fieldnames = list(table.fields.keys())
csv_file = "C:\\Users\\Jason\\Desktop\\testsss.csv"
# CSV-Datei erstellen und Daten schreiben
with open(csv_file, mode="w+", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")  # Semikolon als Trenner

    writer.writerow(fieldnames)  # Spaltenüberschriften schreiben (Fix!)

    for row in table:
        writer.writerow([getattr(row, field) for field in fieldnames])  # Werte als Liste speichern


@app.on_event("startup")
async def startup():
    await create_tables()
@app.get('/')
def index():
    return {'message': 'hello world'}
