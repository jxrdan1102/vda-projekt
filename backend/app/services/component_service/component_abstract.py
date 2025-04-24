import math

from app.services.component_service.EverythinForComponents import TMU_ConstList
from app.services.component_service.EverythinForComponents.TMU_Atom import TMU_Atom
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
)
from app.services.component_service.EverythinForComponents.TMuKompRec import (
    TAuswertungsArchiv,
    TKompEditFieldsSet,
    TMuKompRec,
)

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
        self.modell: object = AModell
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

    def setData(self, data: TMuKompRec):
        self.data = data

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

    def is_valid(self):
        data = self.data
        result = (
            (("EF_Term0" not in self.FieldsToEdit) or (data["TermL0"] != MU_NAN))
            and (("EF_Term1" not in self.FieldsToEdit) or (data["TermL1"] != MU_NAN))
            and (
                ("EF_Verteilung" not in self.FieldsToEdit)
                or (data["Verteilung"] != "Verteilung_Undefiniert")
            )
            and (
                ("EF_Kennwertart" not in self.FieldsToEdit)
                or (data["KennwertArt"] != "KennwertArt_Undefiniert")
            )
            and (
                ("EF_Freheitsgrad" not in self.FieldsToEdit)
                or (data["Freiheitsgrad"] != "Freiheitsgrad_Undefiniert")
            )
        )

        if data["Freiheitsgrad"] == "FG_N_Minus1":
            result = result and (data["FreiN_minus_1"] > 0)
        return result

    def std_unsicherheit(self, l: float) -> float:
        if l != MU_NAN:
            # Check distribution and return appropriate uncertainty
            if self.data.Verteilung.name == "V_Rechteck":
                if self.data.KennwertArt.name == "K_HalbWeite":
                    return l / math.sqrt(3)
                elif self.data.KennwertArt.name == "K_Spannweite":
                    return l / (2 * math.sqrt(3))
                elif self.data.KennwertArt.name == "K_Standardabweichung":
                    return l
            elif self.data.Verteilung.name == "V_Normal":
                if self.data.KennwertArt.name == "K_HalbWeite":
                    return l / 2
                elif self.data.KennwertArt.name == "K_Spannweite":
                    return l / 4
                elif self.data.KennwertArt.name == "K_Standardabweichung":
                    return l
            elif self.data.Verteilung.name == "V_Dreieck":
                if self.data.KennwertArt.name == "K_HalbWeite":
                    return l / math.sqrt(6)
                elif self.data.KennwertArt.name == "K_Spannweite":
                    return l / (2 * math.sqrt(6))
                elif self.data.KennwertArt.name == "K_Standardabweichung":
                    return l
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
        if self.data.Freiheitsgrad.name == "FG_unbegrenzt":
            self.EffektiverFreiheitsgrad = 1000
            return 1000
        elif self.data.Freiheitsgrad.name == "FG_N_Minus1":
            if self.data.FreiN_minus_1 > 0:
                self.EffektiverFreiheitsgrad = self.data.FreiN_minus_1
                return self.data.FreiN_minus_1
            return MU_NAN
        return MU_NAN

    def unsicherheitsbeitrag_l0(self) -> float:
        su = self.std_unsicherheit(self.a_val())
        c1 = self.sensititivty_c1()
        if su != MU_NAN and c1 != MU_NAN:
            return su * c1
        return MU_NAN

    def unsicherheitsbeitrag_l1(self) -> float:
        su = self.std_unsicherheit(self.b_val())
        c2 = self.sensititivty_c2()
        l = 25 * 1000  # Messwert in mm Berechnung in µm
        if su != MU_NAN and c2 != MU_NAN and l != MU_NAN:
            return su * c2 * l
        return MU_NAN

    @property
    def unsicherheitsbeitrag(self) -> float:
        su0 = self.unsicherheitsbeitrag_l0()
        su1 = self.unsicherheitsbeitrag_l1()
        if su0 != MU_NAN and su1 != MU_NAN:
            if self.id == 4 or self.id == 6:
                self.data.Flags = 2
            return math.sqrt(self.data.Flags) * (abs(su0) + abs(su1))
        return MU_NAN

    def varianz(self) -> float:
        ub = self.unsicherheitsbeitrag
        if not math.isnan(ub):
            return ub**2
        return MU_NAN

    def prep_archiv(self):
        self.arch_data = {
            "AVAL": self.a_val(),
            "BVAL": self.b_val(),
            "ASUL0": self.std_unsicherheit_l0(),
            "ASUL1": self.std_unsicherheit_l1(),
            "SensC1": self.sensititivty_c1(),
            "SensC2": self.sensititivty_c2(),
            "FreiEff": self.effektiver_freiheitsgrad,
            "UNSBL0": self.unsicherheitsbeitrag_l0,
            "UNSBL1": self.unsicherheitsbeitrag_l1,
            "UnsB": self.unsicherheitsbeitrag,
            "VARIANZ": self.varianz(),
        }

    # Placeholder for database load and save functions (to be implemented)
    def db_load(self, analyse_id: int):
        pass

    def db_save(self, analyse_id: int):
        pass

    def debug_str(self, s: list[str]) -> bool:
        s.append("Berechnete Daten:")  # For simplicity
        return False

    def debug_grid(self, grid: list[list[str]]) -> bool:
        grid.append(["Daten", "Werte"])
        return False
