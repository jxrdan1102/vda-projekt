import math

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import TMU_Komponente

MU_NAN = math.nan


class KomponenteA(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        try:
            super().__init__(modell, 12, const_list, "notthere")
            self.const_list = const_list
            self.archiv = False
            self.lfdnr = lfdnr
            self.data = TMuKompRec(
                TermL0=0.15,
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
                "EF_Freheitsgrad",
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

    def sensitivity_c1(self):
        try:
            dk = 10 / 1000
            En = 200e9
            Emo = 210e9
            Vn = 0.21
            Vmo = 0.22
            F = 0.75
            r = 0.9
            E = (Emo + En) / 2
            v = (Vmo + Vn) / 2
            if any(val == MU_NAN for val in [dk, En, Emo, E, v, Vn, Vmo, F]):
                return MU_NAN
            return (
                1.1
                * math.pow(10, 6)
                * math.pow(dk, -1 / 3)
                * math.pow((1 - v**2) / E, 2 / 3)
                * math.pow(F, -1 / 3)
            )
        except Exception as e:
            print(f"[Fehler in KomponenteA.sensitivity_c1] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l0(self):
        try:
            if self.archiv:
                return self.arch_data.UNSBL0
            su = self.std_unsicherheit(self.a_val())
            c1 = self.sensitivity_c1()
            r = 0.9
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
            NennmassEN = 1 * 1000  # Beispielwert

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
            r = 0.5
            g = 9
            v = 0.12

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
            Vn = 0.21
            Vmo = 0.22
            if Vn != MU_NAN and Vmo != MU_NAN:
                return abs(Vmo - Vn) / 2
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.a_Val] {e}")
            return MU_NAN

    def b_val(self):
        return 0

    def sensitivity_c1(self):
        try:
            dk = 10 / 1000  # Eingabe in mm, Berechnung in m
            En = 200000000000
            Emo = 210000000000
            Vn = 0.21
            Vmo = 0.22
            F = 0.75
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
            print(f"[Fehler in TK_AbweichungPoissonKoeffizientMO_EN.sensitivity_c1] {e}")
            return MU_NAN

    def unsicherheitsbeitrag_l0(self):
        try:
            su = self.StdUnsicherheit(self.a_Val())
            c1 = self.sensitivity_c1()
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
            En = 200000000000
            Emo = 210000000000
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
            dk = 10 / 1000  # Eingabe in mm, Berechnung in m
            En = 200000000000
            Emo = 210000000000
            Vn = 0.21
            Vmo = 0.22
            F = 0.75
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
            tx = 20.2
            tn = 20.0
            if tx != MU_NAN and tn != MU_NAN:
                return abs(tx - tn)
            else:
                return MU_NAN
        except Exception as e:
            print(f"[Fehler in TK_TempDifferenz_MO_ME.b_val] {e}")
            return MU_NAN

    def sensititivty_c2(self):
        try:
            ax = 0.0000115
            an = 0.0000115
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
            tx = 20.2
            tn = 20

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
            ax = 0.000015
            an = 0.000015

            if ax is None or an is None:
                return None
            return abs(ax - an) / (2 * math.sqrt(3))
        except Exception as e:
            print(f"[Fehler in TK_AbweichungMittlereTemp_MO_ME.sensititivty_c2] {e}")
            return None