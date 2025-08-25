import math

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import TMU_Komponente

MU_NAN = math.nan
def zeiss_reihe_d(steigung: float) -> float:
    if steigung == 0.2: return 0.13
    elif steigung == 0.25: return 0.17
    elif steigung == 0.3: return 0.17
    elif steigung == 0.35: return 0.22
    elif steigung == 0.4: return 0.25
    elif steigung == 0.45: return 0.29
    elif steigung == 0.5: return 0.29
    elif steigung == 0.6: return 0.335
    elif steigung == 0.7: return 0.455
    elif steigung == 0.75: return 0.455
    elif steigung == 0.8: return 0.455
    elif steigung == 1: return 0.62
    elif steigung == 1.25: return 0.725
    elif steigung == 1.5: return 0.895
    elif steigung == 1.75: return 1.1
    elif steigung == 2: return 1.35
    elif steigung == 2.5: return 1.65
    elif steigung == 3: return 2.05
    elif steigung == 3.5: return 2.05
    elif steigung == 4: return 2.55
    elif steigung == 4.5: return 2.55
    elif steigung == 5: return 3.2
    elif steigung == 5.5: return 3.2
    elif steigung == 6: return 4
    else: return MU_NAN

class TK_StreuungMesskraft(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1042, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_DurchmesserMesseinsatzME"],
                TKompConstants["TC_Elast_Modul_Normal"],
                TKompConstants["TC_Elast_Modul_MO"],
                TKompConstants["TC_Poisson_Koeff_Normal"],
                TKompConstants["TC_Poisson_Koeff_MO"],
                TKompConstants["TC_Korrelationskoeffizient"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freiheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteA.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in KomponenteA.clear] {e}")

    def sensititivty_c1(self):
        try:
            dk = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME] / 1000
            En = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_Normal]
            Emo = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_MO]
            Vn = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_Normal]
            Vmo = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_MO]
            F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            r = self.modell.const_list.const_map[TKompConstants.TC_Korrelationskoeffizient]
            E = (Emo + En) / 2
            v = (Vmo + Vn) / 2
            if any(val == MU_NAN for val in [dk, En, Emo, E, v, Vn, Vmo, F, r]):
                return MU_NAN
            return (
                    1.1
                    * math.pow(10, 6)
                    * math.pow(dk, -1 / 3)
                    * math.pow((1 - v**2) / E, 2 / 3)
                    * math.pow(F, -1 / 3)
            )
        except Exception as e:
            print(f"[Fehler in KomponenteA.sensititivty_c1] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0
            su = self.std_unsicherheit(self.a_val())
            c1 = self.sensititivty_c1()
            r = self.modell.const_list.const_map[TKompConstants.TC_Korrelationskoeffizient]
            if all(x != MU_NAN for x in [su, c1, r]) and r <= 1:
                return 2 * su * c1 * math.sqrt(1 - r)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteA.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_KalibrierungME(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1001, AConstList, "&delta;I<sub>ME</sub>")
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0.035,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_KalibrierungME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 3
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_KalibrierungME.clear] {e}")


class TK_Kalibrierung_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1027, AConstList, "&delta;I<sub>ENK</sub>")
            self.ConstNeeded += [
                TKompConstants["TC_NennmassEN"]
            ]
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0.05,
                TermL1=0.0000012,
                Verteilung="V_Normal",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_EN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 3
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_EN.clear] {e}")

    def unsicherheitsbeitrag_l1(self):
        try:
            if hasattr(self, "archiv") and self.archiv:
                return self.ArchData["UNSBL1"]
            su = self.std_unsicherheit(self.b_val())
            c2 = self.sensititivty_c2()
            NennmassEN = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN] * 1000

            if su != MU_NAN and c2 != MU_NAN and NennmassEN != MU_NAN:
                return su * c2 * NennmassEN
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_EN.unsicherheitsbeitrag_l1] {e}")
            return MU_NAN

class TK_AufloesungME(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1003, AConstList, "&delta;I<sub>MEW</sub>")
            self.data = TMuKompRec(
                TermL0=0.005,
                TermL1=0,
                Verteilung=2,
                KennwertArt=3,
                Freiheitsgrad=2,
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []
            self.addConstNeededToModell()
            self.lfdnr = lfdnr
        except Exception as e:
            print(f"[Fehler in TK_AufloesungME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_AufloesungME.clear] {e}")


class TK_Wiederholpraezision(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1040, AConstList, "&delta;W")
            self.data = TMuKompRec(
                TermL0=0.01,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.lfdnr = lfdnr
            self.ConstNeeded += []
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Wiederholpraezision.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 3
            self.data.KennwertArt = 4
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_Wiederholpraezision.clear] {e}")

class TK_NichtZentrischeAntastung(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1041, AConstList, "&delta;I<sub>v</sub>")
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.lfdnr = lfdnr

            self.ConstNeeded += [
                TKompConstants["TC_Radius_der_Zone_des_Spiels"],
                TKompConstants["TC_Laenge_kurze_Kante_PEM"],
                TKompConstants["TC_Tol_Abw_Spanne_ISO_3650"],
            ]
            self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_NichtZentrischeAntastung.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 4
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_NichtZentrischeAntastung.clear] {e}")

    def a_val(self):
        try:
            r = self.modell.const_list.const_map[TKompConstants.TC_Radius_der_Zone_des_Spiels]
            g = self.modell.const_list.const_map[TKompConstants.TC_Laenge_kurze_Kante_PEM]
            v = self.modell.const_list.const_map[TKompConstants.TC_Tol_Abw_Spanne_ISO_3650]

            if g != 0 and r != MU_NAN and g != MU_NAN and v != MU_NAN:
                return r * v / g
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_NichtZentrischeAntastung.a_val] {e}")
            return MU_NAN

    def b_val(self):
        return 0


class TK_AbweichungPoissonKoeffizientMO_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1043, AConstList, "&delta;V")
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_DurchmesserMesseinsatzME"],
                TKompConstants["TC_Elast_Modul_Normal"],
                TKompConstants["TC_Elast_Modul_MO"],
                TKompConstants["TC_Poisson_Koeff_Normal"],
                TKompConstants["TC_Poisson_Koeff_MO"],
            ]
            self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 4
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.clear] {e}")

    def a_Val(self):
        try:
            Vn = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_Normal]
            Vmo = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_MO]
            if Vn != MU_NAN and Vmo != MU_NAN:
                return abs(Vmo - Vn) / 2
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.a_Val] {e}")
            return MU_NAN

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            dk = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME] / 1000  # Eingabe in mm, Berechnung in m
            En = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_Normal]
            Emo = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_MO]
            Vn = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_Normal]
            Vmo = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_MO]
            F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            v = (Vmo + Vn) / 2
            E = (Emo + En) / 2

            if any(val == MU_NAN for val in [dk, En, Emo, E, v, Vn, Vmo, F]):
                return MU_NAN
            else:
                # Formel zur Berechnung der Sensitivität C1
                return (
                    -1.47
                    * math.pow(10, 6)
                    * math.pow(dk, -1 / 3)
                    * math.pow(F, 2 / 3)
                    * math.pow(E, -2 / 3)
                    * v
                    * math.pow(1 - math.pow(v, 2), -1 / 3)
                )
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.sensititivty_c1] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l0(self):
        try:
            su = self.StdUnsicherheit(self.a_Val())
            c1 = self.sensititivty_c1()
            if su != MU_NAN and c1 != MU_NAN:
                return 2 * su * c1
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN

    def StdUnsicherheit(self, value):
        try:
            if value == MU_NAN:
                return MU_NAN
            else:
                return value * 0.1
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.StdUnsicherheit] {e}")
            return MU_NAN

class TK_AbweichungElastizitaetsModul_MO_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1044, AConstList, "&delta;E")
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_DurchmesserMesseinsatzME"],
                TKompConstants["TC_Elast_Modul_Normal"],
                TKompConstants["TC_Elast_Modul_MO"],
                TKompConstants["TC_Poisson_Koeff_Normal"],
                TKompConstants["TC_Poisson_Koeff_MO"],
            ]
            self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_AbweichungElastizitaetsModul_MO_EN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 4
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_AbweichungElastizitaetsModul_MO_EN.clear] {e}")

    def a_val(self):
        try:
            En = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_Normal]
            Emo = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_MO]
            if En != MU_NAN and Emo != MU_NAN:
                return abs(Emo - En) / 2
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_AbweichungElastizitaetsModul_MO_EN.a_val] {e}")
            return MU_NAN

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            dk = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME] / 1000  # Eingabe in mm, Berechnung in m
            En = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_Normal]
            Emo = self.modell.const_list.const_map[TKompConstants.TC_Elast_Modul_MO]
            Vn = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_Normal]
            Vmo = self.modell.const_list.const_map[TKompConstants.TC_Poisson_Koeff_MO]
            F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            v = (Vmo + Vn) / 2
            E = (Emo + En) / 2

            if any(val == MU_NAN for val in [dk, En, Emo, E, v, Vn, Vmo, F]):
                return MU_NAN
            else:
                # Formel zur Berechnung der Sensitivität C1
                return (
                    -0.733
                    * math.pow(10, 6)
                    * math.pow(dk, -1 / 3)
                    * math.pow(F, 2 / 3)
                    * math.pow(E, -5 / 3)
                    * math.pow(1 - math.pow(v, 2), 2 / 3)
                )
        except Exception as e:
            print(f"[Fehler in TK_AbweichungElastizitaetsModul_MO_EN.sensititivty_c1] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l0(self):
        try:
            su = self.std_unsicherheit(self.a_val())
            c1 = self.sensititivty_c1()
            if su != MU_NAN and c1 != MU_NAN:
                return 2 * su * c1
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_AbweichungElastizitaetsModul_MO_EN.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_TempDifferenz_MO_ME(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            super().__init__(AModell, 1009, AConstList, "&delta;t")
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_TempME"],
                TKompConstants["TC_TempMO"],
                TKompConstants["TC_AusdehnKoeffME"],
                TKompConstants["TC_AusdehnKoeffMO"],
            ]
            self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]

            self.c1_val = 0  # Festlegung, c2 wird errechnet
            self.Einheit = "°C"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_TempDifferenz_MO_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 3
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_TempDifferenz_MO_ME.clear] {e}")

    def b_val(self):
        try:
            tx = self.modell.const_list.const_map[TKompConstants.TC_TempMO]
            tn = self.modell.const_list.const_map[TKompConstants.TC_TempME]
            if tx != MU_NAN and tn != MU_NAN:
                return abs(tx - tn)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_TempDifferenz_MO_ME.b_val] {e}")
            return MU_NAN

    def sensititivty_c2(self):
        try:
            ax = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffME]
            an = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffMO]
            if ax != MU_NAN and an != MU_NAN:
                return (ax + an) / 2
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_TempDifferenz_MO_ME.sensititivty_c2] {e}")
            return MU_NAN

class TK_AbweichungMittlereTemp_MO_ME(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
        try:
            # Aufruf des Konstruktors der Basisklasse
            super().__init__(AModell, 1010, AConstList, "notthere")
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.lfdnr = lfdnr
            #self.id =10
            # Die spezifischen Initialisierungen für diese Klasse
            self.ConstNeeded += [
                TKompConstants["TC_TempME"],
                TKompConstants["TC_TempMO"],
                TKompConstants["TC_AusdehnKoeffME"],
                TKompConstants["TC_AusdehnKoeffMO"],
            ]
            self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]
            self.c1_val = 0
            self.Einheit = "°C"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_AbweichungMittlereTemp_MO_ME.__init__] {e}")

    def clear(self):
        try:
            # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in TK_AbweichungMittlereTemp_MO_ME.clear] {e}")

    def b_val(self):
        try:
            # Berechnet den Temperaturunterschied b_Val
            tx = self.modell.const_list.const_map[TKompConstants.TC_TempMO]
            tn = self.modell.const_list.const_map[TKompConstants.TC_TempME]

            if tx is None or tn is None:
                return None
            return abs((tx + tn) / 2 - 20)
        except Exception as e:
            print(f"[Fehler in TK_AbweichungMittlereTemp_MO_ME.b_val] {e}")
            return None

    def sensititivty_c2(self):
        try:
            # Berechnet die Sensitivität C2 basierend auf den
            # Ausdehnungskoeffizienten
            ax = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffME]
            an = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffMO]

            if ax is None or an is None:
                return None
            return abs(ax - an) / (2 * math.sqrt(3))
        except Exception as e:
            print(f"[Fehler in TK_AbweichungMittlereTemp_MO_ME.sensititivty_c2] {e}")
            return None

class TK_ErmittelteMessabweichungME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_ErmittelteMessabweichungME.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 1
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_ErmittelteMessabweichungME.clear] {e}")

