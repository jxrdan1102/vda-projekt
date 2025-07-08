from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.database.database import create_tables, ping_connection
from app.routers import KMG, ana_mu, auth, components, items, modells

app = FastAPI()
app.include_router(items.router)
app.include_router(components.router)
app.include_router(modells.router)
app.include_router(ana_mu.router)
app.include_router(auth.router)
app.include_router(KMG.router)
"""
table = Table(
    "C:\\Program Files (x86)\\Kistner Messtechnik\\QUEEN VDA5 GUM\\MUDB\\ANAMU.DB"
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

"""
origins = [
    "http://localhost:5173",  # Hier den richtigen Frontend-Link angeben
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
    await create_tables()
    await ping_connection()
    value = 257
    """
    # 4 Bytes extrahieren
    byte1 = (value >> 24) & 0xFF
    byte2 = (value >> 16) & 0xFF
    byte3 = (value >> 8) & 0xFF
    byte4 = value & 0xFF

    b1_str = format(byte1, '08b')
    b2_str = format(byte2, '08b')
    b3_str = format(byte3, '08b')
    b4_str = format(byte4, '08b')

    print(b1_str)
    print(b2_str)
    print(b3_str)
    print(b4_str)
"""
@app.get("/")
def index():
    return {"message": "hello world"}
"""
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
"""