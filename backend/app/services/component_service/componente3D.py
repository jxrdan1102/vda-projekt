import math

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.component_abstract import MU_NAN, TMU_Komponente


class TMU_3DKomponente(TMU_Komponente):
    def __init__(self, modell, komp_id, const_list, formel):
        try:
            super().__init__(modell, komp_id, const_list, formel)
            self.ConstNeeded = [
                TKompConstants["TC_3d_KMG_A"],
                TKompConstants["TC_3d_KMG_K"],
                TKompConstants["TC_3d_KMG_Uc"],
                TKompConstants["TC_3d_KMG_alphaM"],
                TKompConstants["TC_3d_KMG_LT"]
            ]
            self.c2_val = 0
            self.copy_source = None
            self.messpunkt_anzahl = None
            self.anzahl_messungen: int | None = None
            self.id: int
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.__init__] {e}")


    def a_val(self) -> float:
        return self.standard_unsicherheit_su()

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval
            elif self.data.TermL0 != 0:
                return self.data.TermL0
            else:
                a = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]  # Platzhalter für 'Konstanter Teil A'
                return a / 3 if a != MU_NAN else MU_NAN
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.standard_unsicherheit_su] {e}")
            return MU_NAN

    def is_valid(self) -> bool:
        try:
            f = self.fields_to_edit
            return (
                ("EF_Term0" not in f or self.data.TermL0 != MU_NAN)
                and ("EF_Verteilung" not in f or self.data.Verteilung.name != "Verteilung_Undefiniert")
                and ("EF_Kennwertart" not in f or self.data.KennwertArt.name != "KennwertArt_Undefiniert")
            )
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.is_valid] {e}")
            return False

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            return self.arch_data.frei_eff if self.archiv else 1000
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.effektiver_freiheitsgrad] {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            return self.arch_data.bval if self.archiv else 1
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.b_val] {e}")
            return MU_NAN

    def g_val(self) -> float:
        return 1.0

    def copy_methode(self, komp: str):
        try:
            self.copy_source = self.modell.find_komponente_by_classname(self.id)
            if self.copy_source and self.sensititivty_c1() != MU_NAN:
                self.data.KennwertArt = self.copy_source.data.KennwertArt
                self.data.TermL1 = self.copy_source.data.TermL1
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.copy_methode] {e}")

    def anzahl_messungen(self) -> int:
        try:
            return round(self.data.TermL1)
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.anzahl_messungen] {e}")
            return 0

    def tabelle1_su(self, l: float) -> float:
        try:
            if self.archiv:
                return self.arch_data.stdu
            if l == MU_NAN:
                return MU_NAN

            verteilung = self.data.Verteilung.name
            art = self.data.KennwertArt.name

            if verteilung == "V3D_Rechteck":
                if art == "K_HalbWeite":
                    return l / math.sqrt(3)
                if art == "K_Spannweite":
                    return l / (2 * math.sqrt(3))
                if art == "K_Standardabweichung":
                    return l

            elif verteilung == "V3D_Normal":
                if art == "K_HalbWeite":
                    return l / 2
                if art == "K_Spannweite":
                    return l / 4
                if art == "K_Standardabweichung":
                    return l

            elif verteilung == "V3d_Dreieck":
                if art == "K_HalbWeite":
                    return l / math.sqrt(6)
                if art == "K_Spannweite":
                    return l / (2 * math.sqrt(6))
                if art == "K_Standardabweichung":
                    return l

            return MU_NAN
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.tabelle1_su] {e}")
            return MU_NAN

    @property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb
            siai = self.standard_unsicherheit_su()
            b = self.b_val()
            g = self.g_val()
            ci = self.sensititivty_c1()
            if all(val != MU_NAN for val in [siai, b, g, ci]):
                return siai * b * g * ci
            return MU_NAN
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.unsicherheitsbeitrag] {e}")
            return MU_NAN

    def mindestpunkt_anzahl(self, element: str) -> int:
        try:
            mapping = {
                "Punkt": 1,
                "Gerade": 2,
                "Ebene": 3,
                "Kreis": 4,
                "Halbkugel": 5,
                "Zylinder": 6,
                "Kegel": 7,
            }
            return mapping.get(element, 0)
        except Exception as e:
            print(f"[Fehler in TMU_3DKomponente.mindestpunkt_anzahl] {e}")
            return 0