class TK_Positioniergenauigkeit_Taster_X_Achse(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Hoehendifferenz_Stuetzpunkte"],
                TKompConstants["TC_Laenge_Messobjekt"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Positioniergenauigkeit_Taster_X_Achse.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Positioniergenauigkeit_Taster_X_Achse.clear] {e}")

    def sensititivty_c1(self) -> float:
        h = self.modell.const_list.const_map[TKompConstants.TC_Hoehendifferenz_Stuetzpunkte]
        L = self.modell.const_list.const_map[TKompConstants.TC_Laenge_Messobjekt]
        if not math.isnan(h) and not math.isnan(L) and L != 0:
            return h/L
        return MU_NAN

class TK_Ebenheit_Messplatte(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Ebenheit_Messplatte.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Ebenheit_Messplatte.clear] {e}")

    def b_val(self):
        return 0

class TK_Kalibrierung_Ebenheit_Messplatte(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Ebenheit_Messplatte.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Ebenheit_Messplatte.clear] {e}")

    def b_val(self):
        return 0

class TK_Aufloesung_ME_Einstell(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Aufloesung_ME_Einstell.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Aufloesung_ME_Einstell.clear] {e}")


class TK_Ebenheit_1_2_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Ebenheit_1_2_MO.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Ebenheit_1_2_MO.clear] {e}")


class TK_Korr_Zylin_GN_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Zylin_GN_1_2.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Korr_Zylin_GN_1_2.clear] {e}")



class TK_Korr_Rundheit_EN_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1002, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Rundheit_EN_1_2.__init__] {e}")
    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 1
        except Exception as e:
            print(f"[Fehler in TK_Korr_Rundheit_EN_1_2.clear] {e}")

class TK_Ebenheit_1_2_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1005, const_list, "&delta;E<sub>ME</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",      # Entspricht V_Rechteck in Pascal
                KennwertArt="K_Spannweite",    # Entspricht K_Spannweite
                Freiheitsgrad="FG_unbegrenzt", # Entspricht FG_unbegrenzt
                FreiN_minus_1=0,
                Flags=1
            )

            self.ConstNeeded += []
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
            self.Einheit = None
            self.addConstNeededToModell()

        except Exception as e:
            print(f"[Fehler in TK_Ebenheit_1_2_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Ebenheit_1_2_ME.clear] {e}")

class TK_ParallelitaetMessflaechenME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1007, const_list, "&delta;P<sub>ME</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",      # entspricht V_Rechteck
                KennwertArt="K_Spannweite",    # entspricht K_Spannweite
                Freiheitsgrad="FG_unbegrenzt", # entspricht FG_unbegrenzt
                FreiN_minus_1=0,
                Flags=1
            )

            self.ConstNeeded += []
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
            self.Einheit = None
            self.addConstNeededToModell()

        except Exception as e:
            print(f"[Fehler in TK_ParallelitaetMessflaechenME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_ParallelitaetMessflaechenME.clear] {e}")


class TK_KorrParallelitaet_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1008, const_list, "&delta;P<sub>MO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",       # entspricht Delphi: V_Rechteck
                KennwertArt="K_Spannweite",     # entspricht K_Spannweite
                Freiheitsgrad="FG_unbegrenzt",  # entspricht FG_unbegrenzt
                FreiN_minus_1=0,
                Flags=1
            )

            self.ConstNeeded += []
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
            self.Einheit = None
            self.addConstNeededToModell()

        except Exception as e:
            print(f"[Fehler in TK_KorrParallelitaet_MO.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_KorrParallelitaet_MO.clear] {e}")


class TK_VerformungMO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1011, const_list, "&delta;F<sub>Z</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )

            self.ConstNeeded += [
                TKompConstants["TC_MantellinieMO"],
                TKompConstants["TC_DurchmesserMessflaeche"],
                TKompConstants["TC_MesskraftME"]
            ]
            self.c2_val = 0  # Festlegung wie in Delphi
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_VerformungMO.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_VerformungMO.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1

            lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieMO]
            d = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMessflaeche]
            lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]

            l = max(lm, d) if lm != MU_NAN and d != MU_NAN else MU_NAN

            if l != MU_NAN and lx != MU_NAN:
                return 0.0938 * math.pow(lx, -1 / 3) * math.pow(l, -1)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_VerformungMO.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVAL
            return self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
        except Exception as e:
            print(f"[Fehler in TK_VerformungMO.b_val] {e}")
            return MU_NAN


class TK_Korr_Biegung_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1012, const_list, "&delta;F<sub>B</sub>")
            self.lfdnr = lfdnr
            self.const_list = const_list
            self.archiv = False
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )
            self.FieldsToEdit = []
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Biegung_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Korr_Biegung_ME.clear] {e}")


class TK_RundheitMessflaeche_1_2_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1013, const_list, "&delta;R<sub>MO</sub>")
            self.lfdnr = lfdnr
            self.const_list = const_list
            self.archiv = False
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )
            self.FieldsToEdit = []
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_RundheitMessflaeche_1_2_MO.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_RundheitMessflaeche_1_2_MO.clear] {e}")


class TK_Zylindrizitaet_MO_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1014, const_list, "&delta;Z<sub>MO</sub>")
            self.lfdnr = lfdnr
            self.const_list = const_list
            self.archiv = False
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )
            self.FieldsToEdit = []
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Zylindrizitaet_MO_1_2.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Zylindrizitaet_MO_1_2.clear] {e}")

class TK_Korr_Zylin_ME_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1015, const_list, "&delta;Z<sub>ME</sub>")
            self.lfdnr = lfdnr
            self.const_list = const_list
            self.archiv = False
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )
            self.FieldsToEdit = []
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Zylin_ME_1_2.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Korr_Zylin_ME_1_2.clear] {e}")

class TK_Korr_Rundheit_ME_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(
            modell,
            1017,
            const_list,
            "&delta;R<sub>ME</sub>"
        )
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_Spannweite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.FieldsToEdit = []
        self.addConstNeededToModell()

    def clear(self):
        super().clear()
        self.data.Verteilung = "V_Rechteck"
        self.data.KennwertArt = "K_Spannweite"
        self.data.Freiheitsgrad = "FG_unbegrenzt"


class TK_Korr_Rundheit_GN_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell,1019,const_list,"&delta;R<sub>GN</sub>")
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_Spannweite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.FieldsToEdit = []
        self.addConstNeededToModell()

    def clear(self):
        super().clear()
        self.data.Verteilung = "V_Rechteck"
        self.data.KennwertArt = "K_Spannweite"
        self.data.Freiheitsgrad = "FG_unbegrenzt"

class TK_Korr_Ebenheit_1_2(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell,1020,const_list,"&delta;E<sub>EN</sub>")
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_Spannweite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.lfdnr = lfdnr
        self.FieldsToEdit = []
        self.addConstNeededToModell()

    def clear(self):
        super().clear()
        self.data.Verteilung = "V_Rechteck"
        self.data.KennwertArt = "K_Spannweite"
        self.data.Freiheitsgrad = "FG_unbegrenzt"

class TK_Korr_Parallelitaet_EN(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1021, const_list, "&delta;P<sub>EN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KorrParallelitaetENComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KorrParallelitaetENComponent.clear] {e}")

class TK_Verformung_MOsph_MEplan(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1022, const_list, "")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_MesskraftSchwankungME"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0  # c1 wird errechnet
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEplan.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEplan.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1
            lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
            F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            if any(x == MU_NAN for x in [lx, F]) or (lx * F) == 0:
                return MU_NAN
            return 0.543 * math.pow(lx * F, -1 / 3)
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEplan.sensititivty_c1] {e}")
            return MU_NAN

    def a_val(self):
        try:
            if self.archiv:
                return self.arch_data.AVal
            return self.modell.const_list.const_map[TKompConstants.TC_MesskraftSchwankungME]
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEplan.a_val] {e}")
            return MU_NAN


class TK_Verformung_MOsph_MEsph(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1023, const_list, "")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_DurchmesserMesseinsatzME"],
                TKompConstants["TC_MesskraftSchwankungME"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0  # c1 wird errechnet
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEsph.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEsph.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1
            lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
            F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            d = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
            if any(x == MU_NAN or x == 0 for x in [lx, d, F]):
                return MU_NAN
            return 0.277 * math.pow(F, 1 / 3) * math.pow((1 / lx) + (1 / d), 1 / 3)
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEsph.sensititivty_c1] {e}")
            return MU_NAN

    def a_val(self):
        try:
            if self.archiv:
                return self.arch_data.AVal
            return self.modell.const_list.const_map[TKompConstants.TC_MesskraftSchwankungME]
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOsph_MEsph.a_val] {e}")
            return MU_NAN


class TK_Verformung_MOzyl_MEsph(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1024, const_list, "")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_DurchmesserMesseinsatzME"],
                TKompConstants["TC_MesskraftSchwankungME"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0  # c1 wird errechnet
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOzyl_MEsph.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOzyl_MEsph.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1

            lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
            d = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]

            if any(x == MU_NAN or x == 0 for x in [lx, d]):
                return MU_NAN

            divident = ((1 / d) + (1 / lx)) * (1 / d)
            divident = math.pow(divident, 1 / 4)  # 4. Wurzel
            divisor = (2 / d) + (1 / lx)
            divisor = math.pow(divisor, 1 / 6)    # 6. Wurzel

            return 0.32 * (divident / divisor)
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOzyl_MEsph.sensititivty_c1] {e}")
            return MU_NAN

    def a_val(self):
        try:
            if self.archiv:
                return self.arch_data.AVal
            return self.modell.const_list.const_map[TKompConstants.TC_MesskraftSchwankungME]
        except Exception as e:
            print(f"[Fehler in TK_Verformung_MOzyl_MEsph.a_val] {e}")
            return MU_NAN


class TK_Abweichung_Nennmass_EN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1026, const_list, "&delta;I<sub>ENA</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten benötigt
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Abweichung_Nennmass_EN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Abweichung_Nennmass_EN.clear] {e}")


class TK_Korr_TempDifferenz_EN_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1028, const_list, "&delta;t<sub>EN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.c1_val = 0  # Vorbelegung
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_AusdehnKoeffEN"],
                TKompConstants["TC_AusdehnKoeffME"],
                TKompConstants["TC_TempME"],
                TKompConstants["TC_TempEN"],
                TKompConstants["TC_NennmassEN"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "°C"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME.clear] {e}")

    def sensititivty_c2(self):
        try:
            if self.archiv:
                return self.arch_data.SensC2
            alphaEN = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffEN]
            alphaN = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffME]
            if MU_NAN in [alphaEN, alphaN]:
                return MU_NAN
            return (alphaEN + alphaN) / 2
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME.sensititivty_c2] {e}")
            return MU_NAN

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVal
            t_en = self.modell.const_list.const_map[TKompConstants["TC_TempEN"]]
            t_me = self.modell.const_list.const_map[TKompConstants["TC_TempME"]]
            if MU_NAN in [t_en, t_me]:
                return MU_NAN
            return abs(t_en - t_me)
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME.b_val] {e}")
            return MU_NAN

class TK_Korr_TempDifferenz_EN_ME_20(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1029, const_list, "&delta;&Delta;t<sub>EN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            #self.c2_val = 0
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_AusdehnKoeffEN"],
                TKompConstants["TC_AusdehnKoeffME"],
                TKompConstants["TC_TempME"],
                TKompConstants["TC_TempEN"],
                TKompConstants["TC_NennmassEN"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "°C"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME20.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME20.clear] {e}")

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVal
            ten = self.modell.const_list.const_map[TKompConstants.TC_TempEN]
            tn = self.modell.const_list.const_map[TKompConstants.TC_TempME]
            if MU_NAN in [ten, tn]:
                return MU_NAN
            return abs((ten + tn) / 2 - 20)
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME20.b_val] {e}")
            return MU_NAN

    def sensititivty_c2(self):
        try:
            if self.archiv:
                return self.arch_data.SensC2
            alpha_en = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffEN]
            alpha_n = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffME]
            if MU_NAN in [alpha_en, alpha_n]:
                return MU_NAN
            return abs(alpha_en - alpha_n) / (2 * math.sqrt(3))
        except Exception as e:
            print(f"[Fehler in KorrTempDifferenzENME20.sensititivty_c2] {e}")
            return MU_NAN


class TK_Drift_GN(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1031, const_list, "&delta;D<sub>EN</sub>")
            self.const_list = const_list
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "°C"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Drift_GN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Drift_GN.clear] {e}")

class TK_Korr_Abplattung_Messkraft(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr, AnID = 1032):
        try:
            super().__init__(modell, AnID, const_list, "&delta;F<sub>GEOMETRIE</sub>")
            self.const_list = const_list
            self.lfdnr = lfdnr
            self.c2_val = 0  # Vorbelegung, Berechnung für C1
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Abplattung_Messkraft.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Korr_Abplattung_Messkraft.clear] {e}")


