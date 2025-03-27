from fastapi import FastAPI
from app.routers import items
from app.database import engine, Base

app = FastAPI(title="Mein FastAPI Backend", version="1.0")

# Datenbanktabellen erstellen (nur für Dev, in Prod Alembic nutzen!)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await create_tables()

app.include_router(items.router)

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}