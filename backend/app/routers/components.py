from fastapi import APIRouter, HTTPException, Depends
from app.services.component_service.component_factory import ComponentFactory

from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell

from app.schemas.component import ComponentRefCreate

from app.schemas.component import ComponentBack
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.component import ComponentRefUpdate

from app.models import Component

router = APIRouter(prefix="/components", tags=["components"])


@router.get("")
def get_components():
    components = ComponentFactory.get_all_components()

    return [ComponentBack(**k.data.to_dict()) for k in components]

@router.put("/{id}")
async def update_component(id: int, component: ComponentRefUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Component).where(Component.id == id))
    db_component = result.scalar_one_or_none()

    if db_component is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Nur die übergebenen Felder aktualisieren
    update_data = component.model_dump(exclude_unset=True)  # Nur vorhandene Werte nehmen
    for key, value in update_data.items():
        setattr(db_component, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_component)

    return db_component

@router.get("/modell-a")
def get_komponente_a():

    komponenta_instance = ComponentFactory.get_component(1042)

    if not komponenta_instance:
        raise HTTPException(status_code=404, detail="Komponente A nicht gefunden")

    const_needed = komponenta_instance.unsicherheitsbeitrag()


    return {" Erweiterte Messunsicherheit: ": const_needed}