class TK_Korr_Abplattung_Messkraft_ME_MO(TK_Korr_Abplattung_Messkraft):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, const_list,lfdnr,10321)
            self.Einheit = "N"
            self.lfdnr = lfdnr
            geom_me = self.modell.i_geometrie_me
            geom_mo = self.modell.i_geometrie_mo

            if geom_me == 1:
                if geom_mo == 2:
                    self.ConstNeeded += [TKompConstants["TC_MesskraftME"]]
                elif geom_mo == 3:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMessflaeche"],
                        TKompConstants["TC_MantellinieMO"],
                    ]
            elif geom_me == 2:
                if geom_mo in [1, 2, 3, 4]:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_MesskraftME"],
                    ]
            elif geom_me == 3:
                if geom_mo == 1:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_BreiteMessflaecheMO"],
                        TKompConstants["TC_MantellinieME"],
                    ]
                elif geom_mo in [2,3,4]:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_MesskraftME"],
                    ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Abplattung_Messkraft_ME_MO.__init__] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1

            c1 = 0
            geom_me = self.modell.i_geometrie_me
            geom_mo = self.modell.i_geometrie_mo

            if geom_me == 1:
                if geom_mo == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    c1 = 0.277 * math.pow(F * lx, -1 / 3)
                elif geom_mo == 3:
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    D = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMessflaeche]
                    lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieMO]
                    lb = min(D, lm)
                    c1 = 4.69e-2 * math.pow(lx, -1 / 3) * math.pow(lb, -1)

            elif geom_me == 2:
                if geom_mo == 1:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.277 * math.pow(F * dd, -1 / 3)
                elif geom_mo == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.277 * math.pow(F, -1 / 3) * math.pow((1 / lx) + (1 / dd), 1 / 3)
                elif geom_mo == 3:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / dd) + (1 / lx), 1 / 4) * \
                         math.pow((2 / dd) + (1 / lx), -1 / 6)
                elif geom_mo == 4:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / dd) - (1 / lx), 1 / 4) * \
                         math.pow((2 / dd) - (1 / lx), -1 / 6)

            elif geom_me == 3:
                if geom_mo == 1:
                    D = self.modell.const_list.const_map[TKompConstants.TC_BreiteMessflaecheMO]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieME]
                    lb = min(D, lm)
                    c1 = 4.69e-2 * math.pow(dd, -1 / 3) * math.pow(lb, -1)
                elif geom_mo == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / lx) + (1 / dd), 1 / 4) * \
                         math.pow((2 / lx) + (1 / dd), -1 / 6)
                elif geom_mo == 3:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / dd) + (1 / lx), 1 / 4) * \
                         math.pow((2 / dd) + (1 / lx), -1 / 6)
                elif geom_mo == 4:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / dd) - (1 / lx), 1 / 4) * \
                         math.pow((2 / dd) - (1 / lx), -1 / 6)

            return c1
        except Exception as e:
            print(f"[Fehler in TK_Korr_Abplattung_Messkraft_ME_MO.sensititivty_c1] {e}")
            return MU_NAN


class TK_Korr_Abplattung_Messkraft_ME_GN(TK_Korr_Abplattung_Messkraft):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, const_list, lfdnr, 10322)
            self.Einheit = "N"
            geom_me = self.modell.i_geometrie_me
            geom_en = self.modell.i_geometrie_en
            self.lfdnr = lfdnr
            if geom_me == 1:
                if geom_en == 2:
                    self.ConstNeeded += [TKompConstants["TC_MesskraftME"], TKompConstants["TC_DurchmesserEN"]]
                elif geom_en == 3:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMessflaeche"],
                        TKompConstants["TC_MantellinieEN"],
                    ]
            elif geom_me == 2:
                if geom_en == 1:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_MesskraftME"],
                    ]
                elif geom_en in [2, 3, 4]:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_MesskraftME"],
                        TKompConstants["TC_NennmassEN"],
                    ]
            elif geom_me == 4:
                if geom_en == 1:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_BreiteMessflaecheEN"],
                        TKompConstants["TC_MantellinieME"],
                    ]
                elif geom_en in [2, 3, 4]:
                    self.ConstNeeded += [
                        TKompConstants["TC_DurchmesserMesseinsatzME"],
                        TKompConstants["TC_MesskraftME"],
                        TKompConstants["TC_NennmassEN"],
                    ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Korr_Abplattung_Messkraft_ME_GN.__init__] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1

            c1 = 0
            geom_me = self.modell.i_geometrie_me
            geom_en = self.modell.i_geometrie_en
            cl = self.modell.const_list.const_map

            if geom_me == 1:
                if geom_en == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserEN]
                    c1 = 0.277 * math.pow(F * dd, -1 / 3)
                elif geom_en == 3:
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    D = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMessflaeche]
                    lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieEN]
                    lb = min(D, lm)
                    c1 = 4.69e-2 * math.pow(lx, -1 / 3) * math.pow(lb, -1)

            elif geom_me == 2:
                if geom_en == 1:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.277 * math.pow(F * dd, -1 / 3)
                elif geom_en == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.277 * math.pow(F, -1 / 3) * math.pow((1 / lx) + (1 / dd), 1 / 3)
                elif geom_en == 3:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / dd) + (1 / lx), 1 / 4) * \
                         math.pow((2 / dd) + (1 / lx), -1 / 6)
                elif geom_en == 4:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    delta1 = (1 / dd) - (1 / lx)
                    delta2 = (2 / dd) - (1 / lx)
                    if delta1 <= 0 or delta2 <= 0:
                        return MU_NAN
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow(delta1, 1 / 4) * \
                         math.pow(delta2, -1 / 6)

            elif geom_me == 3:
                if geom_en == 1:
                    D = self.modell.const_list.const_map[TKompConstants.TC_BreiteMessflaecheEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieME]
                    lb = min(D, lm)
                    c1 = 4.69e-2 * math.pow(dd, -1 / 3) * math.pow(lb, -1)
                elif geom_en == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / lx) + (1 / dd), 1 / 4) * \
                         math.pow((2 / lx) + (1 / dd), -1 / 6)
                elif geom_en == 3:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow((1 / dd) + (1 / lx), 1 / 4) * \
                         math.pow((2 / dd) + (1 / lx), -1 / 6)
                elif geom_en == 4:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                    delta1 = (1 / dd) - (1 / lx)
                    delta2 = (2 / dd) - (1 / lx)
                    if delta1 <= 0 or delta2 <= 0:
                        return MU_NAN
                    c1 = 0.320 * math.pow(F, -1 / 3) * math.pow(delta1, 1 / 4) * \
                         math.pow(delta2, -1 / 6)

            return c1
        except Exception as e:
            print(f"[Fehler in TK_Korr_Abplattung_Messkraft_ME_GN.sensititivty_c1] {e}")
            return MU_NAN

class TK_Kalibrierung_Faktor_Kennlinie_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1033, const_list, "&delta;B")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.c1_val = 0
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_FaktorKennlinieME"]
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Faktor_Kennlinie_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Faktor_Kennlinie_ME.clear] {e}")

    def sensititivty_c2(self):
        try:
            if self.archiv:
                return self.arch_data.SensC2
            b = self.modell.const_list.const_map[TKompConstants.TC_FaktorKennlinieME]
            if b != 0 and b != MU_NAN:
                return 1 / (b * b)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Faktor_Kennlinie_ME.sensititivty_c2] {e}")
            return MU_NAN

class TK_Kalibrierung_Parm_Kennlinie_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1034, const_list, "&delta;A")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            # Ursprünglich war hier TC_ParameterKennlinieME, aber Kommentar sagt falsche Konstante
            self.ConstNeeded += [
                TKompConstants["TC_FaktorKennlinieME"]
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Parm_Kennlinie_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Parm_Kennlinie_ME.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1
            b = self.modell.const_list.const_map[TKompConstants.TC_FaktorKennlinieME]
            if b != 0 and b != MU_NAN:
                return 1 / b
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_Kalibrierung_Parm_Kennlinie_ME.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        return 0  # Immer 0 laut Pascal-Code

class TK_Nichtlinearitaet_Kennlinie_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1035, const_list, "&delta;G")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_FaktorKennlinieME"]
            ]
            self.FieldsToEdit = []
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Nichtlinearitaet_Kennlinie_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Nichtlinearitaet_Kennlinie_ME.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1
            b = self.modell.const_list.const_map[TKompConstants.TC_FaktorKennlinieME]
            if b != 0 and b != MU_NAN:
                return 1 / b
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_Nichtlinearitaet_Kennlinie_ME.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        return 0  # Immer laut Delphi-Code

class TK_Zeitdrift_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1036, const_list, "&delta;(&tau;<sub>*</sub>&nu;")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_ZeitDeltaMessungEN_MO"],
                TKompConstants["TC_ZeitDrift"],
                TKompConstants["TC_FaktorKennlinieME"]
            ]
            self.FieldsToEdit = [
                "EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"
            ]
            self.Einheit = "µm/min"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Zeitdrift_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Zeitdrift_ME.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1
            b = self.modell.const_list.const_map[TKompConstants.TC_FaktorKennlinieME]
            if b != 0 and b != MU_NAN:
                return 1 / b
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_Zeitdrift_ME.sensititivty_c1] {e}")
            return MU_NAN

    def a_val(self):
        try:
            if self.archiv:
                return self.arch_data.AVal
            tau = self.modell.const_list.const_map[TKompConstants.TC_ZeitDeltaMessungEN_MO]
            gamma = self.modell.const_list.const_map[TKompConstants.TC_ZeitDrift]
            return tau * gamma
        except Exception as e:
            print(f"[Fehler in TK_Zeitdrift_ME.a_val] {e}")
            return MU_NAN


from enum import Enum, auto

MU_NAN = float('nan')

class TMU_Objekt(Enum):
    MessObjekt = auto()
    Gebrauchsnormal = auto()
    Bezugsnormal = auto()

class TMU_Geometrie(Enum):
    Geometrie_undefiniert = auto()
    Flaeche = auto()
    Kugel = auto()
    Zylinder = auto()
    HohlZylinder = auto()

class TK_Verformung_Differenz_MO_GN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1037, const_list, "")
        self.modell = modell
        self.c1_val = 1
        self.c2_val = 0
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Normal",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.ConstList = const_list
        self.archiv = False
        self.ArchData = type('ArchDataType', (object,), {"Aval": 0.0})()
        self.clear()

    def clear(self):
        self.data.Verteilung = "V_Rechteck"
        self.data.KennwertArt = "K_HalbWeite"
        self.data.Freiheitsgrad = "FG_unbegrenzt"

    def CalcDelta(self, objekt: TMU_Objekt) -> float:
        try:
            delta = 0.0
            geo_map = {
                TMU_Objekt.MessObjekt: self.modell.i_geometrie_mo,
                TMU_Objekt.Gebrauchsnormal: self.modell.i_geometrie_me,
                TMU_Objekt.Bezugsnormal: self.modell.i_geometrie_en
            }
            geo = geo_map.get(objekt, self.modell.i_geometrie_mo)
            if objekt == TMU_Objekt.MessObjekt:
                geo = self.modell.i_geometrie_mo
            if objekt == TMU_Objekt.Gebrauchsnormal:
                geo = self.modell.i_geometrie_en
            if objekt == TMU_Objekt.Bezugsnormal:
                geo = self.modell.i_geometrie_bn
            if objekt not in [TMU_Objekt.MessObjekt,TMU_Objekt.Gebrauchsnormal,TMU_Objekt.Bezugsnormal]:
                geo = self.modell.i_geometrie_mo

            geo_ME = self.modell.i_geometrie_me

            # --- FLÄCHE als ME ---
            if geo_ME in [0, 1]:
                if geo == 1:
                    delta = 0
                elif geo == 2:
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    delta = 0.415 * F**(2/3) * lx**(-1/3)
                elif geo == 3:
                    lm = MU_NAN
                    F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                    lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    D = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMessflaeche]
                    if objekt == TMU_Objekt.MessObjekt:
                        lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieMO]
                    if objekt == TMU_Objekt.Gebrauchsnormal:
                        lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieEN]
                    if objekt == TMU_Objekt.Bezugsnormal:
                        lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieEN]
                    if objekt not in [TMU_Objekt.MessObjekt,TMU_Objekt.Gebrauchsnormal,TMU_Objekt.Bezugsnormal]:
                        lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieMO]



                    lb = min(D, lm)
                    delta = 4.69e-2 * lx**(-1/3) * lb**(-1) * F
                elif geo == 4:
                    delta = 0

            # --- KUGEL als ME ---
            elif geo_ME == 2:
                F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                if geo in [1, 0]:
                    delta = 0.415 * F**(2/3) * dd**(-1/3)
                elif geo == 2:
                    lx = MU_NAN
                    if objekt == TMU_Objekt.MessObjekt:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    if objekt == TMU_Objekt.Gebrauchsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt == TMU_Objekt.Bezugsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt not in [TMU_Objekt.MessObjekt,TMU_Objekt.Gebrauchsnormal,TMU_Objekt.Bezugsnormal]:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]

                    delta = 0.415 * F**(2/3) * ((1/lx)+(1/dd))**(1/3)
                elif geo in [3, 4]:
                    lx = MU_NAN
                    if objekt == TMU_Objekt.MessObjekt:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    if objekt == TMU_Objekt.Gebrauchsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt == TMU_Objekt.Bezugsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt not in [TMU_Objekt.MessObjekt, TMU_Objekt.Gebrauchsnormal, TMU_Objekt.Bezugsnormal]:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    if geo == 3:
                        delta = 0.480 * F**(2/3) * ((1/dd)+(1/lx))**(1/4) * ((2/dd)+(1/lx))**(-1/6)
                    else:
                        delta = 0.480 * F**(2/3) * ((1/dd)-(1/lx))**(1/4) * ((2/dd)-(1/lx))**(-1/6)

            # --- ZYLINDER als ME ---
            elif geo_ME == 3:
                F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
                dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
                if geo in [1, 0]:
                    lm = self.modell.const_list.const_map[TKompConstants.TC_MantellinieME]
                    D = MU_NAN
                    if objekt == TMU_Objekt.MessObjekt:
                        D = self.modell.const_list.const_map[TKompConstants.TC_BreiteMessflaecheMO]
                    if objekt == TMU_Objekt.Gebrauchsnormal:
                        D = self.modell.const_list.const_map[TKompConstants.TC_BreiteMessflaecheEN]
                    if objekt == TMU_Objekt.Bezugsnormal:
                        D = self.modell.const_list.const_map[TKompConstants.TC_BreiteMessflaecheEN]
                    if objekt not in [TMU_Objekt.MessObjekt, TMU_Objekt.Gebrauchsnormal, TMU_Objekt.Bezugsnormal]:
                        D = self.modell.const_list.const_map[TKompConstants.TC_BreiteMessflaecheMO]
                    lb = min(D, lm)
                    delta = 4.69e-2 * F * dd**(-1/3) * lb**(-1)
                elif geo == 2:
                    lx = MU_NAN
                    if objekt == TMU_Objekt.MessObjekt:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    if objekt == TMU_Objekt.Gebrauchsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt == TMU_Objekt.Bezugsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt not in [TMU_Objekt.MessObjekt, TMU_Objekt.Gebrauchsnormal, TMU_Objekt.Bezugsnormal]:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    delta = 0.480 * F**(2/3) * ((1/lx)+(1/dd))**(1/4) * ((2/lx)+(1/dd))**(-1/6)
                elif geo in [3, 4]:
                    lx = MU_NAN
                    if objekt == TMU_Objekt.MessObjekt:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    if objekt == TMU_Objekt.Gebrauchsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt == TMU_Objekt.Bezugsnormal:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_NennmassEN]
                    if objekt not in [TMU_Objekt.MessObjekt, TMU_Objekt.Gebrauchsnormal, TMU_Objekt.Bezugsnormal]:
                        lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
                    if geo == 3:
                        delta = 0.480 * F**(2/3) * ((1/dd)+(1/lx))**(1/4) * ((2/dd)+(1/lx))**(-1/6)
                    else:
                        delta = 0.480 * F**(2/3) * ((1/dd)-(1/lx))**(1/4) * ((2/dd)-(1/lx))**(-1/6)

            return delta
        except Exception:
            return MU_NAN

    def a_val(self) -> float:
        if self.archiv:
            return self.ArchData.Aval
        else:
            return self.CalcDelta(TMU_Objekt.MessObjekt) - self.CalcDelta(TMU_Objekt.Gebrauchsnormal)

