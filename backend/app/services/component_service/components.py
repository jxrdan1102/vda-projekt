import math


__all__ = ["KomponenteA", "KomponenteB"]

from app.services.component_service.component_abstract import TMU_Komponente

from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec

MU_NAN = math.nan
class KomponenteA(TMU_Komponente):
    def __init__(self, modell, const_list):
        super().__init__(modell, 12, const_list,"notthere")
        # Konstruktoraufruf der Basisklasse (wir simulieren diesen in Python)
        self.modell = modell
        self.const_list = const_list
        self.archiv = False  # Beispielwert für Archivstatus
        self.data = TMuKompRec(0.15,MU_NAN,'V_Rechteck','K_HalbWeite','FG_unbegrenzt',0,1)
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

class KomponenteB(TMU_Komponente):
    def __init__(self):
        super().__init__("Komponente B", 2.5)

    def special_function(self):
        return f"{self.name}: Spezialfunktion von B!"