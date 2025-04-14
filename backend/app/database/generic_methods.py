from http.client import HTTPException
from typing import Type, TypeVar, Any, List, Callable, Optional, Union

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.models import Component, Modell
from app.schemas.component import ComponentKompidOnly
from app.schemas.modell import ModellBase
from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_ModellSchema, TMU_Modell

from app.services.component_service.EverythinForComponents.TMuKompRec import TMU_Verteilung, TMU_KennwertArt, \
    TMU_Freiheitsgrad

from app.models.ANAMU import ANAKOMP

from app.schemas.component import ComponentData

T = TypeVar("T")

async def update_model(
    db: AsyncSession,
    model_class: Type[T],
    *,
    id: Optional[int] = None,
    fk_field: Optional[InstrumentedAttribute] = None,
    fk_value: Optional[Union[int, str]] = None,
    update_data: dict
) -> Union[T, List[T]]:
    if id is None and (fk_field is None or fk_value is None):
        raise ValueError("Either 'id' or 'fk_field' and 'fk_value' must be provided")

    # Hole Objekt(e) – nach id oder ForeignKey
    if id is not None:
        result = await db.execute(select(model_class).where(model_class.id == id))
        items = [result.scalar_one_or_none()]
    else:
        result = await db.execute(select(model_class).where(fk_field == fk_value))
        items = result.scalars().all()

    if not items or items[0] is None:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_items = []
    for item in items:
        changed = False
        for key, value in update_data.items():
            if hasattr(item, key):
                current_value = getattr(item, key)
                if current_value != value:
                    setattr(item, key, value)
                    changed = True
                    # Wenn JSON-Feld oder ArrayField (PostgreSQL): flag_modified(db_instance, key)
        if changed:
            updated_items.append(item)

    if updated_items:
        db.add_all(updated_items)
        await db.commit()
        for obj in updated_items:
            await db.refresh(obj)

    return updated_items if len(updated_items) > 1 else updated_items[0]

async def get_by_id(
    orm_model: Type,
    model_id: int,
    db: AsyncSession,
    pydantic_model: Type[BaseModel]
) -> Optional[BaseModel]:

    model_fields = pydantic_model.model_fields.keys()
    columns = [getattr(orm_model, field) for field in model_fields if hasattr(orm_model, field)]

    stmt = select(*columns).filter(orm_model.id == model_id)
    result = await db.execute(stmt)
    row = result.fetchone()

    if row:
        return pydantic_model(**dict(zip(model_fields, row)))
    return None


def generic_child_builder(model_class, fk_field: str):
    def builder(child_data, parent):
        return model_class(
            **child_data.model_dump(exclude={fk_field}),
            **{fk_field: parent.id}
        )
    return builder


async def create_entity_with_children(
        db: AsyncSession,
        entity: Any,
        child_data_list: List[Any],
        child_builder: Callable[[Any], Any]
):
    # Entität zur Session hinzufügen
    db.add(entity)

    # Kinder nur hinzufügen, wenn vorhanden
    if child_data_list:
        # Kind-Entitäten in einem Schritt erstellen
        children = [child_builder(data, entity) for data in child_data_list]
        db.add_all(children)

    # Commit in einem Schritt, nachdem alle Entitäten (inkl. Kinder) hinzugefügt wurden
    await db.commit()

    # Optional: Entität nach dem Commit nicht mehr auffrischen, wenn nicht notwendig
    return entity


async def get_all_generic(
        model: Type[Any],  # Das ORM-Modell (z. B. Component)
        db: AsyncSession,
        pydantic_model: Type[BaseModel],  # Das Pydantic-Response-Modell
) -> List[Any]:

    fields = list(pydantic_model.model_fields.keys())
    stmt = select(*[getattr(model, field) for field in fields])

    result = await db.execute(stmt)
    rows = result.all()

    return [pydantic_model(**dict(zip(fields, row))) for row in rows]

async def get_by_foreign_key(
    orm_model: Type,
    fk_field: InstrumentedAttribute,
    value: Any,
    db: AsyncSession,
    pydantic_model: Type[BaseModel]
) -> List[BaseModel]:

    # Nur die Spalten holen, die auch im Pydantic-Modell sind
    model_fields = pydantic_model.model_fields.keys()
    columns = [getattr(orm_model, field) for field in model_fields]

    stmt = select(*columns).filter(fk_field == value)
    result = await db.execute(stmt)
    rows = result.all()

    # Mapping der Zeilen auf Pydantic-Modelle
    return [pydantic_model(**dict(zip(model_fields, row))) for row in rows]


async def calc_uncertainty(
    project_id: int,
    modell_id: int,
    db: AsyncSession
) -> Optional[float]:  # Oder passendes Rückgabetyp je nach MUPruefverfahren_U()

    modell = await get_by_id(Modell, modell_id, db, ModellBase)
    if not modell:
        return None

    components = await get_by_foreign_key(
        ANAKOMP,
        ANAKOMP.fk_anamu,
        project_id,
        db,
        ComponentData
    )
    components_ids = await get_by_foreign_key(Component,Component.fk_modell,modell_id,db,ComponentKompidOnly)
    component_ids = [c.kompid for c in components_ids]

    tmu_modell_schema = TMU_ModellSchema(
        aufgabe=modell.aufgabe,
        modell_id=modell.id
    )
    tmu_modell = TMU_Modell(tmu_modell_schema)

    for component_id in component_ids:
        tmu_modell.addComponent(component_id)
    print("muuu",tmu_modell)
    print(components)
    for component, comp_data in zip(tmu_modell, components):
        print("test3",comp_data)
        component.data.TermL0 = comp_data.terml0
        component.data.TermL1 = comp_data.terml1
        component.data.Verteilung = TMU_Verteilung(comp_data.verteilung)
        component.data.KennwertArt = TMU_KennwertArt(comp_data.wertart)
        component.data.Freiheitsgrad = TMU_Freiheitsgrad(comp_data.freigrad)
        component.data.FreiN_minus_1 = comp_data.frei_n_1
        print("test", component.data, component)

    return tmu_modell.MUPruefverfahren_U()