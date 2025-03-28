from fastapi import FastAPI
from app.routers import items  # Sicherstellen, dass der items.router hier importiert wird
from app.database import engine, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.services.item_service import create_default_item  # Importiere die Funktion hier
import uvicorn
from fastapi.routing import APIRoute
app = FastAPI()
app.include_router(items.router)  # Hier wird der Router hinzugefügt

# Datenbanktabellen erstellen (nur für Dev, in Prod Alembic nutzen!)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Verwende async sessionmaker, um Sessions zu erstellen
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@app.on_event("startup")
async def startup():
    async with SessionLocal() as db:  # ✅ Session richtig erstellen
        await create_tables()
        await create_default_item(db)
        # Alle Routen durchgehen und anzeigen
        for route in app.routes:
            print(f"Route: {route.path} | Methods: {route.methods}")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}