class TK_AufloesungMO(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1038, const_list, "&delta;I<sub>yMO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # keine Konstanten erforderlich
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"  # Einheit nicht explizit gesetzt, ggf. anpassen
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in AufloesungMOComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in AufloesungMOComponent.clear] {e}")

class TK_AnstellwinkelHebel(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1039, const_list, "&delta;&phi;<sub>H</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Winkelabweichung_von_90_Grad"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "°"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in AnstellwinkelHebelComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in AnstellwinkelHebelComponent.clear] {e}")

    def a_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in AnstellwinkelHebelComponent.a_val] {e}")
            return MU_NAN

    def b_val(self):
        try:
            delta_phi = self.modell.const_list.const_map[TKompConstants.TC_Winkelabweichung_von_90_Grad]
            if delta_phi == MU_NAN:
                return MU_NAN
            return 0.00015 * delta_phi ** 2
        except Exception as e:
            print(f"[Fehler in AnstellwinkelHebelComponent.b_val] {e}")
            return MU_NAN

class TK_Messkraft_3Draht_Methode(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1045, const_list, "&delta;F<sub>Dr</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_DurchmesserMesseinsatzME"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.c2_val = 0  # explizit gesetzt wie im Delphi-Code
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in Messkraft3DrahtMethodeComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in Messkraft3DrahtMethodeComponent.clear] {e}")

    def sensititivty_c1(self):
        try:
            F = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            dd = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
            if F != MU_NAN and dd != MU_NAN:
                return 0.582 * (F * dd) ** (-1 / 3)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in Messkraft3DrahtMethodeComponent.sensititivty_c1] {e}")
            return MU_NAN

class TK_KalibrierungMessdraehte(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1046, const_list, "&delta;dd<sub>k</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c1_val = 3   # wie im Pascal-Code festgelegt
            self.c2_val = 0   # wie im Pascal-Code festgelegt
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KalibrierungMessdraehteComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KalibrierungMessdraehteComponent.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in KalibrierungMessdraehteComponent.b_val] {e}")
            return MU_NAN

class TK_Zylindrizitaet_Messdraehte(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1047, const_list, "&delta;dd<sub>z</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c1_val = 3  # Festlegung wie im Original
            self.c2_val = 0
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in ZylindrizitaetMessdraehteComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in ZylindrizitaetMessdraehteComponent.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in ZylindrizitaetMessdraehteComponent.b_val] {e}")
            return MU_NAN


class TK_GewindeProfilwinkel(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1048, const_list, "&delta;&phi;<sub>G</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [TKompConstants["TC_Gewinde_Steigung"]]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in GewindeProfilwinkelComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 1  # V_Normal
            self.data.KennwertArt = 1  # K_Standardabweichung
            self.data.Freiheitsgrad = 2  # FG_unbegrenzt
        except Exception as e:
            print(f"[Fehler in GewindeProfilwinkelComponent.clear] {e}")

    def sensititivty_c1(self):
        try:
            if self.archiv:
                return self.arch_data.SensC1

            alpha_deg = 60 / 2
            alpha_rad = 2 * math.pi * (alpha_deg / 360)

            p = self.modell.const_list.const_map[TKompConstants.TC_Gewinde_Steigung]
            d = zeiss_reihe_d(p) if isinstance(p,(int, float)) else MU_NAN

            if all(isinstance(val,(int, float)) for val in [alpha_rad, p, d]):
                cos_a = math.cos(alpha_rad)
                sin_a = math.sin(alpha_rad)
                return 1000 * (d - (p / (2 * cos_a))) * (cos_a / (sin_a ** 2))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in GewindeProfilwinkelComponent.sensititivty_c1] {e}")
            return MU_NAN

    def a_val(self):
        try:
            p = self.modell.const_list.const_map[TKompConstants.TC_Gewinde_Steigung]
            if isinstance(p,(float, int)):
                return 0.003 * math.pow(p, -0.75)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in GewindeProfilwinkelComponent.a_val] {e}")
            return MU_NAN

    def b_val(self):
        return 0

class TK_Messkraft_2Kugel_Methode(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1049, const_list, "δF<sub>Kug</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_MesskraftME"],
                TKompConstants["TC_DurchmesserMesseinsatzME"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteMesskraft2KugelMethode.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KomponenteMesskraft2KugelMethode.clear] {e}")

    def sensititivty_c1(self):
        try:
            f = self.modell.const_list.const_map[TKompConstants.TC_MesskraftME]
            dk = self.modell.const_list.const_map[TKompConstants.TC_DurchmesserMesseinsatzME]
            if f != MU_NAN and dk != MU_NAN:
                return 1.0115 * (f * dk) ** (-1 / 3)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteMesskraft2KugelMethode.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        return 0

class TK_KalibrierungMesskugeln(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1050, const_list, "δd<sub>K</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteKalibrierungMesskugeln.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KomponenteKalibrierungMesskugeln.clear] {e}")

    def b_val(self):
        return 0


class TK_RundheitMesskugeln(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1051, const_list, "δR<sub>Kug</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c2_val = 0
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteRundheitMesskugeln.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KomponenteRundheitMesskugeln.clear] {e}")

    def b_val(self):
        return 0

class TK_Geradheit_stehender_Schenkel_EN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1052, const_list, "&delta;G<sub>EN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.einheit = "mm"

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Schrittweite_Geradheitskalibrierung_EN"],   # 2043
                TKompConstants["TC_Positionsgenauigkeit_Kalibrierung_MO"]     # 2044
                # "TC_Betrag_max_Abweichung_Bezugsgerade"     # 2045 (nicht verwendet laut Doku)
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ KomponenteGeradheitStehenderSchenkelEN] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear KomponenteGeradheitStehenderSchenkelEN] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            dz = self.modell.const_list.const_map[TKompConstants.TC_Positionsgenauigkeit_Kalibrierung_MO]
            deltaz = self.modell.const_list.const_map[TKompConstants.TC_Schrittweite_Geradheitskalibrierung_EN]
            if isinstance(dz, (float, int)) and isinstance(deltaz, (float, int)) and deltaz != 0:
                return dz / deltaz
            return MU_NAN
        except Exception as e:
            print(f"[Fehler in sensititivty_c1 KomponenteGeradheitStehenderSchenkelEN] {e}")
            return MU_NAN


class TK_Geradheit_stehender_Schenkel_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1053, const_list, "&delta;G<sub>MO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Schrittweite_Geradheitskalibrierung_MO"],  # 2059
                TKompConstants["TC_Positionsgenauigkeit_Kalibrierung_MO"],   # 2044
                # TKompConstants["TC_Betrag_max_Abweichung_Bezugsgerade"]     # 2045 (auskommentiert)
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Geradheit_stehender_Schenkel_MO] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Geradheit_stehender_Schenkel_MO] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            dz = self.modell.const_list.const_map[TKompConstants.TC_Positionsgenauigkeit_Kalibrierung_MO]
            deltaz = self.modell.const_list.const_map[TKompConstants.TC_Schrittweite_Geradheitskalibrierung_MO]
            if isinstance(dz, (float, int)) and isinstance(deltaz, (float, int)) and deltaz != 0:
                return dz / deltaz
            return MU_NAN
        except Exception as e:
            print(f"[Fehler in sensititivty_c1 TK_Geradheit_stehender_Schenkel_MO] {e}")
            return MU_NAN

