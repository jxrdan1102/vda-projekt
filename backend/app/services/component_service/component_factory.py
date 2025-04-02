import app.services.component_service.components as k

from app.services.component_service.EverythinForComponents.TMU_ConstList import TMU_ConstList


class ComponentFactory:
    COMPONENTS = {
        "type_a": k.KomponenteA,
        "type_b": k.TK_KalibrierungME,
        "TK_Kalibrierung_EN": k.TK_Kalibrierung_EN,
        "TK_AufloesungME": k.TK_AufloesungME,
        "TK_Wiederholpraezision": k.TK_Wiederholpraezision,
        "TK_NichtZentrischeAntastung": k.TK_NichtZentrischeAntastung,
        "TK_AbweichungPoissonKoeffizientMO_EN": k.TK_AbweichungPoissonKoeffizientMO_EN,
        "TK_AbweichungElastizitaetsModul_MO_EN": k.TK_AbweichungElastizitaetsModul_MO_EN,
        "TK_TempDifferenz_MO_ME": k.TK_TempDifferenz_MO_ME,
        "TK_AbweichungMittlereTemp_MO_ME": k.TK_AbweichungMittlereTemp_MO_ME
    }

    @staticmethod
    def get_component(type_name: str):
        component_class = ComponentFactory.COMPONENTS.get(type_name)
        return component_class(None, TMU_ConstList) if component_class else None

    @staticmethod
    def get_all_components():
        return [component_class() for component_class in ComponentFactory.COMPONENTS.values()]