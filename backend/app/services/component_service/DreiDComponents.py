import math
from enum import Enum
from functools import cached_property
from math import pi, sqrt

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import MU_NAN
from app.services.component_service.componente3D import TMU_3DKomponente


class TMU_3DAufgabe(Enum):
    aDurchmesser = 1
    aAbstand = 2
    aRichtung = 3
    aKoaxialitaet = 4
    aForm = 5
    aWinkel = 6
    aPosition = 7

class TMU_3dKomponente_Richtung(TMU_3DKomponente):
    def __init__(self, modell, komp_id, const_list, formel):
        super().__init__(modell, komp_id, const_list, formel)

    @cached_property
    def unsicherheitsbeitrag(self):
        try:
            result = MU_NAN
            print("wildinn'", self.anzahl_messungen)

            if self.archiv:
                result = self.ArchData.UNSB
            else:
                ux = MU_NAN
                if self.c1_val != MU_NAN:
                    if self.data.KennwertArt.name == "M3D_MethodeA":
                        ux = self.standard_unsicherheit
                    else:
                        A = 1
                        si = self.standard_unsicherheit_su()
                        if si != MU_NAN:
                            ux = si
                        elif A != MU_NAN:
                            ux = A / 3
                if ux != MU_NAN and self.b_val != MU_NAN and self.c1_val != MU_NAN:
                    result = ux * self.b_val() * self.sensititivty_c1()
            return result
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def unsicherheitsbeitrag_alternative(self):
        return self.unsicherheitsbeitrag()

    @property
    def effektiver_freiheitsgrad(self):
        try:
            result = MU_NAN

            if self.archiv:
                result = self.ArchData.FreiEff
            else:
                if self.data.KennwertArt.name == "M3D_MethodeB":
                    result = self.messpunkt_anzahl - 1
                else:
                    result = self.anzahl_messungen * (self.messpunkt_anzahl - 2)
            if result != MU_NAN:
                result = abs(result)
            return result
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN


def in_grad(bogen: float) -> float:
    try:
        return bogen * (180 / pi)
    except Exception as e:
        print(f"Fehler in in_grad: {e}")
        return MU_NAN


class TK_3d_ResKMG(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1378, const_list, "&Delta;I<sub>KMG;R</sub>")
        self.lfdnr = lfdnr
        self.einheit = "µm"
        self.einheit_ergebnis = "µm"
        self.dez = 5
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_AUFLOES"],]
        self.fields_to_edit = []
        self.id: int
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.messpunkt_anzahl = None
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1
            return 1.0
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return 1.0

    def b_val(self) -> float:
        return 1.0

    def standard_unsicherheit_su(self) -> float:
        try:
            i = 2
            if i != MU_NAN:
                return i / (3**0.5)
            return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN


class TK_3d_Wi_WE(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1379, const_list, "W<sub>E</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LME"], TKompConstants["TC_3d_Ri_LE"],]
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.messpunkt_anzahl = None
        self.id: int
        self.data = TMuKompRec(
            TermL0=0.0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.addConstNeededToModell()

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval
            result = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.modell.Element1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                    result = 1.0
            elif self.messpunkt_anzahl > 0:
                if self.modell.Element1 in ["Gerade", "Ebene"]:
                    if self.modell.punktmuster == 1:
                        result = sqrt((12 * (4 - 1)) / (4 * (4 + 1)))
                    elif self.modell.punktmuster == 2:
                        result = sqrt(4 / 4)
                    elif self.modell.punktmuster == 3:
                        result = sqrt(8 / self.messpunkt_anzahl)

                elif self.modell.Element1 in ["Zylinder", "Kegel"]:
                    if self.modell.punktmuster == 1:
                        result = sqrt(
                            (24 * (self.messpunkt_anzahl - 1))
                            / (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1))
                        )
                    elif self.modell.punktmuster == 2:
                        result = sqrt(8 / self.messpunkt_anzahl)
            return result
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval

            sab = MU_NAN
            lme = 2

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.data.TermL0 != 0:
                    sab = self.data.TermL0
            else:
                if self.data.TermL0 != 0:
                    sab = self.data.TermL0
                else:
                    a = 1
                    if a != MU_NAN:
                        sab = a / 3.0
            if sab != MU_NAN and lme != MU_NAN and lme != 0:
                result = (3 * sab * 0.001) / lme
                return result / sqrt(3)
            return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            if self.modell.Element1 not in ["Punkt", "Kreis"]:
                lme = 2
                le = 2
                if le != MU_NAN and lme != MU_NAN and lme != 0:
                    return in_grad(le / lme)
            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