class TK_Geradheit_liegender_Schenkel_EN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1054, const_list, "&delta;g<sub>EN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Laenge_stehender_Schenkel_EN"],         # 2046
                TKompConstants["TC_Abstand_Stuetzpunkte_EN"],              # 2047
                TKompConstants["TC_Geradheit_Messplatte_EN"],              # 2048
                TKompConstants["TC_Positionsabweichung_Stuetzpunkte_EN"],  # 2049
                TKompConstants["TC_Kalibrierung_Geradheit_EN"],            # 2050
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Geradheit_liegender_Schenkel_EN] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Geradheit_liegender_Schenkel_EN] {e}")

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0
            else:
                const_map = self.modell.const_list.const_map
                L1EN = const_map.get(TKompConstants.TC_Laenge_stehender_Schenkel_EN)
                AN = const_map.get(TKompConstants.TC_Abstand_Stuetzpunkte_EN)
                GEN = const_map.get(TKompConstants.TC_Geradheit_Messplatte_EN)
                DeltaAgEN = const_map.get(TKompConstants.TC_Positionsabweichung_Stuetzpunkte_EN)
                UGEN = const_map.get(TKompConstants.TC_Kalibrierung_Geradheit_EN)

                if all(isinstance(v, (float, int)) for v in [L1EN, AN, GEN, DeltaAgEN, UGEN]) and AN != 0:
                    a = L1EN / AN
                    b = (GEN ** 2) / 3
                    c = (1 / 4) + (DeltaAgEN / AN) ** 2
                    d = (UGEN ** 2) / 4
                    return a * math.sqrt(b * c + d)
                else:
                    return MU_NAN
        except Exception as e:
            print(f"[Fehler in unsicherheitsbeitrag_l0 TK_Geradheit_liegender_Schenkel_EN] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l1(self):
        return 0

class TK_Geradheit_liegender_Schenkel_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1055, const_list, "&delta;g<sub>MO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Laenge_stehender_Schenkel_MO"],         # 2051
                TKompConstants["TC_Stuetzpunktabstand_MO"],                # 2052
                TKompConstants["TC_Geradheit_Messplatte_MO"],              # 2053
                TKompConstants["TC_Positionsabweichung_Stuetzpunkte_MO"],  # 2054
                TKompConstants["TC_Kalibrierung_Geradheit_MO"],            # 2055
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Geradheit_liegender_Schenkel_MO] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Geradheit_liegender_Schenkel_MO] {e}")

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0
            else:
                const_map = self.modell.const_list.const_map
                L1MO = const_map.get(TKompConstants.TC_Laenge_stehender_Schenkel_MO)
                AMO = const_map.get(TKompConstants.TC_Stuetzpunktabstand_MO)
                GMO = const_map.get(TKompConstants.TC_Geradheit_Messplatte_MO)
                DeltaAgMO = const_map.get(TKompConstants.TC_Positionsabweichung_Stuetzpunkte_MO)
                UGMO = const_map.get(TKompConstants.TC_Kalibrierung_Geradheit_MO)

                if all(isinstance(v, (float, int)) for v in [L1MO, AMO, GMO, DeltaAgMO, UGMO]) and AMO != 0:
                    a = L1MO / AMO
                    b = (GMO ** 2) / 3
                    c = (1 / 4) + (DeltaAgMO / AMO) ** 2
                    d = (UGMO ** 2) / 4
                    return a * math.sqrt(b * c + d)
                else:
                    return MU_NAN
        except Exception as e:
            print(f"[Fehler in unsicherheitsbeitrag_l0 TK_Geradheit_liegender_Schenkel_MO] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l1(self):
        return 0


class TK_Neigung_Winkelnormal_EN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1056, const_list, "&delta;E<sub>EN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Laenge_stehender_Schenkel_EN"],          # 2046
                TKompConstants["TC_Abstand_Stuetzpunkte_EN"],               # 2047
                TKompConstants["TC_Geradheit_Messplatte_EN"],               # 2048
                TKompConstants["TC_Positionsabweichung_Stuetzpunkte_EN"],   # 2049
                TKompConstants["TC_Kalibrierung_Ebenheit_Messplatte"],      # 2056
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Neigung_Winkelnormal_EN] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Neigung_Winkelnormal_EN] {e}")

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0
            else:
                const_map = self.modell.const_list.const_map
                L1EN = const_map.get(TKompConstants.TC_Laenge_stehender_Schenkel_EN)
                AEN = const_map.get(TKompConstants.TC_Abstand_Stuetzpunkte_EN)
                EEN = const_map.get(TKompConstants.TC_Geradheit_Messplatte_EN)
                DeltaAgEN = const_map.get(TKompConstants.TC_Positionsabweichung_Stuetzpunkte_EN)
                UE = const_map.get(TKompConstants.TC_Kalibrierung_Ebenheit_Messplatte)

                if all(isinstance(v, (float, int)) for v in [L1EN, AEN, EEN, DeltaAgEN, UE]) and AEN != 0:
                    a = L1EN / AEN
                    b = (EEN ** 2) / 3
                    c = 0.25 + (DeltaAgEN / AEN) ** 2
                    d = (UE ** 2) / 4
                    return a * math.sqrt(b * c + d)
                else:
                    return MU_NAN
        except Exception as e:
            print(f"[Fehler in unsicherheitsbeitrag_l0 TK_Neigung_Winkelnormal_EN] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l1(self):
        return 0

class TK_Neigung_Messobjekts_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1057, const_list, "&delta;G<sub>MO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Laenge_stehender_Schenkel_MO"],         # 2051
                TKompConstants["TC_Stuetzpunktabstand_MO"],                # 2052
                TKompConstants["TC_Geradheit_Messplatte_MO"],              # 2053
                TKompConstants["TC_Kalibrierung_Ebenheit_Messplatte"],     # 2056
                TKompConstants["TC_Positionsgenauigkeit_Stuetzpunkte"],    # 2058
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Neigung_Messobjekts_MO] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Neigung_Messobjekts_MO] {e}")

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0
            else:
                const_map = self.modell.const_list.const_map

                L1mo = const_map.get(TKompConstants.TC_Laenge_stehender_Schenkel_MO)
                Amo = const_map.get(TKompConstants.TC_Stuetzpunktabstand_MO)
                Gmo = const_map.get(TKompConstants.TC_Geradheit_Messplatte_MO)
                Ue = const_map.get(TKompConstants.TC_Kalibrierung_Ebenheit_Messplatte)
                DeltaAmo = const_map.get(TKompConstants.TC_Positionsgenauigkeit_Stuetzpunkte)

                if all(isinstance(v, (float, int)) for v in [L1mo, Amo, Gmo, DeltaAmo, Ue]) and Amo != 0:
                    a = L1mo / Amo
                    b = (Gmo ** 2) / 3
                    c = 0.25 + (DeltaAmo / Amo) ** 2
                    d = (Ue ** 2) / 4
                    return a * math.sqrt(b * c + d)
                else:
                    return MU_NAN
        except Exception as e:
            print(f"[Fehler in unsicherheitsbeitrag_l0 TK_Neigung_Messobjekts_MO] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l1(self):
        return 0

class TK_Kalibrierung_Geradheit_stehender_Schenkel_EN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1059, const_list, "&delta;G<sub>ENK</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Schrittweite_Geradheitskalibrierung_EN"],   # 2043
                TKompConstants["TC_Positionsgenauigkeit_Kalibrierung_MO"],     # 2044
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Kalibrierung_Geradheit_stehender_Schenkel_EN] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Kalibrierung_Geradheit_stehender_Schenkel_EN] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            const_map = self.modell.const_list.const_map
            DeltaZ = const_map.get(TKompConstants.TC_Schrittweite_Geradheitskalibrierung_EN)
            dz     = const_map.get(TKompConstants.TC_Positionsgenauigkeit_Kalibrierung_MO)

            if all(isinstance(v, (float, int)) for v in [DeltaZ, dz]) and DeltaZ != 0:
                return dz / (math.sqrt(3) * DeltaZ)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in sensititivty_c1 TK_Kalibrierung_Geradheit_stehender_Schenkel_EN] {e}")
            return MU_NAN

class TK_Kalibrierung_Geradheit_stehender_Schenkel_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1060, const_list, "&delta;G<sub>MOK</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.ConstNeeded += [
                TKompConstants["TC_Positionsgenauigkeit_Kalibrierung_MO"],     # 2044
                TKompConstants["TC_Schrittweite_Geradheitskalibrierung_MO"],   # 2059
            ]

            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in __init__ TK_Kalibrierung_Geradheit_stehender_Schenkel_MO] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Kalibrierung_Geradheit_stehender_Schenkel_MO] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            const_map = self.modell.const_list.const_map
            DeltaZ = const_map.get(TKompConstants.TC_Schrittweite_Geradheitskalibrierung_MO)  # 2059
            dz     = const_map.get(TKompConstants.TC_Positionsgenauigkeit_Kalibrierung_MO)    # 2044

            if all(isinstance(v, (float, int)) for v in [DeltaZ, dz]) and DeltaZ != 0:
                return dz / (math.sqrt(3) * DeltaZ)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in sensititivty_c1 TK_Kalibrierung_Geradheit_stehender_Schenkel_MO] {e}")
            return MU_NAN

class TK_Kalibrierung_Geradheit_Hoehenmessgeraets(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1061, const_list, "&delta;G<sub>NK</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Kalibrierung_Geradheit_Hoehenmessgeraets] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Normal"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Kalibrierung_Geradheit_Hoehenmessgeraets] {e}")

    def b_val(self):
        return 0

class TK_Geradheitabweichung_Hoehenmessgeraets(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1062, const_list, "&delta;G<sub>N</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Geradheitabweichung_Hoehenmessgeraets] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Spannweite"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Geradheitabweichung_Hoehenmessgeraets] {e}")

    def b_val(self):
        return 0

class TK_Geradheit_Schenkelinnenseite(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1066, const_list, "&delta;G<sub>Schenk</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Geradheit_Schenkelinnenseite] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Spannweite"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Geradheit_Schenkelinnenseite] {e}")

    def b_val(self):
        return 0


class TK_Kalibrierung_Geradheit_Schenkelinnenseite(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1067, const_list, "&delta;G<sub>Schenk.K</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Kalibrierung_Geradheit_Schenkelinnenseite] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Spannweite"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Kalibrierung_Geradheit_Schenkelinnenseite] {e}")

    def b_val(self):
        return 0

class TK_Strichbreite_EN(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1071, const_list, "&delta;l<sub>yEN</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.Einheit = "mm"

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Strichbreite_EN] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Strichbreite_EN] {e}")

    def sensititivty_c1(self):
        return 1000

    def b_val(self):
        return 0


class TK_Strichbreite_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1072, const_list, "&delta;l<sub>yMO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.Einheit = "mm"

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Strichbreite_MO] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Strichbreite_MO] {e}")

    def sensititivty_c1(self):
        return 1000

    def b_val(self):
        return 0

class TK_Strichbreite_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1073, const_list, "&delta;l<sub>yME</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.Einheit = "mm"

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )

            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]
        except Exception as e:
            print(f"[Fehler in __init__ TK_Strichbreite_ME] {e}")

    def clear(self):
        try:
            super().clear()
            with self.data:
                self.Verteilung = "V_Rechteck"
                self.KennwertArt = "K_Standardabweichung"
                self.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in clear TK_Strichbreite_ME] {e}")

    def sensititivty_c1(self):
        return 1000

    def b_val(self):
        return 0


class TK_Winkel_Achsen_MO_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1074, const_list, "&delta;&phi;")
            self.const_list = const_list
            self.lfdnr = lfdnr
            self.ConstNeeded += [
                TKompConstants["TC_Anzahl_Verschiebungen_MO"],            # 2065
                TKompConstants["TC_Messbereichsendwert_Messeinrichtung"], # 2066
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "°"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in TK_Winkel_Achsen_MO_ME.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in TK_Winkel_Achsen_MO_ME.clear] {e}")

    def a_val(self):
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                # TermL0 in Grad, umwandeln in Bogenmaß und quadrieren
                rad = self.data.TermL0 * (math.pi / 180)
                return rad * rad
        except Exception as e:
            print(f"[Fehler in TK_Winkel_Achsen_MO_ME.a_val] {e}")
            return MU_NAN

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            m = self.modell.const_list.const_map[TKompConstants.TC_Anzahl_Verschiebungen_MO]          # 2065
            lyMEmax = self.modell.const_list.const_map[TKompConstants.TC_Messbereichsendwert_Messeinrichtung] # 2066
            lx = self.modell.const_list.const_map[TKompConstants.TC_Messwert]                          # 2006
            if all(val != MU_NAN for val in [m, lyMEmax, lx]):
                # (1000/2) statt 0.5 wegen Eingabung b in mm
                return (1000 / 2) * (lx - (m * lyMEmax))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_Winkel_Achsen_MO_ME.SensititvityC1] {e}")
            return MU_NAN

class TK_Anzahl_Verschiebungen_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1075, const_list, "ΔL_Schieb")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.ConstNeeded += [
                TKompConstants["TC_Messbereichsendwert_Messeinrichtung"],  # 2066
            ]
            self.KompsNeeded += [
                "Komp_KalibrierungME",             # 1001
                "Komp_ErmittelteMessabweichungME", # 1002
                "Komp_AufloesungME",               # 1003
                "Komp_Wiederholpraezision",        # 1040
                "Komp_Strichbreite_MO",            # 1072
                "Komp_Strichbreite_ME",            # 1073
                "Komp_Winkel_Achsen_MO_ME"         # 1074
            ]
            self.FieldsToEdit = [
                "EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"
            ]
            self.Einheit = "°"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in AnzahlVerschiebungenMO.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in AnzahlVerschiebungenMO.clear] {e}")

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            m = self.modell.const_list.const_map[TKompConstants.TC_Anzahl_Verschiebungen_MO]  # 2065

            VImek = MU_NAN
            VImeka = MU_NAN
            VImeanz = MU_NAN
            VW = MU_NAN
            VImestr = MU_NAN
            VImostr = MU_NAN
            Vphi = MU_NAN

            for komp in self.modell:
                klassname = komp.__class__.__name__
                if klassname == "TK_KalibrierungME":
                    VImek = komp.varianz()
                elif klassname == "TK_ErmittelteMessabweichungME":
                    VImeka = komp.varianz()
                elif klassname == "TK_AufloesungME":
                    VImeanz = komp.varianz()
                elif klassname == "TK_Wiederholpraezision":
                    VW = komp.varianz()
                elif klassname == "TK_Strichbreite_MO":
                    VImestr = komp.varianz()
                elif klassname == "TK_Strichbreite_ME":
                    VImostr = komp.varianz()
                elif klassname == "TK_Winkel_Achsen_MO_ME":
                    Vphi = komp.varianz()

            values = [VImek, VImeka, VImeanz, VW, VImestr, VImostr, Vphi, m]
            if all(val == val and val is not None for val in values):  # val == val ist True, wenn val != NaN
                return math.sqrt(m) * math.sqrt(sum(values[:-1]))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in AnzahlVerschiebungenMO.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l1(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in AnzahlVerschiebungenMO.unsicherheitsbeitrag_l1] {e}")
            return MU_NAN

