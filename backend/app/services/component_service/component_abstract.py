import math
from functools import cached_property

from app.services.component_service.EverythinForComponents import TMU_ConstList
from app.services.component_service.EverythinForComponents.TMU_Atom import TMU_Atom
from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TAuswertungsArchiv, TKompEditFieldsSet, \
    TMuKompRec
from app.services.component_service.EverythinForComponents.TMuKompRec import TMU_Verteilung, TMU_KennwertArt, \
    TMU_Freiheitsgrad

MU_NAN = math.nan


class TMU_Komponente(TMU_Atom):

    def __init__(
        self, AModell: "TMU_Modell", AnID: int, AConstList: TMU_ConstList, AFormel: str
    ):
        super().__init__(AnID, "Komponente")
        self.data = TMuKompRec(
            TermL0=MU_NAN,
            TermL1=MU_NAN,
            Verteilung="Verteilung_Undefiniert",  # String-Wert wird akzeptiert
            KennwertArt="KennwertArt_Undefiniert",  # String-Wert wird akzeptiert
            Freiheitsgrad="Freiheitsgrad_Undefiniert",  # String-Wert wird akzeptiert
            FreiN_minus_1=0,
            Flags=1,
        )
        self.modell: "TMU_Modell" = AModell
        self.const_list: object = AConstList
        self.formel: str = AFormel
        self.modl_txt_id: int = 0
        self.komp_txt_id: int = 0
        self.arch_data: TAuswertungsArchiv | None = None
        self.ConstNeeded: list[TKompConstants] = [TKompConstants["TC_Messwert"]]
        self.freikat_text: str = ""
        self.c1_val: float = 1
        self.c2_val: float = 1
        self.fields_to_edit: TKompEditFieldsSet | None = None
        self.position: int = 0
        self.einheit_ergebnis: str = ""
        self.clear()

    def setData(self, data: dict) -> None:
        if data.get('KennwertArt') is not None:
            # Verwende die _get_value-Methode für eine sichere Enum-Konvertierung
            self.data.KennwertArt = TMU_KennwertArt._get_value(data['KennwertArt'])

        if data.get('Freiheitsgrad') is not None:
            self.data.Freiheitsgrad = TMU_Freiheitsgrad._get_value(data['Freiheitsgrad'])

        if data.get('FreiN_minus_1') is not None:
            self.data.FreiN_minus_1 = data['FreiN_minus_1']

        if data.get('TermL0') is not None:
            self.data.TermL0 = data['TermL0']

        if data.get('TermL1') is not None:
            self.data.TermL1 = data['TermL1']

        if data.get('Verteilung') is not None:
            self.data.Verteilung = TMU_Verteilung._get_value(data['Verteilung'])

        if data.get('Flags') is not None:
            self.data.Flags = data['Flags']
    def asciiformel(self) -> str:
        return self.formel

    def addConstNeededToModell(self):
        if self.modell is not None:
            for const in self.ConstNeeded:
                self.modell.const_needed.add(const)
                self.modell.const_list.const_map[const] = None

    def clear(self):
        self.data = TMuKompRec(
            TermL0=MU_NAN,
            TermL1=MU_NAN,
            Verteilung="Verteilung_Undefiniert",  # String-Wert wird akzeptiert
            KennwertArt="KennwertArt_Undefiniert",  # String-Wert wird akzeptiert
            Freiheitsgrad="Freiheitsgrad_Undefiniert",  # String-Wert wird akzeptiert
            FreiN_minus_1=0,
            Flags=1,
        )

    def std_unsicherheit(self, l: float) -> float:
        if not is_valid_number(l):
            return MU_NAN

        verteilung = self.data.Verteilung.name
        kennwert = self.data.KennwertArt.name

        try:
            if verteilung == "V_Rechteck":
                if kennwert == "K_HalbWeite":
                    return l / math.sqrt(3)
                elif kennwert == "K_Spannweite":
                    return l / (2 * math.sqrt(3))
                elif kennwert == "K_Standardabweichung":
                    return l

            elif verteilung == "V_Normal":
                if kennwert == "K_HalbWeite":
                    return l / 2
                elif kennwert == "K_Spannweite":
                    return l / 4
                elif kennwert == "K_Standardabweichung":
                    return l

            elif verteilung == "V_Dreieck":
                if kennwert == "K_HalbWeite":
                    return l / math.sqrt(6)
                elif kennwert == "K_Spannweite":
                    return l / (2 * math.sqrt(6))
                elif kennwert == "K_Standardabweichung":
                    return l
        except Exception as e:
            print(f"Fehler bei std_unsicherheit(): {e}")

        return MU_NAN

    def a_val(self) -> float:
        return self.data.TermL0

    def b_val(self) -> float:
        return self.data.TermL1

    def std_unsicherheit_l0(self) -> float:
        return self.std_unsicherheit(self.a_val())

    def std_unsicherheit_l1(self) -> float:
        return self.std_unsicherheit(self.b_val())

    def sensititivty_c1(self) -> float:
        return self.c1_val

    def sensititivty_c2(self) -> float:
        return self.c2_val

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.data.Freiheitsgrad.name == "FG_unbegrenzt":
                return 1000
            elif self.data.Freiheitsgrad.name == "FG_N_Minus1":
                if self.data.FreiN_minus_1 > 0:
                    return self.data.FreiN_minus_1
        except Exception as e:
            print(f"Fehler bei effektiver_freiheitsgrad: {e}")
        return MU_NAN


    def unsicherheitsbeitrag_l0(self) -> float:
        su = self.std_unsicherheit(self.a_val())
        c1 = self.sensititivty_c1()
        if is_valid_number(su) and is_valid_number(c1):
            return su * c1
        return MU_NAN

    def unsicherheitsbeitrag_l1(self) -> float:
        su = self.std_unsicherheit(self.b_val())
        c2 = self.sensititivty_c2()
        l = self.modell.const_list.const_map[TKompConstants.TC_Messwert] * 1000  # mm → µm
        if is_valid_number(su) and is_valid_number(c2) and is_valid_number(l):
            return su * c2 * l
        return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            su0 = self.unsicherheitsbeitrag_l0()
            su1 = self.unsicherheitsbeitrag_l1()

            if math.isnan(su0) or math.isnan(su1):
                return MU_NAN

            if self.data.Flags < 0:
                return MU_NAN

            return math.sqrt(self.data.Flags) * (abs(su0) + abs(su1))

        except Exception as e:
            return MU_NAN

    def varianz(self) -> float:
        try:
            ub = self.unsicherheitsbeitrag
            print("Komponente: ",self,ub)
            if is_valid_number(ub):
                return ub ** 2
        except Exception as e:
            print(f"Fehler bei varianz(): {e}")
        return MU_NAN

def is_valid_number(value: float) -> bool:
    return value is not None and not math.isnan(value)
