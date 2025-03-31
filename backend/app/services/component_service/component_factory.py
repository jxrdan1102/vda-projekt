import app.services.component_service.components as k

from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_ConstList


class ComponentFactory:
    COMPONENTS = {
        "type_a": k.KomponenteA,
        "type_b": k.KomponenteB
    }

    @staticmethod
    def get_component(type_name: str):
        component_class = ComponentFactory.COMPONENTS.get(type_name)
        return component_class(None, TMU_ConstList) if component_class else None

    @staticmethod
    def get_all_components():
        return [component_class() for component_class in ComponentFactory.COMPONENTS.values()]