class TK_3d_Wi_WB(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1380, const_list, "&Delta;I<sub>KMG;R</sub>")
        self.lfdnr = lfdnr
        self.id: int
        self.archiv = None
        self.modell = modell
        self.messpunkt_anzahl = None
        self.lmb = 2
        self.lb = 2
        self.a = 1
        self.c1_val = 1
        self.result = None
        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LMB"], TKompConstants["TC_3d_Koax_LB"], TKompConstants["TC_3d_KMG_A"],]
        self.MU_NAN = float("nan")
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.addConstNeededToModell()

    def in_grad(self, bog: float) -> float:
        try:
            return bog * (180 / math.pi)
        except Exception as e:
            print(f"Fehler in in_grad: {e}")
            return self.MU_NAN

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_sens_c1()
            else:
                if self.modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                    if self.lmb is not None and self.lb is not None and self.lmb != 0:
                        return self.in_grad(self.lb / self.lmb)
            return self.MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return self.MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_bval()
            else:
                if self.sensititivty_c1() != self.MU_NAN:
                    if self.data.KennwertArt.name == "M3D_MethodeA":
                        if self.modell.Element1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                            return 1
                    else:
                        if self.messpunkt_anzahl > 1:
                            if self.modell.Element1 in ["Gerade", "Ebene"]:
                                if self.modell.Bezug1 in ["Punkt", "NDEF"]:
                                    return math.sqrt(
                                        (12 * (self.messpunkt_anzahl - 1))
                                        / (
                                            self.messpunkt_anzahl
                                            * (self.messpunkt_anzahl + 1)
                                        )
                                    )
                                elif self.modell.Bezug1 == "Gerade":
                                    return math.sqrt(4 / self.messpunkt_anzahl)
                                elif self.modell.Bezug1 == "Ebene":
                                    return math.sqrt(8 / self.messpunkt_anzahl)
                            elif self.modell.Element1 in ["Zylinder", "Kegel"]:
                                if self.modell.Bezug1 in ["Punkt", "Kegel"]:
                                    return math.sqrt(
                                        (24 * (self.messpunkt_anzahl - 1))
                                        / (
                                            self.messpunkt_anzahl
                                            * (self.messpunkt_anzahl + 1)
                                        )
                                    )
                                elif self.modell.Bezug1 == "Gerade":
                                    return math.sqrt(8 / self.messpunkt_anzahl)
            return self.MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return self.MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_aval()
            else:
                sab = self.MU_NAN
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    if self.data.TermL0 != 0:
                        sab = self.data.TermL0
                else:
                    if self.data.TermL0 != 0:
                        sab = self.data.TermL0
                    else:
                        if self.a is not None:
                            sab = self.a / 3

                if sab != self.MU_NAN and self.lmb != self.MU_NAN and self.lmb != 0:
                    result = (3 * sab * 0.001) / self.lmb
                    if result != self.MU_NAN:
                        return result / math.sqrt(3)
            return self.MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return self.MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_frei_eff()
            else:
                if self.data.KennwertArt.name == "M3D_MethodeB":
                    return max(0, self.messpunkt_anzahl - 1)
                else:
                    return max(0, self.messpunkt_anzahl - self.mindestpunkt_anzahl())
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return self.MU_NAN

    def archiv_data_sens_c1(self):
        try:
            return 1.0
        except Exception as e:
            print(f"Fehler in archiv_data_sens_c1: {e}")
            return 1.0

    def archiv_data_bval(self):
        try:
            return 1.0
        except Exception as e:
            print(f"Fehler in archiv_data_bval: {e}")
            return 1.0

    def archiv_data_aval(self):
        try:
            return 1.0
        except Exception as e:
            print(f"Fehler in archiv_data_aval: {e}")
            return 1.0

    def archiv_data_frei_eff(self):
        try:
            return 1.0
        except Exception as e:
            print(f"Fehler in archiv_data_frei_eff: {e}")
            return 1.0

    def mindestpunkt_anzahl(self):
        try:
            return 2
        except Exception as e:
            print(f"Fehler in mindestpunkt_anzahl: {e}")
            return 2

class TK_3d_Wi_DeltaEKMG(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1381, const_list, "&Delta;I<sub>KMG;R</sub>")
        self.messpunkt_anzahl = None
        self.archiv = None
        self.lfdnr = lfdnr
        self.id: int
        self.k = 1
        self.alpha = 2
        self.le = 2
        self.lb = 2
        self.MU_NAN = float("nan")
        self.c1_val = 1
        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_K"],
            TKompConstants["TC_3d_Ri_LE"],
            TKompConstants["TC_3d_Ri_LME"],
            TKompConstants["TC_3d_Koax_LB"],
            TKompConstants["TC_3d_Ri_Alpha"],
        ]
        self.result = None
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.addConstNeededToModell()

    def in_grad(self, bog: float) -> float:
        return bog * (180 / math.pi)

    def in_rad(self, grad: float) -> float:
        return grad * (math.pi / 180)

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_sens_c1()
            if self.le and self.lb and self.lb != 0:
                return self.in_grad(self.le / self.lb)
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
        return self.MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_aval()
            if self.k and self.k != 0:
                rad = self.in_rad(self.alpha)
                sin_sq = math.sin(rad) ** 2
                result = ((2 * 0.001) / self.k) * sin_sq
                return result / (2 * math.sqrt(3))
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
        return self.MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.archiv_data_bval()
            return 1
        except Exception as e:
            print(f"Fehler in b_val: {e}")
        return self.MU_NAN

    def archiv_data_sens_c1(self):
        return 1.0

    def archiv_data_aval(self):
        return 1.0

    def archiv_data_bval(self):
        return 1.0

    MU_NAN = float('nan')

