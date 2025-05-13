from app.models.components import Component
from app.schemas.component import ComponentGet
from app.services.BaseCRUD import BaseCRUD
from sqlalchemy.ext.asyncio import AsyncSession

ComponentCRUD = BaseCRUD(Component)

async def get_component_by_id(db: AsyncSession, id: int, user_id: int):
    return await ComponentCRUD.get_by_id(db, id, user_id)

async def update_component(db: AsyncSession, id: int, data: dict, user_id: int):
    return await ComponentCRUD.update(db, id, data, user_id)