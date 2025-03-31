from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+asyncmy://fastapi_user:JoRu0430@localhost/vda_fastapi_db"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Synchrone Methode zum Erstellen der Tabellen
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()