class TK_3d_Dw(TMU_3DKomponente):
    def __init__(self, modell, const_list,lfdnr):
        super().__init__(modell, 1301, const_list, "D<sub>W</sub>")
        self.fields_to_edit = ['EF_Term0', 'EF_Kennwertart', 'EF_MPAnzahl']
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        if self.modell.Element1 != 4:  # Annahme: Vergleich als String oder Enum
            self.ConstNeeded += [TKompConstants['TC_3d_KMG_A'],TKompConstants['TC_3d_DUME_alpha']]
        else:
            self.ConstNeeded += [TKompConstants['TC_3d_KMG_A']]
        self.addConstNeededToModell()

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL

        Element = self.modell.Element1
        n = self.messpunkt_anzahl
        faktor = MU_NAN

        if self.data.KennwertArt.name == 'M3D_MethodeA':
            if Element in ['Kreis', 'Halbkugel', 'Zylinder']:
                faktor = 1
        else:
            if n is not None and n > 3:
                if Element in ['Kreis', 'Zylinder']:
                    faktor = 1
                elif Element == 'Halbkugel':
                    if n in [4,5,6]:
                        faktor = 1
                    elif n > 6:
                        faktor = 1.5

        if n is not None and n > 0 and not math.isnan(faktor):
            print(faktor * math.sqrt(4 / n))
            return faktor * math.sqrt(4 / n)
        else:
            return MU_NAN

    def g_val(self) -> float:
        Phi = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_alpha]
        if Phi == 0 or math.isnan(Phi):
            Phi = 360
        print("Phi:",20631 * (Phi ** -1.6878))
        return 20631 * (Phi ** -1.6878)

    def EffektiverFreiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt.name == 'M3D_MethodeB':
            return self.messpunkt_anzahl - 1

        return self.anzahl_messungen * abs(
            self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1)
        )


class TK_3dA_DeltaDT(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1320, const_list, "&Delta;D<sub>T</sub>")
        self.fields_to_edit = ['EF_Term0', 'EF_Kennwertart', 'EF_MPAnzahl']
        self.ConstNeeded += []
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.addConstNeededToModell()

        self.lfdnr = lfdnr
    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        else:
            result = 1.0

            el1 = self.modell.Element1
            el2 = self.modell.Element2
            taster_anzahl = self.modell.taster #aufpassen

            if taster_anzahl == 2:
                if el1 in ['Punkt', 'Gerade', 'Ebene'] and el2 in ['Punkt', 'Gerade', 'Ebene']:
                    result = 0.5
            elif taster_anzahl == 1:
                if el1 in ['Punkt', 'Gerade', 'Ebene'] and el2 in ['Halbkugel', 'Zylinder', 'Kegel']:
                    result = 0.5

            return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL

        faktor = MU_NAN
        n = self.messpunkt_anzahl

        if self.data.KennwertArt.name == 'M3D_MethodeA':
            faktor = 1
        elif n is not None and n >= 4:
            if n in [4, 5, 6]:
                faktor = 1
            else:
                faktor = 1.5

        if n is not None and n > 0 and not math.isnan(faktor):
            return faktor * math.sqrt(4 / n)
        return MU_NAN

    def EffektiverFreiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        n = self.messpunkt_anzahl

        if self.data.KennwertArt.name == 'M3D_MethodeB':
            result = n - 1
        else:
            result = self.anzahl_messungen * (n - 4)

        if not math.isnan(result):
            return abs(result)
        return MU_NAN

class TK_3d_DeltaDC(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1303, const_list, "&Delta;D<sub>C</sub>")
        self.fields_to_edit = []
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_Uc"]]
        self.result = None  # optional, falls Ergebnis gecached wird
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.addConstNeededToModell()

        self.lfdnr = lfdnr
    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                uc = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_Uc]
                if not math.isnan(uc):
                    return uc / 2
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (DeltaDC): {e}")
        return MU_NAN



class TK_3d_DeltaLkmg(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1304, const_list, "&Delta;L<sub>KMG</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        self.ConstNeeded += [
            TKompConstants["TC_3D_NennLaenge_LD"],
            TKompConstants["TC_3d_KMG_K"]
        ]

        if self.modell.element in [3, 6]:
            self.ConstNeeded += [TKompConstants["TC_3d_DUME_L"]]
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                d = self.modell.const_list.const_map[TKompConstants.TC_3D_NennLaenge_LD]
                k = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]

                if not math.isnan(d) and not math.isnan(k) and k != 0:
                    return d / k
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (DeltaLkmg): {e}")
        return MU_NAN

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        return 0.5


class TK_3dA_LalphaM(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1323, const_list, "&Delta;L<sub>&alpha;M</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)


        aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
        if aufgabe == "aDurchmesser":
            self.ConstNeeded += [TKompConstants["TC_3D_NennLaenge_LD"]]
        elif aufgabe == "aAbstand":
            self.ConstNeeded += [TKompConstants["TC_3d_ABST_L"]]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_alphaM"],
            TKompConstants["TC_3d_KMG_Tm"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.SensC1
            else:
                aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
                d = None
                if aufgabe == "aDurchmesser":
                    d = self.modell.const_list.const_map[TKompConstants.TC_3D_NennLaenge_LD]
                elif aufgabe == "aAbstand":
                    d = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_L]

                tm = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_Tm]

                if not math.isnan(d) and not math.isnan(tm):
                    return abs(1000 * d * (tm - 20))
        except Exception as e:
            print(f"Fehler in sensitivity_c1 (LalphaM): {e}")
        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                alpha_m = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_alphaM]
                if not math.isnan(alpha_m):
                    return alpha_m * 10**-6 / (5 * math.sqrt(3))
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (LalphaM): {e}")
        return MU_NAN


