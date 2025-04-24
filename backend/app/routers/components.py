from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.database.generic_methods import get_by_id, update_model
from app.models import Component
from app.schemas.component import ComponentBack, ComponentGet, ComponentRefUpdate
from app.services.component_service.component_factory import ComponentFactory

router = APIRouter(prefix="/components", tags=["components"])


# Ist der Endpunkt sinnvoll?
@router.get("", response_model=list[ComponentBack])
def get_components():
    components = ComponentFactory.get_all_components()

    return [ComponentBack(data=k.data, ConstNeeded=k.ConstNeeded) for k in components]


@router.put("/{id}")
async def update_comp(
    id: int, comp_update: ComponentRefUpdate, db: AsyncSession = Depends(get_db)
):
    update_data = comp_update.model_dump(exclude_unset=True)
    updated = await update_model(db, Component, id=id, update_data=update_data)
    return updated


@router.get("/{id}", response_model=ComponentGet)
async def get_component_db(id: int, db: AsyncSession = Depends(get_db)):
    component = await get_by_id(Component, id, db, ComponentGet)

    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")

    return component
