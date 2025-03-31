from fastapi import APIRouter, HTTPException
from app.services.component_service.component_factory import ComponentFactory
from app.schemas.component import Komponente
router = APIRouter(prefix="/components", tags=["items"])


@router.get("")
def get_components():
    components = ComponentFactory.get_all_components()

    return [Komponente(**k.__dict__) for k in components]

@router.get("/komponente-a")
def get_komponente_a():
    # Holen der Komponenteninstanz
    komponenta_instance = ComponentFactory.get_component('type_a')

    if not komponenta_instance:
        raise HTTPException(status_code=404, detail="Komponente A nicht gefunden")

    # Holen der benötigten Konstanten
    const_needed = komponenta_instance.get_const_needed()
    edit_fields = komponenta_instance.get_fields_edit()
    unsicherheitsbeitrag = komponenta_instance.unsicherheitsbeitrag()


    return {"const_needed": const_needed , "edit_fields": edit_fields , "unsicherheitsbeitrag": unsicherheitsbeitrag}