class TK_3dA_LalphaW(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1324, const_list, "&Delta;L<sub>&alpha;W</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
        if aufgabe == "aDurchmesser":
            self.ConstNeeded += [TKompConstants["TC_3D_NennLaenge_LD"]]
        elif aufgabe == "aAbstand":
            self.ConstNeeded += [TKompConstants["TC_3d_ABST_L"]]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_Tw"],
            TKompConstants["TC_3d_KMG_alphaW"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.SensC1
            else:
                aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
                d = None
                if aufgabe == "aDurchmesser":
                    d = self.modell.const_list.const_map[TKompConstants.TC_3D_NennLaenge_LD]
                elif aufgabe == "aAbstand":
                    d = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_L]

                tw = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_Tw]

                if not math.isnan(d) and not math.isnan(tw):
                    return abs(1000 * d * (tw - 20))
        except Exception as e:
            print(f"Fehler in sensitivity_c1 (LalphaW): {e}")
        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                alpha_w = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_alphaW]
                if not math.isnan(alpha_w):
                    return alpha_w * 1e-6 / (5 * math.sqrt(3))
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (LalphaW): {e}")
        return MU_NAN


class TK_3dA_LtM(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1325, const_list, "&Delta;L<sub>tM</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
        if aufgabe == "aDurchmesser":
            self.ConstNeeded += [TKompConstants["TC_3D_NennLaenge_LD"]]
        elif aufgabe == "aAbstand":
            self.ConstNeeded += [TKompConstants["TC_3d_ABST_L"]]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_alphaM"],
            TKompConstants["TC_3d_KMG_deltaTm"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.SensC1
            else:
                aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
                d = None
                if aufgabe == "aDurchmesser":
                    d = self.modell.const_list.const_map[TKompConstants.TC_3D_NennLaenge_LD]
                elif aufgabe == "aAbstand":
                    d = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_L]

                alpha_m = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_alphaM]

                if not math.isnan(d) and not math.isnan(alpha_m):
                    return abs(1000 * d * (alpha_m * 1e-6))
        except Exception as e:
            print(f"Fehler in sensitivity_c1 (LtM): {e}")
        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                delta_tm = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_deltaTm]
                if not math.isnan(delta_tm):
                    return delta_tm / math.sqrt(3)
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (LtM): {e}")
        return MU_NAN


class TK_3dA_LtW(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1326, const_list, "&Delta;L<sub>tW</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
        if aufgabe == "aDurchmesser":
            self.ConstNeeded += [TKompConstants["TC_3D_NennLaenge_LD"]]
        elif aufgabe == "aAbstand":
            self.ConstNeeded += [TKompConstants["TC_3d_ABST_L"]]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_alphaW"],
            TKompConstants["TC_3d_KMG_deltaTw"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.SensC1
            else:
                aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
                d = (
                    self.modell.const_list.const_map[TKompConstants.TC_3D_NennLaenge_LD]
                    if aufgabe == "aDurchmesser"
                    else self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_L]
                )
                alpha_w = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_alphaW]

                if not math.isnan(d) and not math.isnan(alpha_w):
                    return abs(1000 * d * (alpha_w * 1e-6))
        except Exception as e:
            print(f"Fehler in sensitivity_c1 (LtW): {e}")
        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            else:
                delta_tw = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_deltaTw]
                if not math.isnan(delta_tw):
                    return abs(delta_tw / math.sqrt(3))
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (LtW): {e}")
        return MU_NAN


class TK_3d_Delta_L_t(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1377, const_list, "&Delta;L<sub>t</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        aufgabe = TMU_3DAufgabe(modell.aufgabe).name
        if aufgabe == "aDurchmesser":
            self.ConstNeeded += [TKompConstants["TC_3D_NennLaenge_LD"]]
        elif aufgabe == "aAbstand":
            self.ConstNeeded += [TKompConstants["TC_3d_ABST_L"]]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_alphaW"],
            TKompConstants["TC_3d_KMG_alphaM"],
            TKompConstants["TC_3d_KMG_Tw"],
            TKompConstants["TC_3d_KMG_Tm"]
        ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.SensC1
            else:
                aufgabe = TMU_3DAufgabe(self.modell.aufgabe).name
                d = (
                    self.modell.const_list.const_map[TKompConstants.TC_3D_NennLaenge_LD]
                    if aufgabe == "aDurchmesser"
                    else self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_L]
                )
                if not math.isnan(d):
                    return abs(1000 * d * math.sqrt(2))  # Änderung vom 25.02.2013
        except Exception as e:
            print(f"Fehler in sensitivity_c1 (Delta_L_t): {e}")
        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL

            alpha_w = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_alphaW]
            alpha_m = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_alphaM]
            temp_w = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_Tw]
            temp_m = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_Tm]

            if all(not math.isnan(x) for x in [alpha_w, alpha_m, temp_w, temp_m]):
                alpha_w *= 1e-6
                alpha_m *= 1e-6

                alpha = (alpha_w + alpha_m) / 2
                delta_alpha = (alpha_w - alpha_m) / 2
                alpha_max = max(alpha_w, alpha_m)

                theta_w = temp_w - 20
                theta_m = temp_m - 20
                theta = (theta_w + theta_m) / 2
                delta_theta = (theta_w - theta_m) / 2
                theta_max = max(abs(theta_w), abs(theta_m))

                u_theta_max = theta_max / math.sqrt(3)
                u_alpha_max = max(alpha_w / 5, alpha_m / 5)

                result = math.sqrt(
                    (alpha**2 + delta_alpha**2) * u_theta_max**2 +
                    (theta**2 + delta_theta**2) * u_alpha_max**2
                )
                return result
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (Delta_L_t): {e}")
        return MU_NAN