class TK_Kalibrierung_Rechwinkligkeit(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1076, const_list, "Δl_RNK")
            self.lfdnr = lfdnr
            self.ConstNeeded += [TKompConstants["TC_Hoehe_zu_Rechtwinkligkeit"]]
            self.ConstNeeded = [c for c in self.ConstNeeded if c != TKompConstants["TC_Messwert"]]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KalibrierungRechwinkligkeit.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KalibrierungRechwinkligkeit.clear] {e}")

    def unsicherheitsbeitrag_l1(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL1
            su = self.std_unsicherheit(self.b_val())
            c2 = self.sensititivty_c2()
            l = self.modell.const_list.const_map[TKompConstants.TC_Hoehe_zu_Rechtwinkligkeit] * 1000  # µm

            if all(x == x and x is not None for x in [su, c2, l]):  # kein NaN
                return su * c2 * l
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KalibrierungRechwinkligkeit.unsicherheitsbeitrag_l1] {e}")
            return MU_NAN

class TK_Ermittelte_Rechwinkligkeit(TMU_Komponente):
    def __init__(self, modell, const_list):
        try:
            super().__init__(modell, 1077, const_list, "Δl_RN")
            self.ConstNeeded += [TKompConstants["TC_Hoehe_zu_Rechtwinkligkeit"]]
            self.ConstNeeded = [c for c in self.ConstNeeded if c != TKompConstants["TC_Messwert"]]
        except Exception as e:
            print(f"[Fehler in ErmittelteRechwinkligkeit.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in ErmittelteRechwinkligkeit.clear] {e}")

    def unsicherheitsbeitrag_l1(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL1
            su = self.std_unsicherheit(self.b_val())
            c2 = self.sensititivty_c2()
            l = self.modell.const_list.const_map[TKompConstants.TC_Hoehe_zu_Rechtwinkligkeit] * 1000  # µm

            if all(x == x and x is not None for x in [su, c2, l]):  # Prüfe kein NaN
                return su * c2 * l
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in ErmittelteRechwinkligkeit.unsicherheitsbeitrag_l1] {e}")
            return MU_NAN


class TK_Rh_Kalibrierung_Einstellnormal_EN(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1078, const_list, "&delta;(Pt<sub>n</sub>)")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],  # 2068
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],               # 2069
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhKalibrierungEinstellnormalEN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhKalibrierungEinstellnormalEN.clear] {e}")

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            if all(val != MU_NAN for val in [n, m]) and m != 0:
                return n / m
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhKalibrierungEinstellnormalEN.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        return 0

class TK_Rh_Drift_Richtiger_Wert_vom_EN(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1079, const_list, "&delta;D<sub>Ptn</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],  # 2068
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],              # 2069
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhDriftRichtigerWertVomEN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhDriftRichtigerWertVomEN.clear] {e}")

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            if all(val != MU_NAN for val in [n, m]) and m != 0:
                return n / m
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhDriftRichtigerWertVomEN.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        return 0


class TK_Rh_Unterschied_Kalibrierort_EN(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1080, const_list, "&delta;(&Delta;Pt)")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],   # 2068
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],               # 2069
                TKompConstants["TC_Rh_Ortabhaengige_Unsicherheit_in_y"],       # 2070
                TKompConstants["TC_Rh_Gradient_in_Rillenrichtung"],            # 2071
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhUnterschiedKalibrierortEN.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhUnterschiedKalibrierortEN.clear] {e}")

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            if all(val != MU_NAN for val in [n, m]) and m != 0:
                return n / m
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhUnterschiedKalibrierortEN.sensititivty_c1] {e}")
            return MU_NAN

    def a_val(self):
        try:
            ay = self.modell.const_list.const_map[TKompConstants.TC_Rh_Ortabhaengige_Unsicherheit_in_y]
            G = self.modell.const_list.const_map[TKompConstants.TC_Rh_Gradient_in_Rillenrichtung]
            if all(val != MU_NAN for val in [ay, G]):
                return ay * G
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhUnterschiedKalibrierortEN.a_val] {e}")
            return MU_NAN

    def b_val(self):
        return 0


class TK_Rh_Wiederholpraezision_Antastung_MO(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1081, const_list, "&delta;(MW(Pt<sub>m</sub>))")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],  # 2068
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],               # 2069
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhWiederholpraezisionAntastungMO.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhWiederholpraezisionAntastungMO.clear] {e}")

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            if all(val != MU_NAN for val in [n, m]) and m != 0:
                return math.sqrt(m * n) / (m ** 2)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhWiederholpraezisionAntastungMO.sensititivty_c1] {e}")
            return MU_NAN

    def b_val(self):
        return 0


class TK_Rh_Topografie_MO(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1082, const_list, "Δ(MW(Rz))")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],  # 2068
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],               # 2069
                TKompConstants["TC_Rh_Messpunktabstand"],                      # 2072
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],                 # 2073
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhTopografieMO.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhTopografieMO.clear] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]

            if any(val == MU_NAN for val in [n, m, delta_x, lambda_s]) or n == 0 or lambda_s == 0:
                return MU_NAN

            return (math.sqrt(m * n) / (n ** 2)) * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhTopografieMO.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Fuehrungsabweichung(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1083, const_list, "&delta;Wt<sub>0</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhFuehrungsabweichungKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhFuehrungsabweichungKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhFuehrungsabweichungKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s]) or m == 0 or lambda_s == 0:
                return MU_NAN

            return (n / m) * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhFuehrungsabweichungKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Drift_Fuehrungsabweichung(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1084, const_list, "&delta;D<sub>Wt0</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhDriftFuehrungsabweichungKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhDriftFuehrungsabweichungKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhDriftFuehrungsabweichungKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s]) or m == 0 or lambda_s == 0:
                return MU_NAN

            return (n / m) * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhDriftFuehrungsabweichungKomponente.sensititivty_c1] {e}")
            return MU_NAN



class TK_Rh_Grundrauschen(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1085, const_list, "&delta;(MW(Rz<sub>0</sub>))")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhGrundrauschenKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhGrundrauschenKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhGrundrauschenKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s]) or n == 0 or lambda_s == 0:
                return MU_NAN

            return (m / n) * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhGrundrauschenKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Drift_Grundrauschen(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1086, const_list, "&delta;D<sub>MWRz0</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhDriftGrundrauschenKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhDriftGrundrauschenKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhDriftGrundrauschenKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s]) or n == 0 or lambda_s == 0:
                return MU_NAN

            return (m / n) * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhDriftGrundrauschenKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Verformung_MO(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1087, const_list, "&delta;a<sub>pl</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhVerformungMoKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhVerformungMoKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhVerformungMoKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s]) or m == 0 or lambda_s == 0:
                return MU_NAN

            return (n / m) * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhVerformungMoKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Abweichung_Tastspitzenradius_vom_Nennwert(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1088, const_list, "&delta;r<sub>KA</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
                TKompConstants["TC_Rh_Kennwertaenderungsfaktor"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhAbweichungTastspitzenradiusVomNennwertKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhAbweichungTastspitzenradiusVomNennwertKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhAbweichungTastspitzenradiusVomNennwertKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]
            v = self.modell.const_list.const_map[TKompConstants.TC_Rh_Kennwertaenderungsfaktor]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s, v]) or n == 0 or lambda_s == 0:
                return MU_NAN

            return (m / n) * v * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhAbweichungTastspitzenradiusVomNennwertKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Messunsicherheit_Kalibrierung_Tastspitzenradius(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1089, const_list, "&delta;r<sub>K</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke"],
                TKompConstants["TC_Rh_Anzahl_Teilmessstrecken"],
                TKompConstants["TC_Rh_Messpunktabstand"],
                TKompConstants["TC_Rh_Tiefpasswellenlaengen"],
                TKompConstants["TC_Rh_Kennwertaenderungsfaktor"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhMessunsicherheitKalibrierungTastspitzenradiusKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhMessunsicherheitKalibrierungTastspitzenradiusKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhMessunsicherheitKalibrierungTastspitzenradiusKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke]
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Teilmessstrecken]
            delta_x = self.modell.const_list.const_map[TKompConstants.TC_Rh_Messpunktabstand]
            lambda_s = self.modell.const_list.const_map[TKompConstants.TC_Rh_Tiefpasswellenlaengen]
            v = self.modell.const_list.const_map[TKompConstants.TC_Rh_Kennwertaenderungsfaktor]

            if any(x == MU_NAN for x in [n, m, delta_x, lambda_s, v]) or n == 0 or lambda_s == 0:
                return MU_NAN

            return (m / n) * v * 1.227 * math.sqrt(delta_x / lambda_s)
        except Exception as e:
            print(f"[Fehler in RhMessunsicherheitKalibrierungTastspitzenradiusKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Unbekannte_systematische_Abweichung(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1090, const_list, "&delta;R<sub>u</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Gemessene_Kenngroesse"],  # 2075
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "%"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhUnbekannteSystematischeAbweichungKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhUnbekannteSystematischeAbweichungKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhUnbekannteSystematischeAbweichungKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            rz = self.modell.const_list.const_map[TKompConstants.TC_Rh_Gemessene_Kenngroesse]
            if rz != MU_NAN:
                return rz / 100
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhUnbekannteSystematischeAbweichungKomponente.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Kalibrierung_Einstellnormal_EN_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1091, const_list, "&delta;(Pt<sub>ENK</sub>)")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten notwendig
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhKalibrierungEinstellnormalENTGKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhKalibrierungEinstellnormalENTGKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhKalibrierungEinstellnormalENTGKomponente.b_val] {e}")
            return MU_NAN


class TK_Rh_Drift_Richtiger_Wert_von_EN_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1092, const_list, "&delta;D<sub>Ptn</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten benötigt
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhDriftRichtigerWertVonENTGKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhDriftRichtigerWertVonENTGKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhDriftRichtigerWertVonENTGKomponente.b_val] {e}")
            return MU_NAN



class TK_Rh_Kalibrierort_Kalibrierung_EN_TG(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1093, const_list, "&delta;(Pt<sub>ENT</sub>)")
            self.const_list = const_list
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [TKompConstants["TC_Rh_Anzahl_Wiederholungsmessungen_geaenderter_Antastort"]]  # 2076
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhKalibrierortKalibrierungENTGKomponente.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhKalibrierortKalibrierungENTGKomponente.clear] {e}")

    def b_val(self):
        try:
            return 0
        except Exception as e:
            print(f"[Fehler in RhKalibrierortKalibrierungENTGKomponente.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        try:
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Wiederholungsmessungen_geaenderter_Antastort]  # 2076
            if m != MU_NAN and m > 0:
                return 1 / math.sqrt(m)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhKalibrierortKalibrierungENTGKomponente.SensititvityC1] {e}")
            return MU_NAN


class TK_Rh_Wiederholpraezision_Antastung_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1094, const_list, "&delta;W<sub>MO</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Rh_Anzahl_Wiederholmessungen_selber_Antastort"],  # 2077
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhWiederholpraezisionAntastungTG.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhWiederholpraezisionAntastungTG.clear] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        try:
            m = self.modell.const_list.const_map[TKompConstants.TC_Rh_Anzahl_Wiederholmessungen_selber_Antastort]
            if m != MU_NAN and m > 0:
                return 1 / math.sqrt(m)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in RhWiederholpraezisionAntastungTG.sensititivty_c1] {e}")
            return MU_NAN


class TK_Rh_Fuehrungsabweichung_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1095, const_list, "&delta;Wt<sub>0</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten nötig
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhFuehrungsabweichungTG.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhFuehrungsabweichungTG.clear] {e}")

    def b_val(self):
        return 0

class TK_Rh_Grundrauschen_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1096, const_list, "&delta;(MW(Rz<sub>0</sub>))")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten notwendig
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhGrundrauschenTG.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhGrundrauschenTG.clear] {e}")

    def b_val(self):
        return 0

class TK_Rh_Verformung_EN_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1097, const_list, "&delta;a<sub>pl</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten benötigt
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhVerformungENTG.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhVerformungENTG.clear] {e}")

    def b_val(self):
        return 0

class TK_Rh_Abweichung_Tastspitzenradius_Nennwert(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1098, const_list, "&delta;r<sub>KA</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten notwendig
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhAbweichungTastspitzenradiusNennwert.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhAbweichungTastspitzenradiusNennwert.clear] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        return 0.02


class TK_Rh_Messunsicherheit_Kalibrierung_Tastspitzenradius_TG(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1099, const_list, "&delta;r<sub>K</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += []  # Keine Konstanten notwendig
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in RhMessunsicherheitKalibrierungTastspitzenradiusTG.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in RhMessunsicherheitKalibrierungTastspitzenradiusTG.clear] {e}")

    def b_val(self):
        return 0

    def sensititivty_c1(self):
        return 0.02


class TK_fm_FormNormal(TMU_Komponente):  # Basiskomponente für Formnormalkomponenten

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def b_val(self):
        return 0  # Für fast alle Form-Komponenten gilt b=0



class TK_Fm_Streuung_Anzeige_ME_in_jedem_Profilpunkt(TK_fm_FormNormal):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1100, const_list, "&delta;&Delta;Ry")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Anzahl_Wiederholmessungen_StreuungAnzeige"]
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in FmStreuungAnzeigeMEInJedemProfilpunkt.__init__] {e}")

    def sensititivty_c1(self):
        try:
            n = self.modell.const_list.const_map[TKompConstants.TC_Fm_Anzahl_Wiederholmessungen_StreuungAnzeige]
            if n != MU_NAN and n > 0:
                return 1 / math.sqrt(n)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in FmStreuungAnzeigeMEInJedemProfilpunkt.sensititivty_c1] {e}")
            return MU_NAN


