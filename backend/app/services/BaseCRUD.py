from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseCRUD:
    def __init__(self, model):
        self.model = model

    async def get_all_by_user(self, db: AsyncSession, user_id: int):
        stmt = select(self.model).where(self.model.fk_user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, id: int, user_id: int = None):
        stmt = select(self.model).where(self.model.id == id)
        if user_id is not None:
            stmt = stmt.where(self.model.fk_user_id == user_id)
        result = await db.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} mit ID {id} nicht gefunden oder nicht erlaubt")
        return obj

    async def create(self, db: AsyncSession, data: dict):
        instance = self.model(**data)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def update(self, db: AsyncSession, id: int, data: dict, user_id: int = None):
        instance = await self.get_by_id(db, id, user_id)
        if not data:
            raise ValueError("Leere Daten – nichts zu aktualisieren.")
        for key, value in data.items():
            setattr(instance, key, value)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, id: int, user_id: int = None):
        obj = await self.get_by_id(db, id, user_id)
        await db.delete(obj)
        await db.commit()
        return {"detail": f"{self.model.__name__} mit ID {id} wurde gelöscht"}