class TK_3dA_DeltaLKMG(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1322, const_list, "&Delta;L<sub>KMG</sub>")
        self.fields_to_edit = []
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.lfdnr = lfdnr
        self.ConstNeeded += [TKompConstants["TC_3d_ABST_L"], TKompConstants["TC_3d_KMG_K"]]
        self.addConstNeededToModell()


    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        else:
            return 0.5

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval
        l = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_L]
        k = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]

        if not math.isnan(l) and not math.isnan(k) and k != 0:
            return l / k

        return float('nan')



class TK_3dA_X1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1312, const_list, "X<sub>E</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        if modell.Element1 in [
            "Kreis", "Halbkugel", "Zylinder", "Kegel"
        ]:
            self.ConstNeeded.append(TKompConstants["TC_3d_DUME_alpha"])
            self.addConstNeededToModell()

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        result = float("nan")
        e = self.modell.Element1
        if e in ["Punkt", "Gerade", "Ebene", "Kreis", "Halbkugel", "Zylinder", "Kegel"]:
            mpa = self.mindestpunkt_anzahl(e)
            if self.messpunkt_anzahl >= mpa:
                if e == "Halbkugel":
                    if self.modell.antastung_taster1 == 2:
                        if self.messpunkt_anzahl == 5:
                            result = 1.12 * math.sqrt(2 / self.messpunkt_anzahl)
                        elif self.messpunkt_anzahl == 6:
                            result = 0.87 * math.sqrt(2 / self.messpunkt_anzahl)
                        elif self.messpunkt_anzahl > 6:
                            result = 1.8 * math.sqrt(2 / self.messpunkt_anzahl)
                    elif self.modell.antastung_taster1 == 1:
                        if self.messpunkt_anzahl in [5, 6]:
                            result = 0.71 * math.sqrt(2 / self.messpunkt_anzahl)
                        elif self.messpunkt_anzahl > 6:
                            result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl)
                else:
                    if e in ["Punkt", "Gerade", "Ebene"]:
                        result = math.sqrt(1 / self.messpunkt_anzahl)
                    elif e in ["Kreis", "Zylinder", "Kegel"]:
                        result = math.sqrt(2 / self.messpunkt_anzahl)
        return result

    def g_val(self) -> float:
        phi = self.modell.const_list.const_map.get(TKompConstants["TC_3d_DUME_alpha"], math.nan)
        if math.isnan(phi) or phi == 0:
            phi = 360

        result = float("nan")
        e = self.modell.Element1

        if e in ["Punkt", "Gerade", "Ebene", "Kreis", "Halbkugel", "Zylinder", "Kegel"]:
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if e in ["Punkt", "Gerade", "Ebene"]:
                    result = 1
                elif e in ["Halbkugel", "Kreis", "Zylinder", "Kegel"]:
                    result = 20631 * pow(phi, -1.6878)
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                mpa = self.mindestpunkt_anzahl(e)
                if self.messpunkt_anzahl >= mpa:
                    if e == "Halbkugel":
                        if self.modell.antastung_taster1 in [1, 2]:
                            if self.messpunkt_anzahl in [4, 5, 6]:
                                result = 1
                            elif self.messpunkt_anzahl > 6:
                                result = (
                                    20631 * pow(phi, -1.6878)
                                    if not math.isnan(phi)
                                    else float("nan")
                                )
                    else:
                        if e in ["Punkt", "Gerade", "Ebene"]:
                            result = 1
                        elif e in ["Kreis", "Zylinder", "Kegel"]:
                            result = (
                                20631 * pow(phi, -1.6878)
                                if not math.isnan(phi)
                                else float("nan")
                            )
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            result = self.arch_data.frei_eff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
                result = self.messpunkt_anzahl - 1
            else:
                result = self.anzahl_messungen * (
                    self.messpunkt_anzahl
                    - self.mindestpunkt_anzahl(self.modell.Element1)
                )
        return abs(result) if not math.isnan(result) else result