class TK_Fm_Homogenitaet_MO(TK_fm_FormNormal):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1101, const_list, "&delta;F<sub>H</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten"],
                TKompConstants["TC_Fm_Grenzwellenlaenge"]
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in FmHomogenitaetMO.__init__] {e}")

    def sensititivty_c1(self):
        try:
            deltax = self.modell.const_list.const_map[TKompConstants.TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten]
            lambdac = self.modell.const_list.const_map[TKompConstants.TC_Fm_Grenzwellenlaenge]
            if deltax != MU_NAN and lambdac != MU_NAN and lambdac > 0:
                return 1.227 * math.sqrt(deltax / lambdac)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in FmHomogenitaetMO.sensititivty_c1] {e}")
            return MU_NAN

class TK_Fm_Reinigung_MO(TK_fm_FormNormal):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1102, const_list, "&delta;V<sub>R</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten"],
                TKompConstants["TC_Fm_Grenzwellenlaenge"]
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in FmReinigungMO.__init__] {e}")

    def sensititivty_c1(self):
        try:
            deltax = self.modell.const_list.const_map[TKompConstants.TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten]
            lambdac = self.modell.const_list.const_map[TKompConstants.TC_Fm_Grenzwellenlaenge]
            if deltax != MU_NAN and lambdac != MU_NAN and lambdac > 0:
                return 1.227 * math.sqrt(deltax / lambdac)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in FmReinigungMO.sensititivty_c1] {e}")
            return MU_NAN


class TK_Fm_Dynamische_Eingenschaften_ME(TK_fm_FormNormal):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1103, const_list, "&delta;D<sub>E</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten"],
                TKompConstants["TC_Fm_Grenzwellenlaenge"]
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in FmDynamischeEigenschaftenME.__init__] {e}")

    def sensititivty_c1(self):
        try:
            deltax = self.modell.const_list.const_map[TKompConstants.TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten]
            lambdac = self.modell.const_list.const_map[TKompConstants.TC_Fm_Grenzwellenlaenge]
            if deltax != MU_NAN and lambdac != MU_NAN and lambdac > 0:
                return 1.227 * math.sqrt(deltax / lambdac)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in FmDynamischeEigenschaftenME.sensititivty_c1] {e}")
            return MU_NAN


class TK_Fm_Rauschen_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1104, const_list, "&delta;R<sub>A;S</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten"],
                TKompConstants["TC_Fm_Grenzwellenlaenge"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "N"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteRauschenME.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def sensititivty_c1(self):
        try:
            delta_x = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten
            ]
            lambda_c = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Grenzwellenlaenge
            ]
            if (
                delta_x != MU_NAN
                and lambda_c != MU_NAN
                and lambda_c > 0
            ):
                return 1.227 * math.sqrt(delta_x / lambda_c)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteRauschenME.sensititivty_c1] {e}")
            return MU_NAN



class TK_Fm_Streuung_Empfindlichkeit_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1105, const_list, "&delta;A")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten"],
                TKompConstants["TC_Fm_Grenzwellenlaenge"],
                TKompConstants["TC_Fm_Messwert_MO"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteStreuungEmpfindlichkeitME.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def sensititivty_c1(self):
        try:
            delta_x = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten
            ]
            lambda_c = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Grenzwellenlaenge
            ]
            msw_mo = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Messwert_MO
            ]
            if (
                delta_x != MU_NAN
                and lambda_c != MU_NAN
                and lambda_c > 0
            ):
                return 1.227 * msw_mo * math.sqrt(delta_x / lambda_c)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteStreuungEmpfindlichkeitME.sensititivty_c1] {e}")
            return MU_NAN


class TK_Fm_Unsicherheit_Vergroesserungsnormal(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1106, const_list, "&delta;F<sub>lick</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteUnsicherheitVergroesserungsnormal.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_Fm_Streuung_Spindel_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1107, const_list, "&delta;S<sub>pindel</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Richtiger_Wert_Rundheit_Kugelnormal"],
                TKompConstants["TC_Fm_Messunsicherheit_der_Kalibrierung_Kugelnormal"],
                TKompConstants["TC_Fm_Gemessene_Rundheit_EN"],
            ]
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteStreuungSpindelME.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            delta_rn = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Richtiger_Wert_Rundheit_Kugelnormal
            ]
            u_en = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Messunsicherheit_der_Kalibrierung_Kugelnormal
            ]
            delta_ryen = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Gemessene_Rundheit_EN
            ]

            if all(x != MU_NAN for x in [delta_rn, u_en, delta_ryen]):
                term = abs(delta_ryen**2 - delta_rn**2) / 3 + u_en**2
                return 0.5 * math.sqrt(term) * self.sensititivty_c1()
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteStreuungSpindelME.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_Fm_Linearitaet_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1108, const_list, "&delta;Lin")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteLinearitaetME.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_Fm_Hysterese_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1109, const_list, "&delta;H")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteHystereseME.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_Fm_Exzentrizitaet_MO_Aus(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1110, const_list, "&delta;E<sub>Aus</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Gemessenden_Exzentrizitaet"],
                TKompConstants["TC_Fm_Aussendurchmesser_MO"],
                TKompConstants["TC_Fm_Tastkugeldurchmesser"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "mm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteExzentrizitaetMOAus.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVAL
            else:
                return self.data.TermL1
        except Exception as e:
            print(f"[Fehler in KomponenteExzentrizitaetMOAus.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        # Wenn es später benötigt wird – momentan nicht im Delphi-Code enthalten
        return 1.0

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            eta = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Gemessenden_Exzentrizitaet
            ]
            d_aus = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Aussendurchmesser_MO
            ]
            d = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Tastkugeldurchmesser]

            if all(x != MU_NAN for x in [eta, d_aus, d]) and (d_aus + d) != 0:
                return (1000 * eta**2 * self.sensititivty_c1()) / ((d_aus + d) * math.sqrt(3))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteExzentrizitaetMOAus.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_Fm_Exzentrizitaet_MO_Inn(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1111, const_list, "&delta;E<sub>Inn</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Gemessenden_Exzentrizitaet"],
                TKompConstants["TC_Fm_Tastkugeldurchmesser"],
                TKompConstants["TC_Fm_Innendurchmesser_MO"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "mm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteExzentrizitaetMOInn.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVAL
            else:
                return self.data.TermL1
        except Exception as e:
            print(f"[Fehler in KomponenteExzentrizitaetMOInn.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        # Platzhalter für spätere Erweiterung – aktuell keine Formel im Delphi-Code
        return 1.0

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            eta = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Gemessenden_Exzentrizitaet
            ]
            d_inn = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Innendurchmesser_MO
            ]
            d = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Tastkugeldurchmesser
            ]

            if all(x != MU_NAN for x in [eta, d_inn, d]) and (d_inn - d) != 0:
                return (1000 * eta**2 * self.sensititivty_c1()) / ((d_inn - d) * math.sqrt(3))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteExzentrizitaetMOInn.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_Fm_Nivellierung_Zylinderachse_MO_Rund(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1112, const_list, "&delta;Z<sub>R</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Kippung_MO_XAchse"],
                TKompConstants["TC_Fm_Kippung_MO_YAchse"],
                TKompConstants["TC_Fm_Aussendurchmesser_MO"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteNivellierungZylinderachseMORund.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVAL
            else:
                return self.data.TermL1
        except Exception as e:
            print(f"[Fehler in KomponenteNivellierungZylinderachseMORund.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        # Wird verwendet, auch wenn im Delphi-Code kein eigener Sensitivitätsfaktor berechnet wurde.
        return 1.0

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            d_aus = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Aussendurchmesser_MO
            ]
            alpha_x = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Kippung_MO_XAchse
            ]
            alpha_y = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Kippung_MO_YAchse
            ]

            if all(x != MU_NAN for x in [d_aus, alpha_x, alpha_y]):
                alpha_x_rad = alpha_x * 0.0001
                alpha_y_rad = alpha_y * 0.0001

                grundwert = (1000 * (d_aus / 2)) / math.sqrt(3)
                winkelterm = math.sqrt(
                    (1 / math.cos(alpha_x_rad) - 1) ** 2 +
                    (1 / math.cos(alpha_y_rad) - 1) ** 2
                )
                return grundwert * self.sensititivty_c1() * winkelterm
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteNivellierungZylinderachseMORund.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_Fm_Nivellierung_Zylinderachse_MO_Gerade(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1113, const_list, "&delta;Z<sub>G</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Aussendurchmesser_MO"],
                TKompConstants["TC_Fm_Neigung_Zylinderachse_MO_zu_Flaeche_XOY"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteNivellierungZylinderachseMOGerade.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVAL
            else:
                return self.data.TermL1
        except Exception as e:
            print(f"[Fehler in KomponenteNivellierungZylinderachseMOGerade.b_val] {e}")
            return MU_NAN

    def sensititivty_c1(self):
        # Platzhalter – wird im UB verwendet
        return 1.0

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            d_aus = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Aussendurchmesser_MO
            ]
            alpha = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Neigung_Zylinderachse_MO_zu_Flaeche_XOY
            ]

            if d_aus != MU_NAN and alpha != MU_NAN:
                a_alpha = 54575 * alpha**2 + (-366.57 * alpha) + 0.3414
                b_alpha = (-5.2768 * alpha) + -0.7821
                abw = a_alpha * math.pow(d_aus / 2, b_alpha)
                return (abw / math.sqrt(3)) * self.sensititivty_c1()
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteNivellierungZylinderachseMOGerade.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN


class TK_Fm_Deformation_MO(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1114, const_list, "&delta;A<sub>ufspann</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.FieldsToEdit = [
                "EF_Term0",
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteDeformationMO.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

class TK_Fm_Fuehrungsabweichung_ME(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1115, const_list, "&delta;F<sub>ür</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_Fm_Formabweichung_Normal"],
                TKompConstants["TC_Fm_Kalibrierung_Normal"],
                TKompConstants["TC_Fm_Standardabweichung_Wiederholmessungen_Normal"],
                TKompConstants["TC_Fm_AnzahlMessungen_Fuehrungsabweichung"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = ""
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KomponenteFuehrungsabweichungME.__init__] {e}")

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'

    def b_val(self):
        try:
            if self.archiv:
                return self.arch_data.BVAL
            else:
                return self.data.TermL1
        except Exception as e:
            print(f"[Fehler in KomponenteFuehrungsabweichungME.b_val] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0

            fn = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Formabweichung_Normal
            ]
            fnk = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Kalibrierung_Normal
            ]
            uf = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_Standardabweichung_Wiederholmessungen_Normal
            ]
            n = self.modell.const_list.const_map[
                TKompConstants.TC_Fm_AnzahlMessungen_Fuehrungsabweichung
            ]

            if all(x != MU_NAN for x in [fn, fnk, uf, n]) and n > 0:
                return math.sqrt((1 / 12) * fn ** 2 + (fnk / 2) ** 2 + (uf ** 2) / n)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KomponenteFuehrungsabweichungME.unsicherheitsbeitrag_l0] {e}")
            return MU_NAN

class TK_Fm_Temperatur(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1116, const_list, '&delta;T')
        self.const_list = const_list
        self.archiv = False
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.FieldsToEdit = ['EF_Term0', 'EF_Verteilung', 'EF_Kennwertart', 'EF_Freheitsgrad']
        self.Einheit = 'µm'

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_Fm_Drift_Empfindlichkeit_ME(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1117, const_list, '&delta;D<sub>rift</sub>')
        self.const_list = const_list
        self.archiv = False
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.FieldsToEdit = ['EF_Term0', 'EF_Verteilung', 'EF_Kennwertart', 'EF_Freheitsgrad']

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_Fm_Messabweichung_Kalibrierung_ME_Tastsystem(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1118, const_list, '&delta;T<sub>ast</sub>')
        self.const_list = const_list
        self.archiv = False
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.FieldsToEdit = ['EF_Term0', 'EF_Verteilung', 'EF_Kennwertart', 'EF_Freheitsgrad']

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_Fm_Kalibrierung_ME_Tastsystem(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1119, const_list, '&delta;l<sub>K</sub>')
        self.const_list = const_list
        self.archiv = False
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.FieldsToEdit = ['EF_Term0', 'EF_Verteilung', 'EF_Kennwertart', 'EF_Freheitsgrad']

    def clear(self):
        super().clear()
        self.data.Verteilung = 'V_Normal'
        self.data.KennwertArt = 'K_Standardabweichung'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'


