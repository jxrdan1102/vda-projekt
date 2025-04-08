import app.services.component_service.components as k

from app.services.component_service.EverythinForComponents.TMU_ConstList import TMU_ConstList


class ComponentFactory:
    COMPONENTS = {
        1042: k.KomponenteA,
        1001: k.TK_KalibrierungME,
        1027: k.TK_Kalibrierung_EN,
        1003: k.TK_AufloesungME,
        1040: k.TK_Wiederholpraezision,
        1041: k.TK_NichtZentrischeAntastung,
        1043: k.TK_AbweichungPoissonKoeffizientMO_EN,
        1044: k.TK_AbweichungElastizitaetsModul_MO_EN,
        1009: k.TK_TempDifferenz_MO_ME,
        1010: k.TK_AbweichungMittlereTemp_MO_ME
    }

    @staticmethod
    def get_component(modell: 'TMU_Modell' ,type_name: str):
        component_class = ComponentFactory.COMPONENTS.get(type_name)
        return component_class(modell, TMU_ConstList) if component_class else None

    @staticmethod
    def get_all_components():
        return [component_class(None, TMU_ConstList) for component_class in ComponentFactory.COMPONENTS.values()]