class TK_3dA_W1(TMU_3DKomponente):
    def __init__(self, modell, const_list ,lfdnr):
        super().__init__(modell, 1313, const_list, "W<sub>E</sub>")
        if modell.abstand != 2:
            self.ConstNeeded += [
                TKompConstants["TC_3d_ABST_LM1"],
                TKompConstants["TC_3d_ABST_LE1"]
            ]
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)

        self.lfdnr = lfdnr
        self.fields_to_edit = []
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sensc1

        if self.modell.abstand == 2:
            return 0

        lme = self.modell.const_list.const_map(TKompConstants["TC_3d_ABST_LM1"])
        lse = self.modell.const_list.const_map(TKompConstants["TC_3d_ABST_LE1"])

        if not math.isnan(lme) and not math.isnan(lse) and lme != 0:
            return lse / lme

        return float("nan")

    @property
    def messpunkt_anzahl(self) -> int:
        if not math.isnan(self.sensititivty_c1()):
            x1_komp = self.modell.find_komponente_by_id(1312)
            if x1_komp is not None:
                return x1_komp.messpunkt_anzahl
        return 0

    @property
    def anzahl_messungen(self) -> int:
        if not math.isnan(self.sensititivty_c1()):
            x1_komp = self.modell.find_komponente_by_id(1312)
            if x1_komp is not None:
                return x1_komp.anzahl_messungen
        return 0

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        if math.isnan(self.sensititivty_c1()):
            return float("nan")

        if self.data.KennwertArt.name == "M3D_MethodeA":
            return 1

        result = 0.0
        n = self.messpunkt_anzahl
        if n == 0:
            return result

        e = self.modell.Element1
        winkel = self.modell.winkelE1

        if e in ["Gerade", "Ebene"]:
            if winkel == 2:
                result = math.sqrt(4 / n)
            elif winkel == 1:
                result = math.sqrt((12 * (n - 1)) / (n * (n + 1)))
            elif e == "Ebene" and winkel == 3:
                result = math.sqrt(8 / n)

        if e == "Zylinder":
            if winkel == 2:
                result = math.sqrt(8 / n)
            elif winkel == 1:
                result = math.sqrt((24 * (n - 1)) / (n * (n + 1)))

        return result

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval

        if not math.isnan(self.sensititivty_c1()):
            x1_komp = self.modell.find_komponente_by_id(1312)
            if x1_komp is not None:
                return x1_komp.standard_unsicherheit_su()

        return float("nan")

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return abs(self.arch_data.frei_eff)

        if self.data.KennwertArt.name == "M3D_MethodeB":
            return abs(self.messpunkt_anzahl - 1)

        n = self.messpunkt_anzahl
        m = self.anzahl_messungen
        mpa = self.mindestpunkt_anzahl(self.modell.Element1)
        return abs(m * (n - mpa))



class TK_3dA_DeltaXT1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1314, const_list, "ΔX<sub>TE</sub>")
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.fields_to_edit = []
        self.addConstNeededToModell()


    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititivty_c1() != MU_NAN:
            n = self.messpunkt_anzahl
            if n >= 3:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    return 1
                else:
                    if self.modell.tasterschaft1 == 2:
                        # Taster 1/E Schaft parallel
                        if n == 5:
                            return 1.12
                        elif n == 6:
                            return 0.87
                        else:
                            return 1.8
                    elif self.modell.tasterschaft1 == 1:
                        # Taster 1/E Schaft senkrecht
                        if n in (5, 6):
                            return 0.71
                        else:
                            return 1.3
        return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = self.messpunkt_anzahl - 1
        else:
            result = self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1))

        if result != MU_NAN:
            return abs(result)
        return MU_NAN




class TK_3dA_DeltaRT1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1315,const_list, "ΔD<sub>EE</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.fields_to_edit = []
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sens_c1
        else:
            if self.modell.taster == 1:
                if self.modell.Element1 in ("Punkt", "Gerade", "Ebene"):
                    if self.modell.Element2 in ("Punkt", "Gerade", "Ebene"):
                        return 1.0
                    else:
                        return 0.5
            elif self.modell.taster == 2:
                if self.modell.Element1 in ("Punkt", "Gerade", "Ebene"):
                    return 0.5
            return 0.0


    @property
    def messpunkt_anzahl(self) -> int:
        xt1 = self.modell.find_component_by_id(1314)
        return xt1.messpunkt_anzahl if xt1 else 0

    @property
    def anzahl_messungen(self) -> int:
        xt1 = self.modell.find_component_by_id(1314)
        return xt1.anzahl_messungen if xt1 else 0

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval
        xt1 = self.modell.find_component_by_id(1314)
        return xt1.standard_unsicherheit_su() if xt1 else MU_NAN

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        else:
            if self.data.kennwert_art == "methode_a":
                return 1.0
            elif self.messpunkt_anzahl >= 5:
                return 1.0
            else:
                return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.frei_eff
        else:
            if self.data.kennwert_art == "methode_b":
                val = self.messpunkt_anzahl - 1
            else:
                val = self.anzahl_messungen * (self.messpunkt_anzahl - 4)
            return abs(val) if val != MU_NAN else MU_NAN



