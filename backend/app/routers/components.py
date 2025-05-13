from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.component import ComponentBack, ComponentGet, ComponentRefUpdate
from app.services import ComponentService
from app.services.component_service.component_factory import ComponentFactory

router = APIRouter(prefix="/components", tags=["components"])


@router.get("", response_model=list[ComponentBack])
def get_components():
    components = ComponentFactory.get_all_components()
    return [ComponentBack(data=k.data, ConstNeeded=k.ConstNeeded) for k in components]


@router.get("/{id}", response_model=ComponentGet)
async def get_component_db(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ComponentService.get_component_by_id(db, id, current_user.id)


@router.put("/{id}")
async def update_comp(
    id: int,
    comp_update: ComponentRefUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = comp_update.model_dump(exclude_unset=True)
    return await ComponentService.update_component(db, id, update_data, current_user.id)