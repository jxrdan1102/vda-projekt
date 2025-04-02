import math


__all__ = ["KomponenteA", "TK_KalibrierungME", "TK_Kalibrierung_EN", "TK_AufloesungME","TK_Wiederholpraezision","TK_NichtZentrischeAntastung","TK_AbweichungPoissonKoeffizientMO_EN", "TK_AbweichungElastizitaetsModul_MO_EN", "TK_TempDifferenz_MO_ME", "TK_AbweichungMittlereTemp_MO_ME"]

from app.services.component_service.component_abstract import TMU_Komponente

from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec

MU_NAN = math.nan
class KomponenteA(TMU_Komponente):
    def __init__(self, modell, const_list):
        print("KomponenteA Construktor wurde aufgerufen!")
        super().__init__(0, 12, const_list,"notthere")
        print("Jesus ist gekommen!")
        # Konstruktoraufruf der Basisklasse (wir simulieren diesen in Python)
        self.id = 1
        self.modell = modell
        self.const_list = const_list
        self.archiv = False  # Beispielwert für Archivstatus
        self.data = TMuKompRec(0.15,0,'V_Rechteck','K_HalbWeite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()

        # Initialisierung wie im Delphi-Code
        self.ConstNeeded = [
            'TC_MesskraftME',
            'TC_DurchmesserMesseinsatzME',
            'TC_Elast_Modul_Normal',
            'TC_Elast_Modul_MO',
            'TC_Poisson_Koeff_Normal',
            'TC_Poisson_Koeff_MO',
            'TC_Korrelationskoeffizient'
        ]
        self.FieldsToEdit = ['EF_Term0', 'EF_Verteilung', 'EF_Kennwertart', 'EF_Freheitsgrad']
        self.Einheit = 'N'

    def get_const_needed(self):
        return self.ConstNeeded

    def get_fields_edit(self):
        return self.FieldsToEdit

    def clear(self):
        # Diese Methode wird aufgerufen, um die Felder zurückzusetzen
        self.data.Verteilung = 'V_Rechteck'
        self.data.KennwertArt = 'K_HalbWeite'
        self.data.Freiheitsgrad = 'FG_unbegrenzt'
        self.data.TermL0 = 0.15

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
        if (E == MU_NAN) or (dk == MU_NAN) or (En == MU_NAN) or (Emo == MU_NAN) or (E == MU_NAN) or \
                (v == MU_NAN) or (Vn == MU_NAN) or (Vmo == MU_NAN) or (F == MU_NAN) or (r == MU_NAN):
            return MU_NAN
        else:
            return 1.1 * math.pow(10, 6) * math.pow(dk, -1 / 3) * math.pow((1 - v ** 2) / E, 2 / 3) * math.pow(F,
                                                                                                               -1 / 3)

    def unsicherheitsbeitrag_l0(self):
        # Berechnung des Unsicherheitsbeitrags L0
        if self.archiv:
            return self.arch_data.UNSBL0
        else:
            su = self.std_unsicherheit(self.a_val())  # Platzhalter für Standardunsicherheit
            c1 = self.sensitivity_c1()
            r = 0.9
            if (su != MU_NAN) and (c1 != MU_NAN) and (r != MU_NAN) and (r <= 1):
                return 2 * su * c1 * math.sqrt(1 - r)
            else:
                return MU_NAN

class TK_KalibrierungME(TMU_Komponente):
    def __init__(self, AModell, AConstList):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt die Werte
        super().__init__( 0, 1001, AConstList, '&delta;I<sub>ME</sub>')
        self.data = TMuKompRec(0.035,0,'V_Normal','K_HalbWeite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 2


    def clear(self):
        # Preset defaults, ruft die clear Methode der Basisklasse auf
        super().clear()
        # Setze Standardwerte für die Instanz
        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'


class TK_Kalibrierung_EN(TMU_Komponente):
    def __init__(self,  AModell, AConstList):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt die Werte
        super().__init__( 0, 1027, AConstList, '&delta;I<sub>ENK</sub>')
        self.ConstNeeded = ["TC_NennmassEN"]  # Beispielhafte Konstante für TC_NennmassEN
        self.data = TMuKompRec(0.05,0.0000012,'V_Normal','K_HalbWeite','FG_unbegrenzt',0,1)
        self.id = 3
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()

    def clear(self):
        # Preset defaults, ruft die clear Methode der Basisklasse auf
        super().clear()
        # Setze Standardwerte für die Instanz

        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'

    def unsicherheitsbeitrag_l1(self):
        # Berechnet den Unsicherheitsbeitrag L1
        if hasattr(self, 'archiv') and self.archiv:
            return self.ArchData["UNSBL1"]  # Beispielhafte Verwendung von Archivdaten
        else:
            su = self.std_unsicherheit(self.b_val())  # Beispielhafte Methode für die Standardunsicherheit
            c2 = self.sensititivty_c2()  # Beispielhafte Sensitivitätskonstante
            NennmassEN = 1 * 1000  # Messwert in mm, Berechnung in µm

            if su != MU_NAN and c2 != MU_NAN and NennmassEN != MU_NAN:
                return su * c2 * NennmassEN
            else:
                return MU_NAN

class TK_AufloesungME(TMU_Komponente):
    def __init__(self,  AModell, AConstList):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt die Werte
        super().__init__( 0, 1003, AConstList, '&delta;I<sub>MEW</sub>')
        self.data = TMuKompRec(0.005,0,'V_Rechteck','K_Spannweite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 4

    def clear(self):
        # Preset defaults, ruft die clear Methode der Basisklasse auf
        super().clear()
        # Setze Standardwerte für die Instanz
        self.data.Verteilung: 'V_Rechteck'
        self.data.KennwertArt: 'K_Spannweite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'

class TK_Wiederholpraezision(TMU_Komponente):
    def __init__(self,  AModell, AConstList):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt die Werte
        super().__init__( 0, 1040, AConstList, '&delta;W')
        self.data = TMuKompRec(0.01,0,'V_Normal','K_Standardabweichung','FG_unbegrenzt',0,1)
        self.ConstNeeded = []
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 5

    def clear(self):
        # Preset defaults, ruft die clear Methode der Basisklasse auf
        super().clear()
        # Setze Standardwerte für die Instanz
        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'



class TK_NichtZentrischeAntastung(TMU_Komponente):
    def __init__(self, AModell, AConstList):
        # Der Konstruktor ruft den Konstruktor der Basisklasse auf und setzt die Werte
        super().__init__( 0, 1041, AConstList, '&delta;I<sub>v</sub>')
        self.data = TMuKompRec(0,0,'V_Rechteck','K_HalbWeite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 6

        self.ConstNeeded = [
            "TC_Radius_der_Zone_des_Spiels",
            "TC_Laenge_kurze_Kante_PEM",
            "TC_Tol_Abw_Spanne_ISO_3650"
        ]
        self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]

    def clear(self):
        # Preset defaults, ruft die clear Methode der Basisklasse auf
        super().clear()
        # Setze Standardwerte für die
        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'


    def a_val(self):
        # Berechnung von a_Val
        r = 0.5
        g = 9
        v = 0.12

        if g != 0 and r != MU_NAN and g != MU_NAN and v != MU_NAN:
            print("aval", r*v/g)
            return r * v / g
        else:
            return MU_NAN

    def b_val(self):
        # Berechnung von b_Val
        return 0


class TK_AbweichungPoissonKoeffizientMO_EN(TMU_Komponente):
    def __init__(self, AModell, AConstList):
        super().__init__( 0, 1043, AConstList, '&delta;V')
        self.data = TMuKompRec(0,0,'V_Rechteck','K_Spannweite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 7

        self.ConstNeeded = [
            "TC_MesskraftME",
            "TC_DurchmesserMesseinsatzME",
            "TC_Elast_Modul_Normal",
            "TC_Elast_Modul_MO",
            "TC_Poisson_Koeff_Normal",
            "TC_Poisson_Koeff_MO"
        ]
        self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]

    def clear(self):
        super().clear()
        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'


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
            return -1.47 * math.pow(10, 6) * math.pow(dk, -1/3) * math.pow(F, 2/3) * math.pow(E, -2/3) * v * math.pow(1 - math.pow(v, 2), -1/3)

    def unsicherheitsbeitrag_l0(self):
        su = self.StdUnsicherheit(self.a_Val())
        c1 = self.sensitivity_c1()
        print("hier fucken", su, c1)
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
    def __init__(self, AModell, AConstList):
        super().__init__( 0, 1044, AConstList, '&delta;E')
        self.data = TMuKompRec(0,0,'V_Rechteck','K_Spannweite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 8

        self.ConstNeeded = [
            "TC_MesskraftME",
            "TC_DurchmesserMesseinsatzME",
            "TC_Elast_Modul_Normal",
            "TC_Elast_Modul_MO",
            "TC_Poisson_Koeff_Normal",
            "TC_Poisson_Koeff_MO"
        ]
        self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]

    def clear(self):
        super().clear()

        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'


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
            return -0.733 * math.pow(10, 6) * math.pow(dk, -1/3) * math.pow(F, 2/3) * math.pow(E, -5/3) * math.pow(1 - math.pow(v, 2), 2/3)

    def unsicherheitsbeitrag_l0(self):
        # Berechnung des Unsicherheitsbeitrags L0
        su = self.std_unsicherheit(self.a_val())
        c1 = self.sensititivty_c1()
        if su != MU_NAN and c1 != MU_NAN:
            print("usbl0 = ", 2 * su * c1, "stdusbl0 = ", su)
            return 2 * su * c1
        else:
            return MU_NAN

class TK_TempDifferenz_MO_ME(TMU_Komponente):
    def __init__(self, AModell, AConstList):
        super().__init__( 0, 1009, AConstList, '&delta;t')
        self.data = TMuKompRec(0,0,'V_Rechteck','K_Spannweite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 9

        self.ConstNeeded = [
            "TC_TempME", "TC_TempMO", "TC_AusdehnKoeffME", "TC_AusdehnKoeffMO"
        ]
        self.FieldsToEdit = ["EF_Verteilung", "EF_Kennwertart", "EF_Freheitsgrad"]

        self.data.TermL0 : 0  # Vorbelegung
        self.data.TermL1 : -1  # Nicht benötigt, aber auch nicht NAN

        self.c1_val = 0  # Festlegung, c2 wird errechnet
        self.Einheit = "°C"

    def clear(self):
        super().clear()

        self.data.Verteilung: 'V_Normal'
        self.data.KennwertArt: 'K_HalbWeite'
        self.data.Freiheitsgrad: 'FG_unbegrenzt'
        self.data.TermL0: 0
        self.data.TermL1: -1


    def b_val(self):
        # Berechnung von b_Val
        tx = 20.2
        tn = 20.0
        if tx != MU_NAN and tn != MU_NAN:
            return abs(tx - tn)
        else:
            return MU_NAN

    def sensititivty_c2(self):
        # Berechnung der Sensitivität C2
        print("Gut ist das")
        ax = 0.0000115
        an = 0.0000115
        if ax != MU_NAN and an != MU_NAN:
            return (ax + an) / 2
        else:
            return MU_NAN


class TK_AbweichungMittlereTemp_MO_ME(TMU_Komponente):
    def __init__(self, AModell, AConstList):
        # Aufruf des Konstruktors der Basisklasse
        super().__init__( 0, 1010,AConstList,"notthere")
        self.data = TMuKompRec(0,0,'V_Rechteck','K_HalbWeite','FG_unbegrenzt',0,1)
        self.UnsicherheitsBeitrag = self.unsicherheitsbeitrag()
        self.EffektiverFreiheitsgrad = self.effektiver_freiheitsgrad()
        self.id = 10
        # Die spezifischen Initialisierungen für diese Klasse
        self.ConstNeeded = ['TC_TempME', 'TC_TempMO', 'TC_AusdehnKoeffME', 'TC_AusdehnKoeffMO']
        self.FieldsToEdit = ['EF_Verteilung', 'EF_Kennwertart', 'EF_Freheitsgrad']
        self.c1_val = 0
        self.Einheit = '°C'

    def clear(self):
        # Aufruf des Clear-Methoden der Basisklasse
        super().clear()

        # Weitere spezifische Initialisierungen
        self.data['Verteilung'] = 'V_Rechteck'
        self.data['KennwertArt'] = 'K_HalbWeite'
        self.data['Freiheitsgrad'] = 'FG_unbegrenzt'

    def b_val(self):
        # Berechnet den Temperaturunterschied b_Val
        tx = 20.2
        tn = 20

        if tx is None or tn is None:
            return None
        return abs((tx + tn) / 2 - 20)

    def sensititivty_c2(self):
        # Berechnet die Sensitivität C2 basierend auf den Ausdehnungskoeffizienten
        ax = 0.000015
        an = 0.000015

        if ax is None or an is None:
            return None
        return abs(ax - an) / (2 * math.sqrt(3))