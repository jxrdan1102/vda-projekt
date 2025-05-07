import math

from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
)
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import TMU_Komponente

# __all__ = ["KomponenteA", "TK_KalibrierungME", "TK_Kalibrierung_EN", "TK_AufloesungME","TK_Wiederholpraezision","TK_NichtZentrischeAntastung","TK_AbweichungPoissonKoeffizientMO_EN", "TK_AbweichungElastizitaetsModul_MO_EN", "TK_TempDifferenz_MO_ME", "TK_AbweichungMittlereTemp_MO_ME"]


MU_NAN = math.nan


class KomponenteA(TMU_Komponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 12, const_list, "notthere")
        self.id = 1
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
        # self.setData(0.15,0,'V_Rechteck','K_HalbWeite','FG_unbegrenzt',0,1)

        # Initialisierung wie im Delphi-Code
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

    def get_const_needed(self):
        return self.ConstNeeded

    def get_fields_edit(self):
        return self.FieldsToEdit

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 2
        self.data.Freiheitsgrad = 2

    def b_val(self):
        # Beispielmethode, die 0 zurückgibt
        return 0

    def sensitivity_c1(self):
        # Implementierung der Sensitivitätsberechnung
        dk = 10 / 1000  # Umrechnung in Meter
        En = 200000000000
        Emo = 210000000000
        Vn = 0.21
        Vmo = 0.22
        F = 0.75
        r = 0.9

        E = (Emo + En) / 2
        v = (Vmo + Vn) / 2

        # Wenn einer der Werte NaN ist, wird der Wert NaN zurückgegeben
        if (
            (E == MU_NAN)
            or (dk == MU_NAN)
            or (En == MU_NAN)
            or (Emo == MU_NAN)
            or (E == MU_NAN)
            or (v == MU_NAN)
            or (Vn == MU_NAN)
            or (Vmo == MU_NAN)
            or (F == MU_NAN)
            or (r == MU_NAN)
        ):
            return MU_NAN
        else:
            return (
                1.1
                * math.pow(10, 6)
                * math.pow(dk, -1 / 3)
                * math.pow((1 - v**2) / E, 2 / 3)
                * math.pow(F, -1 / 3)
            )

    def unsicherheitsbeitrag_l0(self):
        # Berechnung des Unsicherheitsbeitrags L0
        if self.archiv:
            return self.arch_data.UNSBL0
        else:
            su = self.std_unsicherheit(
                self.a_val()
            )  # Platzhalter für Standardunsicherheit
            c1 = self.sensitivity_c1()
            r = 0.9
            print("Testi",self.std_unsicherheit(self.a_val()), self.sensitivity_c1())
            if (su != MU_NAN) and (c1 != MU_NAN) and (r != MU_NAN) and (r <= 1):
                return 2 * su * c1 * math.sqrt(1 - r)
            else:
                return MU_NAN