class TK_3dA_X2(TMU_3DKomponente):
    def __init__(self, modell, const_list ,lfdnr):
        super().__init__(modell, 1316, const_list, "X<sub>B</sub>")
        self.fields_to_edit = ["Term0", "Kennwertart", "MPAnzahl"]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15, TermL1=0, Verteilung="V_Rechteck", KennwertArt="M3D_MethodeB",
                               Freiheitsgrad="FG_unbegrenzt", FreiN_minus_1=0, Flags=1, )
        if self.modell.Element2 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_DUME_alpha"]]
        self.addConstNeededToModell()

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        if self.modell.Element2 in {"Punkt", "Gerade", "Ebene", "Kreis", "Zylinder", "Kegel", "Halbkugel"}:
            mpa = self.modell.mindestpunkt_anzahl(self.modell.Element2)
            if self.messpunkt_anzahl >= mpa:
                if self.modell.Element2 == "Halbkugel":
                    if self.modell.tasterschaft2 == 2:  # Schaft parallel
                        match self.messpunkt_anzahl:
                            case 4:
                                return MU_NAN
                            case 5:
                                return 1.12 * math.sqrt(2 / self.messpunkt_anzahl)
                            case 6:
                                return 0.87 * math.sqrt(2 / self.messpunkt_anzahl)
                            case _:
                                return 1.8 * math.sqrt(2 / self.messpunkt_anzahl)
                    elif self.modell.tasterschaft2 == 1:
                        match self.messpunkt_anzahl:
                            case 5 | 6:
                                return 0.71 * math.sqrt(2 / self.messpunkt_anzahl)
                            case _:
                                return 1.3 * math.sqrt(2 / self.messpunkt_anzahl)
                else:
                    if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                        return math.sqrt(1 / self.messpunkt_anzahl)
                    elif self.modell.Element2 in {"Kreis", "Zylinder", "Kegel"}:
                        return math.sqrt(2 / self.messpunkt_anzahl)
        return MU_NAN

    def g_val(self) -> float:
        phi = self.modell.const_list.const_map(TKompConstants["TC_3d_DUME_alpha"])
        if phi == 0 or phi == MU_NAN:
            phi = 360

        if self.modell.Element2 in {"Punkt", "Gerade", "Ebene", "Kreis", "Zylinder", "Kegel", "Halbkugel"}:
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                    return 1.0
                elif self.modell.Element2 in {"Halbkugel", "Kreis", "Zylinder", "Kegel"}:
                    return 20631 * phi**-1.6878 if phi != MU_NAN else MU_NAN
            else:
                mpa = self.modell.mindestpunkt_anzahl(self.modell.Element2_3D)
                if self.messpunkt_anzahl >= mpa:
                    if self.modell.tasterschaft2 == 2:
                        if self.messpunkt_anzahl in {4, 5, 6}:
                            return 1.0
                        else:
                            return 20631 * phi**-1.6878 if phi != MU_NAN else MU_NAN
                    elif self.modell.methode_3d_antastung_taster2 == 1:
                        if self.messpunkt_anzahl in {5, 6}:
                            return 1.0
                        else:
                            return 20631 * phi**-1.6878 if phi != MU_NAN else MU_NAN
        return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.frei_eff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
                val = self.messpunkt_anzahl - 1
            else:
                val = self.anzahl_messungen * abs(self.messpunkt_anzahl - self.modell.mindestpunkt_anzahl(self.modell.Element1_3D))
            return abs(val) if val != MU_NAN else MU_NAN



class TK_3dA_W2(TMU_3DKomponente):
    def __init__(self, modell, const_list ,lfdnr):
        super().__init__(modell, 1317, const_list, "W<sub>B</sub>")
        self.ConstNeeded += [TKompConstants["TC_3d_ABST_LM2"], TKompConstants["TC_3d_ABST_LE2"]]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.fields_to_edit = []
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sens_c1
        if (self.modell.abstand == 1 and
            self.modell.Element2 in {"Gerade", "Ebene", "Zylinder", "Kegel"}):
            lm2 = self.modell.const_list.const_map(TKompConstants["TC_3d_ABST_LM2"])
            le2 = self.modell.const_list.const_map(TKompConstants["TC_3d_ABST_LE2"])
            if lm2 != MU_NAN and le2 != MU_NAN and lm2 != 0:
                return le2 / lm2
        return MU_NAN

    @property
    def messpunkt_anzahl(self) -> int:
        x2 = self.modell.find_komponente_by_id(1316)  # ID von X2
        return x2.messpunkt_anzahl if x2 else 0

    @property
    def anzahl_messungen(self) -> int:
        x2 = self.modell.find_komponente_by_id(1316)
        return x2.anzahl_messungen if x2 else 0

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        c1 = self.sensititivty_c1()
        if c1 == MU_NAN:
            return MU_NAN

        if self.data.KennwertArt.name == "M3D_MethodeA":
            return 1.0
        else:
            n = self.messpunkt_anzahl
            if n <= 0:
                return MU_NAN

            e = self.modell.Element2
            winkel = self.modell.winkelE2

            if e in {"Gerade", "Ebene"}:
                if winkel == 2:  # Messpunkte an den Enden
                    return math.sqrt(4 / n)
                elif winkel == 1:  # Gleichmäßig verteilt
                    return math.sqrt((12 * (n - 1)) / (n * (n + 1)))
            if e == "Ebene" and winkel == 3:  # kreisförmig
                return math.sqrt(8 / n)
            if e == "Zylinder":
                if winkel == 2:  # 2 Radialschnitte mit je n/2 Punkten
                    return math.sqrt(8 / n)
                elif winkel == 1:
                    return math.sqrt((24 * (n - 1)) / (n * (n + 1)))

        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval

        if self.sensititivty_c1() != MU_NAN:
            x2 = self.modell.find_komponente_by_id(1316)
            if x2:
                return x2.standard_unsicherheit_su()
        return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.frei_eff

        if self.data.KennwertArt.name == "M3D_MethodeB":
            return abs(self.messpunkt_anzahl - 1)

        e = self.modell.Element2
        n = self.messpunkt_anzahl
        m = self.anzahl_messungen

        if e == "Punkt":
            return m * abs(n - 1)
        elif e == "Gerade":
            return m * abs(n - 2)
        elif e == "Ebene":
            return m * abs(n - 3)

        return 0.0





