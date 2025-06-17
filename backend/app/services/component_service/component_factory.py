import app.services.component_service.DreiDComponents as d
import app.services.component_service.components as k
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TMU_ConstList,
)


class ComponentFactory:
    COMPONENTS = {
        1002: k.TK_ErmittelteMessabweichungME,
        1042: k.KomponenteA,
        1001: k.TK_KalibrierungME,
        1027: k.TK_Kalibrierung_EN,
        1003: k.TK_AufloesungME,
        1040: k.TK_Wiederholpraezision,
        1041: k.TK_NichtZentrischeAntastung,
        1043: k.TK_AbweichungPoissonKoeffizientMO_EN,
        1044: k.TK_AbweichungElastizitaetsModul_MO_EN,
        1009: k.TK_TempDifferenz_MO_ME,
        1010: k.TK_AbweichungMittlereTemp_MO_ME,
        1111: d.TK_3d_ResKMG,
        2222: d.TK_3d_Wi_WE,
        3333: d.TK_3d_Wi_WB,
        4444: d.TK_3d_Wi_DeltaEKMG,
        1063: k.TK_Positioniergenauigkeit_Taster_X_Achse,
        1064: k.TK_Ebenheit_Messplatte,
        1065: k.TK_Kalibrierung_Ebenheit_Messplatte,
        1025: k.TK_Aufloesung_ME_Einstell,
        1016: k.TK_Korr_Zylin_GN_1_2,
        1018: k.TK_Korr_Rundheit_EN_1_2,
        1006: k.TK_Ebenheit_1_2_MO,
    }

    @staticmethod
    def get_component(modell: "TMU_Modell", type_name: str, lfdnr: int):
        component_class = ComponentFactory.COMPONENTS.get(type_name)
        return component_class(modell, TMU_ConstList, lfdnr) if component_class else None

    @staticmethod
    def get_all_components():
        return [
            component_class(None, TMU_ConstList, 0)
            for component_class in ComponentFactory.COMPONENTS.values()
        ]
