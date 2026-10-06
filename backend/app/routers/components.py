from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.user import User
from app.routers.auth import get_company_id, require_write
from app.schemas.component import ComponentBack, ComponentGet, ComponentRefUpdate
from app.services import ComponentService
from app.services.component_service.component_factory import ComponentFactory

router = APIRouter(prefix="/components", tags=["components"])


#@router.get("", response_model=list[ComponentBack])
#def get_components():
#    components = ComponentFactory.get_all_components()
#    return [ComponentBack(data=k.data, ConstNeeded=k.ConstNeeded, name=k.__class__.__name__, id=k.id) for k in components]

@router.get("", response_model=list[ComponentBack])
def get_components():
    return [ComponentBack(name=cls.__name__, id=comp_id) for comp_id, cls in ComponentFactory.COMPONENTS.items()]

@router.get("/{id}", response_model=ComponentGet)
async def get_component_db(
    id: int,
    db: AsyncSession = Depends(get_db),
    company_id: int | None = Depends(get_company_id),
):
    return await ComponentService.get_component_by_id(db, id, company_id)


@router.post("/{id}")
async def update_comp(
    id: int,
    comp_update: ComponentRefUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id),
):
    update_data = comp_update.model_dump(exclude_unset=True)
    return await ComponentService.update_component(db, id, update_data, company_id)

@router.delete("/{id}")
async def delete_comp(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id),
):
    return await ComponentService.delete_component(db, id, company_id)