class TK_KTMG_Abstand_system(TMU_Komponente):
    def __init__(self, modell, const_list,lfdnr):
        super().__init__(modell, 1121, const_list, "&delta;&eta;<sub>y;s</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "µm"
        self.dez = 5
        self.ConstNeeded += [
            TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
            TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
        ]
        self.fields_to_edit = ["EF_Freheitsgrad"]
        self.addConstNeededToModell()
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )

    def sensititivty_c1(self) -> float:
        return 1.0

    def clear(self):
        super().clear()
        self.data.Verteilung = "V_Rechteck"
        self.data.KennwertArt = "K_Spannweite"
        self.data.Freiheitsgrad = "FG_unbegrenzt"

    def a_val(self) -> float:
        try:
            d = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
            af = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            A = 0.2
            tau = 0.4
            A2 = -0.08
            tau2 = 0.2

            if MU_NAN not in (d, af, n) and n != 0:
                val = math.sqrt(20 / n) * (
                    A * math.exp(-1000 * tau * d) * af +
                    A2 * math.exp(-1000 * tau2 * d)
                )
                return val
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in a_val (system): {e}")
            return MU_NAN


class TK_KTMG_Abstand_zufall(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1122, const_list, "&delta;&eta;<sub>y;z</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "µm"
        self.dez = 5
        self.ConstNeeded += [
            TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
            TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
        ]
        self.fields_to_edit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]
        self.addConstNeededToModell()
        self.data = TMuKompRec(
            TermL0=0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )

    def sensititivty_c1(self) -> float:
        return 1.0

    def clear(self):
        super().clear()
        self.data.Verteilung = "V_Rechteck"
        self.data.KennwertArt = "K_Standardabweichung"
        self.data.Freiheitsgrad = "FG_unbegrenzt"

    def a_val(self) -> float:
        try:
            d = self.modell.const_list.const_map[TKompConstants.TC_Messwert]
            af = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            if MU_NAN not in (d, af, n):
                val = math.sqrt(20 / n) * (
                    (0.1 + 0.06 * (1 - math.exp(-1000 * 0.4 * d))) * af +
                    0.04 * math.exp(-1000 * 0.2 * d)
                )
                return val
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in a_val (zufall): {e}")
            return MU_NAN


class TK_KTMG_Geradheit_system(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1126, const_list, "&delta;G<sub>MEKA;s</sub>")
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
                TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
                TKompConstants["TC_Messwert"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_Geradheit_System.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in KTMG_Geradheit_System.clear] {e}")

    def a_val(self):
        try:
            G = self.modell.const_list.const_map[TKompConstants.TC_Messwert] * 1000
            AF = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            if any(val == MU_NAN for val in [G, AF, n]):
                return MU_NAN

            if 1 < G <= 100:
                fak = 0.02 + (0.2 / G) + (-0.2 / (G ** 2))
            elif 0 < G <= 1:
                fak = 0.0198 * G + (-0.0009)
            else:
                return MU_NAN

            A1 = 1.59
            tau1 = 10
            B1 = 0.22

            return math.sqrt(20 / n) * (
                fak * (AF ** 2) + (A1 * math.exp(-G / tau1) + B1) * AF
            )
        except Exception as e:
            print(f"[Fehler in KTMG_Geradheit_System.a_val] {e}")
            return MU_NAN


class TK_KTMG_Geradheit_zufall(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1127, const_list, "&delta;G<sub>MEKA;z</sub>")
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
                TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
                TKompConstants["TC_Messwert"],
            ]
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "µm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_Geradheit_Zufall.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 1
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in KTMG_Geradheit_Zufall.clear] {e}")

    def a_val(self):
        try:
            G = self.modell.const_list.const_map[TKompConstants.TC_Messwert] * 1000
            AF = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            if any(val == MU_NAN for val in [G, AF, n]):
                return MU_NAN

            b1 = -2.56e-5
            b2 = 4.54e-3
            b3 = 3.43e-1
            A1 = 0.5
            tau1 = 0.008
            BB1 = -0.5

            return math.sqrt(20 / n) * (
                (b1 * G ** 2 + b2 * G + b3) * AF + A1 * math.exp(tau1 * G) + BB1
            )
        except Exception as e:
            print(f"[Fehler in KTMG_Geradheit_Zufall.a_val] {e}")
            return MU_NAN



class TK_KTMG_Radius_system(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1128, const_list, "δR<sub>MEKA;s</sub>")
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
                TKompConstants["TC_KTMG_Sektor_Kreis"],
                TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
            ]
            tc_messwert = TKompConstants.TC_Messwert

            if tc_messwert in self.ConstNeeded:
                self.ConstNeeded.remove(tc_messwert)
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c1_val = 1
            self.c2_val = 0
            self.Einheit = "mm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_Radius_system.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in KTMG_Radius_system.clear] {e}")

    def a_val(self):
        try:
            phi = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Sektor_Kreis]
            AF = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            A1 = 3
            tau1 = 4.38
            b1 = 13.431
            b2 = 55.492

            if MU_NAN in (phi, AF, n):
                return MU_NAN

            return math.sqrt(20 / n) * A1 * math.exp(AF / tau1) * math.exp(-phi / (b1 * math.log(AF) + b2))
        except Exception as e:
            print(f"[Fehler in KTMG_Radius_system.a_val] {e}")
            return MU_NAN


class TK_KTMG_Radius_zufall(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1129, const_list, "δR<sub>MEKA;z</sub>")
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
                TKompConstants["TC_KTMG_Sektor_Kreis"],
                TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
            ]
            tc_messwert = TKompConstants.TC_Messwert

            if tc_messwert in self.ConstNeeded:
                self.ConstNeeded.remove(tc_messwert)
            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.c1_val = 1
            self.c2_val = 0
            self.Einheit = "mm"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_Radius_zufall.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = 2
            self.data.KennwertArt = 2
            self.data.Freiheitsgrad = 2
        except Exception as e:
            print(f"[Fehler in KTMG_Radius_zufall.clear] {e}")

    def a_val(self):
        try:
            phi = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Sektor_Kreis]
            AF = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            a1 = 1.32
            a2 = 0.02
            b1 = 0.161
            b2 = 122.6

            if MU_NAN in (phi, AF, n):
                return MU_NAN

            return math.sqrt(20 / n) * (a1 * AF + a2) * math.exp(-phi / (b1 * AF + b2))
        except Exception as e:
            print(f"[Fehler in KTMG_Radius_zufall.a_val] {e}")
            return MU_NAN


class TK_KTMG_Winkel_plastVerform(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1125, const_list, "&delta;a<sub>pl</sub>")
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",     # Standardwerte wie im Delphi-Code
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1
            )
            self.ConstNeeded += [TKompConstants["TC_KTMG_Laenge_kleinster_Schenkel"]]
            tc_messwert = TKompConstants.TC_Messwert

            if tc_messwert in self.ConstNeeded:
                self.ConstNeeded.remove(tc_messwert)

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad"
            ]

            self.c1_val = 1
            self.c2_val = 0  # immer

            self.Einheit = "°"
            self.addConstNeededToModell()

        except Exception as e:
            print(f"[Fehler in KTMG_WinkelPlastVerformComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KTMG_WinkelPlastVerformComponent.clear] {e}")

    def a_val(self):
        try:
            L = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Laenge_kleinster_Schenkel]
            apl = 0.02
            if L != MU_NAN:
                return 180 / math.pi * math.atan(apl / (1000 * L))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KTMG_WinkelPlastVerformComponent.a_val] {e}")
            return MU_NAN


class TK_KTMG_Winkel_Tastspitzenradius(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1130, const_list, "&delta;R<sub>ME</sub>")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_Spannweite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            self.ConstNeeded += [TKompConstants["TC_KTMG_Laenge_kleinster_Schenkel"]]
            tc_messwert = TKompConstants.TC_Messwert

            if tc_messwert in self.ConstNeeded:
                self.ConstNeeded.remove(tc_messwert)

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]

            self.c1_val = 1
            self.c2_val = 0

            self.Einheit = "°"
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_WinkelTastspitzenradiusComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_Spannweite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KTMG_WinkelTastspitzenradiusComponent.clear] {e}")

    def a_val(self):
        try:
            L = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Laenge_kleinster_Schenkel]
            rME = 0.01  # Konstante aus Delphi
            if L != MU_NAN:
                return 180 / math.pi * math.atan(rME / (1000 * L))
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in KTMG_WinkelTastspitzenradiusComponent.a_val] {e}")
            return MU_NAN


class TK_KTMG_Winkel_system(TMU_Komponente):

    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1123, const_list, "δW<sub>MEKA;s</sub>")
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Rechteck",
                KennwertArt="K_HalbWeite",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )
            self.ConstNeeded += [
                TKompConstants["TC_KTMG_Gemessener_Winkel"],
                TKompConstants["TC_KTMG_Laenge_kleinster_Schenkel"],
                TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
                TKompConstants["TC_KTMG_Anzahl_Messpunkte"]
            ]
            tc_messwert = TKompConstants.TC_Messwert

            if tc_messwert in self.ConstNeeded:
                self.ConstNeeded.remove(tc_messwert)

            self.FieldsToEdit = [
                "EF_Verteilung",
                "EF_Kennwertart",
                "EF_Freheitsgrad",
            ]
            self.Einheit = "°"
            self.c1_val = 1
            self.c2_val = 0
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_Winkel_systemComponent.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Rechteck"
            self.data.KennwertArt = "K_HalbWeite"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KTMG_Winkel_systemComponent.clear] {e}")

    def a_val(self):
        try:
            phi_stern = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Gemessener_Winkel]
            phi = phi_stern
            if 0 <= phi_stern <= 90:
                phi = phi_stern
            elif 90 < phi_stern <= 180:
                phi = 180 - phi_stern
            elif 180 < phi_stern <= 270:
                phi = phi_stern - 180
            elif 270 < phi_stern <= 360:
                phi = 360 - phi_stern

            l = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Laenge_kleinster_Schenkel]
            af = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            if any(val == MU_NAN for val in [phi, l, af, n]):
                return MU_NAN

            a1 = -4 * 10 ** -6
            tau1 = 2.5
            a2 = 9 * 10 ** -4
            tau2 = 2.5

            return math.sqrt(20 / n) * (
                a2 * math.exp(-l / tau2) + a1 * math.exp(-l / tau1) * phi
            ) * af

        except Exception as e:
            print(f"[Fehler in KTMG_Winkel_systemComponent.a_val] {e}")
            return MU_NAN


class TK_KTMG_Winkel_zufall(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 1124, const_list, "&delta;W<sub>MEKA;z</sub>")
            self.archiv = False
            self.lfdnr = lfdnr

            self.data = TMuKompRec(
                TermL0=0,
                TermL1=0,
                Verteilung="V_Normal",
                KennwertArt="K_Standardabweichung",
                Freiheitsgrad="FG_unbegrenzt",
                FreiN_minus_1=0,
                Flags=1,
            )

            # Konstanten setzen (Liste bearbeiten, TC_Messwert entfernen, andere hinzufügen)
            self.ConstNeeded += [
                TKompConstants["TC_KTMG_Gemessener_Winkel"],
                TKompConstants["TC_KTMG_Laenge_kleinster_Schenkel"],
                TKompConstants["TC_KTMG_Konstanter_Anteil_EMPE"],
                TKompConstants["TC_KTMG_Anzahl_Messpunkte"],
            ]
            tc_messwert = TKompConstants.TC_Messwert

            if tc_messwert in self.ConstNeeded:
                self.ConstNeeded.remove(tc_messwert)

            self.FieldsToEdit = ["EF_Freheitsgrad"]
            self.c1_val = 1
            self.c2_val = 0
            self.Einheit = None
            self.addConstNeededToModell()
        except Exception as e:
            print(f"[Fehler in KTMG_Winkel_zufall.__init__] {e}")

    def clear(self):
        try:
            super().clear()
            self.data.Verteilung = "V_Normal"
            self.data.KennwertArt = "K_Standardabweichung"
            self.data.Freiheitsgrad = "FG_unbegrenzt"
        except Exception as e:
            print(f"[Fehler in KTMG_Winkel_zufall.clear] {e}")

    def a_val(self):
        try:
            PhiStern = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Gemessener_Winkel]
            Phi = PhiStern

            if 0 <= PhiStern <= 90:
                Phi = PhiStern
            elif 90 < PhiStern <= 180:
                Phi = 180 - PhiStern
            elif 180 < PhiStern <= 270:
                Phi = PhiStern - 180
            elif 270 < PhiStern <= 360:
                Phi = 360 - PhiStern

            L = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Laenge_kleinster_Schenkel]
            AF = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE]
            n = self.modell.const_list.const_map[TKompConstants.TC_KTMG_Anzahl_Messpunkte]

            if any(x == MU_NAN for x in [AF, n, Phi, L]):
                return MU_NAN

            A1 = -1.4 * 10 ** -4
            tau1 = 3
            A2 = 4 * 10 ** -2
            tau2 = 6.5

            return (
                math.sqrt(20 / n)
                * (
                    A2 * math.exp(-L / tau2)
                    + A1 * math.exp(-L / tau1) * Phi
                )
                * AF
            )
        except Exception as e:
            print(f"[Fehler in KTMG_Winkel_zufall.a_val] {e}")
            return MU_NAN
