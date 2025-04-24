import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+asyncmy://fastapi_user:JoRu0430@localhost/vda_fastapi_db"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


DATABASE_URL = "mysql+asyncmy://fastapi_user:JoRu0430@localhost/vda_fastapi_db"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def ping_connection():
    try:
        # Verwende eine asynchrone Verbindung, um die Datenbank zu pingen
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() != 1:
                raise Exception("Datenbankverbindung fehlgeschlagen.")
        logging.info("Verbindung zur Datenbank erfolgreich hergestellt!")
    except Exception as e:
        logging.warning(f"Verbindung tot. Reconnect wird versucht: {e}")
        raise


# Synchrone Methode zum Erstellen der Tabellen
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as database:
        yield database
