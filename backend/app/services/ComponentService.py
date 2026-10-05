from sqlalchemy.ext.asyncio import AsyncSession
from app.models.components import Component
from app.services.BaseCRUD import BaseCRUD

ComponentCRUD = BaseCRUD(Component)

async def get_component_by_id(db: AsyncSession, id: int, company_id: int | None = None):
    return await ComponentCRUD.get_by_id(db, id, company_id)

async def update_component(db: AsyncSession, id: int, data: dict, company_id: int | None = None):
    return await ComponentCRUD.update(db, id, data, company_id)

async def delete_component(db: AsyncSession, id: int, company_id: int | None = None):
    return await ComponentCRUD.delete(db, id, company_id)