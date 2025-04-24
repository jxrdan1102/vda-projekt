from typing import List

from app.core.security import get_current_user
from app.database.database import get_db
from app.database.generic_methods import (
    calc_uncertainty,
    create_entity_with_children,
    generic_child_builder,
    get_all_generic,
    get_by_foreign_key,
    get_by_id,
    update_model,
)
from app.models.components import Component
from app.models.modell import Modell
from app.models.user import User
from app.schemas.component import ComponentGet, ComponentGetModell, ComponentKompidOnly
from app.schemas.modell import (
    ModellBase,
    ModellCreate,
    ModellIDResponse,
    ModellNameDescription,
    ModellUpdate,
)
from app.services.component_service.EverythinForComponents.TMU_Modell import (
    TMU_Modell,
    TMU_ModellSchema,
)
from app.services.component_service.component_factory import ComponentFactory
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/modells", tags=["modells"])


@router.get("", response_model=List[ModellNameDescription])
async def get_modells(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 👈 Benutzer ziehen
):
    modells = await get_by_foreign_key(
        Modell, Modell.fk_user_id, current_user.id, db, ModellNameDescription
    )
    return modells


@router.get("/{id}/components", response_model=List[ComponentGet])
async def get_modell_components(id: int, db: AsyncSession = Depends(get_db)):
    components = await get_by_foreign_key(
        Component, Component.fk_modell, id, db, ComponentGet
    )
    return components
@router.get("/{id}/test")
async def get_modell_test(id: int, db: AsyncSession = Depends(get_db)):
    TMU_ModellSchem = TMU_ModellSchema(aufgabe=1, modell_id=2, iBezug1=1,iGeometrie_EN="Gerade")
    modell = TMU_Modell(TMU_ModellSchem)
    modell.addComponent(1111)
    modell.addComponent(2222)
    modell.addComponent(3333)
    modell.addComponent(4444)
    print(modell)
    return modell.MUPruefverfahren_U()

@router.get("/{id}", response_model=ModellIDResponse)
async def get_modell_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    modell = await get_by_id(Modell, id, db, ModellBase)
    if not modell:
        raise HTTPException(
            status_code=404, detail="Modell nicht gefunden oder kein Zugriff"
        )

    # Retrieve components
    component_objs = await get_by_foreign_key(
        Component, Component.fk_modell, id, db, ComponentGetModell
    )
    component_ids = [comp.kompid for comp in component_objs]

    tmu_modell = TMU_Modell.from_schema_params(
        aufgabe=modell.aufgabe, modell_id=modell.id
    )

    for component_id in component_ids:
        tmu_modell.addComponent(component_id)

    return ModellIDResponse(
        name=modell.name,
        description=modell.description,
        components=component_objs,
        constantsValue=tmu_modell.const_list,
    )


@router.post("")
async def create_modell(
    modell: ModellCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 👈 wieder User
):
    db_modell = Modell(
        **modell.model_dump(exclude={"components"}),
        fk_user_id=current_user.id,  # 👈 Ownership setzen
    )

    return await create_entity_with_children(
        db=db,
        entity=db_modell,
        child_data_list=modell.components,
        child_builder=generic_child_builder(Component, "fk_modell"),
    )


@router.put("/{id}")
async def update_modell(
    id: int, modell: ModellUpdate, db: AsyncSession = Depends(get_db)
):
    # Use the update_model generic method for the modell
    updated_modell = await update_model(
        db=db,
        model_class=Modell,
        id=id,
        update_data=modell.model_dump(exclude_unset=True, exclude={"components"}),
    )

    # Add components if new ones are provided
    if modell.components:
        new_components = [
            Component(**component.model_dump(), fk_modell=id)
            for component in modell.components
        ]
        db.add_all(new_components)

    await db.commit()
    return updated_modell


@router.delete("/{id}")
async def delete_modell_by_id(id: int, db: AsyncSession = Depends(get_db)):
    modell = await get_by_id(Modell, id, db, ModellBase)
    if not modell:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    # Optional: Delete related components manually if not handled by ON DELETE
    # CASCADE
    await db.execute(delete(Component).where(Component.fk_modell == id))

    await db.delete(modell)
    await db.commit()

    return {"detail": f"Modell mit ID {id} wurde gelöscht"}