class TK_3dA_DeltaXT2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__( modell, 1318, const_list, 'ΔX<sub>TB</sub>')
        self.fields_to_edit = ['Term0', 'Kennwertart', 'MPAnzahl']
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.addConstNeededToModell()

    def b_val(self):
        if self.archiv:
            return self.arch_data.BVAL
        if self.sensititivty_c1() is None:
            return float('nan')

        n = self.messpunkt_anzahl
        if n < 3:
            return float('nan')

        if self.data.KennwertArt.name == "M3D_MethodeA":
            return 1.0
        else:
            taster = self.modell.tasterschaft2
            if taster == 2:  # Schaft parallel
                if n == 5:
                    return 1.12
                elif n == 6:
                    return 0.87
                else:
                    return 1.8
            elif taster == 1:  # Schaft senkrecht
                if n in (5, 6):
                    return 0.71
                else:
                    return 1.3
        return float('nan')

    def effektiver_freiheitsgrad(self):
        if self.archiv:
            return self.arch_data.FreiEff

        n = self.messpunkt_anzahl
        m = self.anzahl_messungen
        if self.data.KennwertArt == "M3D_MethodeB":
            result = n - 1
        elif self.data.KennwertArt == "M3D_MethodeA" and n > 2:
            result = m * (n - 4)
        else:
            result = float('nan')

        return abs(result) if result is not None else float('nan')




class TK_3dA_DeltaRT2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1319, const_list, "ΔD<sub>EB</sub>")
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.fields_to_edit = []
        self.addConstNeededToModell()

    def sensititivty_c1(self):
        if self.archiv:
            return self.arch_data.SensC1

        result = 0.0

        if self.modell.taster1 == 1:
            if self.modell.Element1 in {"Punkt", "Gerade", "Ebene"}:
                if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                    result = 1.0
                else:
                    result = 0.5  # Kreis, Halbkugel, Zylinder, Kegel
        elif self.modell.taster1 == 2:
            if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                result = 0.5  # egal welches toleriertes Element
            # sonst bleibt 0

        return result

    def b_val(self):
        if self.archiv:
            return self.arch_data.BVAL

        if self.data.KennwertArt == "M3D_MethodeA":  # Methode A
            return 1.0
        else:  # Methode B
            if self.messpunkt_anzahl in (5, 6):
                return 1.0
            elif self.messpunkt_anzahl > 6:
                return 1.5
            else:
                return 0.0

    def effektiver_freiheitsgrad(self):
        if self.archiv:
            result = self.arch_data.FreiEff
        else:
            if self.data.KennwertArt == "M3D_MethodeB":  # Methode B
                result = self.messpunkt_anzahl - 1
            else:  # Methode A
                result = self.anzahl_messungen * (self.messpunkt_anzahl - 4)

        if result != MU_NAN:
            return abs(result)
        return result



class TK_3dA_DeltaDC(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1321, const_list, "ΔD<sub>C</sub>")
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_Uc"]]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15, TermL1=0, Verteilung="V_Rechteck", KennwertArt="M3D_MethodeB",
                               Freiheitsgrad="FG_unbegrenzt", FreiN_minus_1=0, Flags=1, )
        self.fields_to_edit = []
        self.addConstNeededToModell()

    def sensititivty_c1(self):
        if self.archiv:
            return self.arch_data.SensC1
        else:
            if self.modell.taster1 == 1:
                return 1.0  # Verwendung desselben Tasters
            else:
                return 0.5  # verschiedene Taster

    def standard_unsicherheit_su(self):
        if self.archiv:
            return self.arch_data.AVAL
        else:
            result = MU_NAN
            if self.sensititivty_c1() != MU_NAN:
                result = self.modell.const_list.const_map(TKompConstants["TC_3d_KMG_Uc"]) / 2.0
            return result



class TK_3dA_DeltaXTR(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1368, const_list, "ΔX<sub>TR</sub>")
        self.fields_to_edit = []
        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_LT"],
            TKompConstants["TC_3D_ABST_LTE"],
            TKompConstants["TC_3D_ABST_LTB"],
            TKompConstants["TC_3d_KMG_MpeML"]
        ]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15, TermL1=0, Verteilung="V_Rechteck", KennwertArt="M3D_MethodeB",
                               Freiheitsgrad="FG_unbegrenzt", FreiN_minus_1=0, Flags=1, )
        self.addConstNeededToModell()

    def ist_zahl(self, x):
        return x is not None and not (isinstance(x, float) and math.isnan(x))

    def standard_unsicherheit_su(self):
        if self.archiv:
            return self.arch_data.AVAL
        else:
            result = MU_NAN
            mpe_ml = self.modell.const_list.const_map(TKompConstants["TC_3d_KMG_MpeML"])
            if mpe_ml != MU_NAN:
                lt = self.modell.const_list.const_map(TKompConstants["TC_3d_KMG_LT"])
                lte = self.modell.const_list.const_map(TKompConstants["TC_3D_ABST_LTE"])
                ltb = self.modell.const_list.const_map(TKompConstants["TC_3D_ABST_LTB"])

                if self.ist_zahl(lte) and self.ist_zahl(ltb) and self.ist_zahl(lt) and lt != 0:
                    result = (lte + ltb) * mpe_ml / (lt * 2.0)

            return result

    def b_val(self):
        if self.archiv:
            return self.arch_data.BVAL
        else:
            return 0.5