class TK_KalibrierungME(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt
        # die Werte
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
        # self.setData(terml0 = 0.035,verteilung = 3,kennwertart = 2,freiheitsgrad=2)
        self.id = 2
        self.ConstNeeded += []
        self.addConstNeededToModell()

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 3
        self.data.KennwertArt = 2
        self.data.Freiheitsgrad = 2


class TK_Kalibrierung_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt
        # die Werte
        super().__init__(AModell, 1027, AConstList, "&delta;I<sub>ENK</sub>")
        self.ConstNeeded += [
            TKompConstants["TC_NennmassEN"]
        ]  # Beispielhafte Konstante für TC_NennmassEN
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
        # self.setData(terml0 = 0.05, terml1 = 0.0000012,verteilung = 3,kennwertart = 2,freiheitsgrad=2)
        self.id = 3
        self.addConstNeededToModell()

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 3
        self.data.KennwertArt = 2
        self.data.Freiheitsgrad = 2

    def unsicherheitsbeitrag_l1(self):
        # Berechnet den Unsicherheitsbeitrag L1
        if hasattr(self, "archiv") and self.archiv:
            # Beispielhafte Verwendung von Archivdaten
            return self.ArchData["UNSBL1"]
        else:
            su = self.std_unsicherheit(
                self.b_val()
            )  # Beispielhafte Methode für die Standardunsicherheit
            c2 = self.sensititivty_c2()  # Beispielhafte Sensitivitätskonstante
            NennmassEN = 1 * 1000  # Messwert in mm, Berechnung in µm

            if su != MU_NAN and c2 != MU_NAN and NennmassEN != MU_NAN:
                return su * c2 * NennmassEN
            else:
                return MU_NAN


class TK_AufloesungME(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt
        # die Werte
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
        # self.setData(terml0 = 0.005,verteilung = 2,kennwertart = 3,freiheitsgrad=2)
        self.ConstNeeded += []
        self.id = 4
        self.addConstNeededToModell()
        self.lfdnr = lfdnr


    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 2
        self.data.Freiheitsgrad = 2


class TK_Wiederholpraezision(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
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

        # self.setData(terml0 = 0.01,verteilung = 3,kennwertart = 4,freiheitsgrad=2)

        self.ConstNeeded += []
        self.id = 5
        self.addConstNeededToModell()

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 3
        self.data.KennwertArt = 4
        self.data.Freiheitsgrad = 2


class TK_NichtZentrischeAntastung(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt
        # die Werte
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

        # self.setData(verteilung = 2,kennwertart = 2,freiheitsgrad=2)

        self.id = 6

        self.ConstNeeded += [
            TKompConstants["TC_Radius_der_Zone_des_Spiels"],
            TKompConstants["TC_Laenge_kurze_Kante_PEM"],
            TKompConstants["TC_Tol_Abw_Spanne_ISO_3650"],
        ]
        self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]
        self.addConstNeededToModell()

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 4
        self.data.Freiheitsgrad = 2

    def a_val(self):
        # Berechnung von a_Val
        r = 0.5
        g = 9
        v = 0.12

        if g != 0 and r != MU_NAN and g != MU_NAN and v != MU_NAN:
            return r * v / g
        else:
            return MU_NAN

    def b_val(self):
        # Berechnung von b_Val
        return 0


class TK_AbweichungPoissonKoeffizientMO_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
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
        # self.setData(verteilung = 2,kennwertart = 3,freiheitsgrad=2)

        self.id = 7

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

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 4
        self.data.Freiheitsgrad = 2

    def a_Val(self):
        # Berechnung von a_Val
        Vn = 0.21
        Vmo = 0.22
        if Vn != MU_NAN and Vmo != MU_NAN:
            return abs(Vmo - Vn) / 2
        else:
            return MU_NAN

    def b_val(self):
        # Berechnung von b_Val
        return 0

    def sensitivity_c1(self):
        # Berechnung der Sensitivität C1
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

    def unsicherheitsbeitrag_l0(self):
        su = self.StdUnsicherheit(self.a_Val())
        c1 = self.sensitivity_c1()
        if su != MU_NAN and c1 != MU_NAN:
            return 2 * su * c1
        else:
            return MU_NAN

    def StdUnsicherheit(self, value):
        if value == MU_NAN:
            return MU_NAN
        else:
            return value * 0.1


class TK_AbweichungElastizitaetsModul_MO_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
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
        # self.setData(verteilung = 2,kennwertart = 3,freiheitsgrad=2)

        self.id = 8

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

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 4
        self.data.Freiheitsgrad = 2

    def a_val(self):
        # Berechnung von a_Val
        En = 200000000000
        Emo = 210000000000
        if En != MU_NAN and Emo != MU_NAN:
            return abs(Emo - En) / 2
        else:
            return MU_NAN

    def b_val(self):
        # Berechnung von b_Val
        return 0

    def sensititivty_c1(self):
        # Berechnung der Sensitivität C1
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

    def unsicherheitsbeitrag_l0(self):
        su = self.std_unsicherheit(self.a_val())
        c1 = self.sensititivty_c1()
        if su != MU_NAN and c1 != MU_NAN:
            return 2 * su * c1
        else:
            return MU_NAN


class TK_TempDifferenz_MO_ME(TMU_Komponente):
    def __init__(self, AModell, AConstList,lfdnr):
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
        self.id = 9

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

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 3
        self.data.Freiheitsgrad = 2

    def b_val(self):
        # Berechnung von b_Val
        tx = 20.2
        tn = 20.0
        if tx != MU_NAN and tn != MU_NAN:
            return abs(tx - tn)
        else:
            return MU_NAN

    def sensititivty_c2(self):
        ax = 0.0000115
        an = 0.0000115
        if ax != MU_NAN and an != MU_NAN:
            return (ax + an) / 2
        else:
            return MU_NAN


class TK_AbweichungMittlereTemp_MO_ME(TMU_Komponente):
    def __init__(self, AModell, AConstList, lfdnr):
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
        self.id = 10
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

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        super().clear()
        self.data.Verteilung = 2
        self.data.KennwertArt = 2
        self.data.Freiheitsgrad = 2

    def b_val(self):
        # Berechnet den Temperaturunterschied b_Val
        tx = 20.2
        tn = 20

        if tx is None or tn is None:
            return None
        return abs((tx + tn) / 2 - 20)

    def sensititivty_c2(self):
        # Berechnet die Sensitivität C2 basierend auf den
        # Ausdehnungskoeffizienten
        ax = 0.000015
        an = 0.000015

        if ax is None or an is None:
            return None
        return abs(ax - an) / (2 * math.sqrt(3))
