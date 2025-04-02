from fastapi import APIRouter, HTTPException
from app.services.component_service.component_factory import ComponentFactory
from app.schemas.component import Komponente

from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell

router = APIRouter(prefix="/components", tags=["items"])


@router.get("")
def get_components():
    components = ComponentFactory.get_all_components()

    return [Komponente(**k.__dict__) for k in components]

@router.get("/modell-a")
def get_komponente_a():
    # Holen der Komponenteninstanz
    komponenta_instances = ComponentFactory.get_component("TK_AbweichungPoissonKoeffizientMO_EN")

   # print("geschafft!!!!!!!!!!!!!!!!!!!!")
    komponenta_instance = TMU_Modell()

    if not komponenta_instances:
        raise HTTPException(status_code=404, detail="Komponente A nicht gefunden")

    # Holen der benötigten Konstanten
    const_needed = komponenta_instance.MUPruefverfahren_U()


    return {" Messunsicherheit: ": const_needed}