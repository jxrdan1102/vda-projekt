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
                    return max(0, self.messpunkt_anzahl - self.mindest_punkt_anzahl())
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

    def mindest_punkt_anzahl(self):
        try:
            return 2
        except Exception as e:
            print(f"Fehler in mindest_punkt_anzahl: {e}")
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
            return faktor * math.sqrt(4 / n)
        else:
            return MU_NAN

    def g_val(self) -> float:
        Phi = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_alpha]
        if Phi == 0 or math.isnan(Phi):
            Phi = 360
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

