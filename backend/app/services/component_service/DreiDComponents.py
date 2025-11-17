from enum import Enum
from functools import cached_property
from math import pi, sqrt, isnan

import numpy as np
import numpy.linalg as la
from numpy.random import default_rng

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import MU_NAN
from app.services.component_service.componente3D import TMU_3DKomponente
from app.services.component_service.montecarlo_code import mu_position

rng = default_rng(42)

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

            if self.archiv:
                result = self.ArchData.UNSB
            else:
                ux = MU_NAN
                if self.c1_val != MU_NAN:
                    if self.data.KennwertArt.name == "M3D_MethodeA":
                        ux = self.standard_unsicherheit_su()
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
        return self.unsicherheitsbeitrag

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

        if self.modell.Element1 != "Halbkugel":  # Annahme: Vergleich als String oder Enum
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
        try:
            phi = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_alpha]
        except (KeyError, AttributeError):
            phi = float("nan")
        if math.isnan(phi) or phi == 0:
            phi = 360
            print("Phi:",20631 * (phi ** -1.6878))
        return 20631 * (phi ** -1.6878)

    @property
    def effektiver_freiheitsgrad(self) -> float:
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

            if taster_anzahl == 1:
                if el1 in ['Punkt', 'Gerade', 'Ebene'] and el2 in ['Punkt', 'Gerade', 'Ebene']:
                    result = 1
            elif taster_anzahl == 2:
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
        return 1

    @property
    def effektiver_freiheitsgrad(self) -> float:
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

        if self.modell.Element1 in ["Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_DUME_l"]]
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

        if self.modell.Element1 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_DUME_alpha"]]
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
                    if self.modell.tasterschaft1 == 2:
                        if self.messpunkt_anzahl == 5:
                            result = 1.12 * math.sqrt(2 / self.messpunkt_anzahl)
                        elif self.messpunkt_anzahl == 6:
                            result = 0.87 * math.sqrt(2 / self.messpunkt_anzahl)
                        elif self.messpunkt_anzahl > 6:
                            result = 1.8 * math.sqrt(2 / self.messpunkt_anzahl)
                    elif self.modell.tasterschaft1 == 1:
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
        try:
            phi = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_alpha]
        except (KeyError, AttributeError):
            phi = float("nan")
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
                        if self.modell.tasterschaft1 in [1, 2]:
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

    @property
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
        self.setMesspunktAnzahl()
        self.setAnzahlMessungen()

    def setMesspunktAnzahl(self):
        for c in self.modell:
            if c.komp_id in [1312,3989]:
                self.messpunkt_anzahl = c.messpunkt_anzahl

    def setAnzahlMessungen(self):
        for c in self.modell:
            if c.komp_id in [1312,3989]:
                self.anzahl_messungen = c.anzahl_messungen

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sensc1

        if self.modell.abstand == 2:
            return 0

        lme = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_LM1]
        lse = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_LE1]

        if not math.isnan(lme) and not math.isnan(lse) and lme != 0:
            return lse / lme

        return float("nan")


    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        self.setMesspunktAnzahl()
        self.setAnzahlMessungen()
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
            if winkel == 5:
                result = math.sqrt(8 / n)
            elif winkel == 4:
                result = math.sqrt((24 * (n - 1)) / (n * (n + 1)))

        return result

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval

        if not math.isnan(self.sensititivty_c1()):
            x1_komp = self.modell.find_komponente_by_id([1312,3989])
            if x1_komp is not None:
                return x1_komp.standard_unsicherheit_su()

        return float("nan")

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return abs(self.arch_data.frei_eff)
        self.setMesspunktAnzahl()
        self.setAnzahlMessungen()
        print(" Look hier",self.messpunkt_anzahl)
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

    @property
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


    def setMesspunktAnzahl(self):
        for c in self.modell:
            if c.komp_id in [1314,3991]:
                self.messpunkt_anzahl = c.messpunkt_anzahl

    def setAnzahlMessungen(self):
        for c in self.modell:
            if c.komp_id in [1314,3991]:
                self.anzahl_messungen = c.anzahl_messungen

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

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval
        xt1 = self.modell.find_komponente_by_id([1314])
        return xt1.standard_unsicherheit_su() if xt1 else MU_NAN

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        else:
            self.setMesspunktAnzahl()
            self.setAnzahlMessungen()
            if self.data.KennwertArt.name == "M3D_MethodeA":
                return 1.0
            elif self.messpunkt_anzahl >= 5:
                return 1.0
            else:
                return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.frei_eff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
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
                               Freiheitsgrad="FG_unbegrenzt", FreiN_minus_1=0, Flags=1)
        if self.modell.Element2 in ["Kreis", "Halbkugel", "Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_DUME_alpha"]]
        self.addConstNeededToModell()

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        if self.modell.Element2 in {"Punkt", "Gerade", "Ebene", "Kreis", "Zylinder", "Kegel", "Halbkugel"}:
            mpa = self.mindestpunkt_anzahl(self.modell.Element2)
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
        try:
            phi = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_alpha]
        except (KeyError, AttributeError):
            phi = float("nan")
        if phi == 0 or isnan(phi):
            phi = 360

        if self.modell.Element2 in {"Punkt", "Gerade", "Ebene", "Kreis", "Zylinder", "Kegel", "Halbkugel"}:
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                    return 1.0
                elif self.modell.Element2 in {"Halbkugel", "Kreis", "Zylinder", "Kegel"}:
                    return 20631 * phi**-1.6878 if phi != MU_NAN else MU_NAN
            else:
                mpa = self.mindestpunkt_anzahl(self.modell.Element2)
                if self.messpunkt_anzahl >= mpa:
                    if self.modell.tasterschaft2 == 2:
                        if self.messpunkt_anzahl in {4, 5, 6}:
                            return 1.0
                        else:
                            return 20631 * phi**-1.6878 if phi != MU_NAN else MU_NAN
                    elif self.modell.tasterschaft2 == 1:
                        if self.messpunkt_anzahl in {5, 6}:
                            return 1.0
                        else:
                            return 20631 * phi**-1.6878 if phi != MU_NAN else MU_NAN
        return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.frei_eff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
                val = self.messpunkt_anzahl - 1
            else:
                val = self.anzahl_messungen * abs(self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1))
            return abs(val) if val != MU_NAN else MU_NAN



class TK_3dA_W2(TMU_3DKomponente):
    def __init__(self, modell, const_list ,lfdnr):
        super().__init__(modell, 1317, const_list, "W<sub>B</sub>")
        self.ConstNeeded += [TKompConstants["TC_3d_ABST_LM2"], TKompConstants["TC_3d_ABST_LE2"]]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(TermL0=0.15,TermL1=0,Verteilung="V_Rechteck",KennwertArt="M3D_MethodeB",Freiheitsgrad="FG_unbegrenzt",FreiN_minus_1=0,Flags=1,)
        self.fields_to_edit = []

        self.addConstNeededToModell()
    def setMesspunktAnzahl(self):
        for c in self.modell:
            if c.komp_id in [1316,3994]:
                self.messpunkt_anzahl = c.messpunkt_anzahl

    def setAnzahlMessungen(self):
        for c in self.modell:
            if c.komp_id in [1316,3994]:
                self.anzahl_messungen = c.anzahl_messungen

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sens_c1
        if (self.modell.abstand == 1 and
            self.modell.Element2 in {"Gerade", "Ebene", "Zylinder", "Kegel"}):
            lm2 = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_LM2]
            le2 = self.modell.const_list.const_map[TKompConstants.TC_3d_ABST_LE2]
            if lm2 != MU_NAN and le2 != MU_NAN and lm2 != 0:
                return le2 / lm2
        return MU_NAN


    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        self.setMesspunktAnzahl()
        self.setAnzahlMessungen()
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
            x2 = self.modell.find_komponente_by_id([1316,3994])
            if x2:
                return x2.standard_unsicherheit_su()
        return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.frei_eff
        self.setMesspunktAnzahl()
        self.setAnzahlMessungen()
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

    @property
    def effektiver_freiheitsgrad(self):
        if self.archiv:
            return self.arch_data.FreiEff

        n = self.messpunkt_anzahl
        m = self.anzahl_messungen
        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = n - 1
        elif self.data.KennwertArt.name == "M3D_MethodeA" and n > 2:
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

        if self.modell.taster == 1:
            if self.modell.Element1 in {"Punkt", "Gerade", "Ebene"}:
                if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                    result = 1.0
                else:
                    result = 0.5  # Kreis, Halbkugel, Zylinder, Kegel
        elif self.modell.taster == 2:
            if self.modell.Element2 in {"Punkt", "Gerade", "Ebene"}:
                result = 0.5  # egal welches toleriertes Element
            # sonst bleibt 0

        return result

    def b_val(self):
        if self.archiv:
            return self.arch_data.BVAL

        if self.data.KennwertArt.name == "M3D_MethodeA":  # Methode A
            return 1.0
        else:  # Methode B
            if self.messpunkt_anzahl in (5, 6):
                return 1.0
            elif self.messpunkt_anzahl > 6:
                return 1.5
            else:
                return 0.0

    @property
    def effektiver_freiheitsgrad(self):
        if self.archiv:
            result = self.arch_data.FreiEff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":  # Methode B
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
            if self.modell.taster == 1:
                return 1.0  # Verwendung desselben Tasters
            else:
                return 0.5  # verschiedene Taster

    def standard_unsicherheit_su(self):
        if self.archiv:
            return self.arch_data.AVAL
        else:
            result = MU_NAN
            if self.sensititivty_c1() != MU_NAN:
                result = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_Uc] / 2.0
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
            mpe_ml = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_MpeML]
            if mpe_ml != MU_NAN:
                lt = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_LT]
                lte = self.modell.const_list.const_map[TKompConstants.TC_3D_ABST_LTE]
                ltb = self.modell.const_list.const_map[TKompConstants.TC_3D_ABST_LTB]

                if self.ist_zahl(lte) and self.ist_zahl(ltb) and self.ist_zahl(lt) and lt != 0:
                    result = (lte + ltb) * mpe_ml / (lt * 2.0)

            return result

    def b_val(self):
        if self.archiv:
            return self.arch_data.BVAL
        else:
            return 0.5












class TK_3d_DeltaFT(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1310, const_list, "&Delta;F<sub>T</sub>")
        self.lfdnr = lfdnr
        self.ConstNeeded += [
            TKompConstants["TC_3d_FORM_FKMG"],
            TKompConstants["TC_3d_FORM_FN"]
        ]
        self.fields_to_edit = []  # Alles wird errechnet
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            result = MU_NAN
            fn = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_FN]
            fkmg = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_FKMG]

            if fn != MU_NAN and fkmg != MU_NAN:
                if fkmg > fn:
                    result = sqrt(fkmg**2 - fn**2) / (2 * sqrt(3))
                else:
                    result = fn / (2 * sqrt(3))
            return result
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN





class TK_3d_DeltaFkmg(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1311, const_list, "&Delta;F<sub>KMG</sub>")
        self.einheit = "µm"
        self.einheit_ergebnis = "µm"
        self.lfdnr = lfdnr
        self.dez = 5
        self.id: int
        self.messpunkt_anzahl = None
        self.fields_to_edit = []

        self.ConstNeeded += [TKompConstants["TC_3d_KMG_K"]]

        element = TMU_3DElementR.get(self.modell.element)
        merkmal = self.modell.merkmal

        if merkmal == 1 and element in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_FORM_L"]]
        elif merkmal == 2 and element == "Ebene":
            self.ConstNeeded += [
                TKompConstants["TC_3d_FORM_L"],
                TKompConstants["TC_3d_FORM_DL"]
            ]
        elif merkmal == 3 and element in ["Kreis", "Halbkugel", "Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_DUME_D"]]
        elif merkmal == 4 and element == "Zylinder":
            self.ConstNeeded += [
                TKompConstants["TC_3d_FORM_L"],
                TKompConstants["TC_3d_DUME_D"]
            ]
        elif merkmal == 5 and element == "Halbkugel":
            self.ConstNeeded += [TKompConstants["TC_3d_FORM_L"]]
        elif merkmal == 5 and element == "Kegel":
            self.ConstNeeded += [
                TKompConstants["TC_3d_FORM_L"],
                TKompConstants["TC_3d_DUME_D"]
            ]

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

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval

            result = MU_NAN
            element = TMU_3DElementR.get(self.modell.element)
            merkmal = self.modell.merkmal

            if merkmal == 1 and element in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                L = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_L]
                K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
                if K != MU_NAN and L != MU_NAN and K != 0:
                    result = L / K

            elif merkmal == 2 and element == "Ebene":
                L = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_L]
                K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
                DL = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_DL]
                if K != MU_NAN and L != MU_NAN and DL != MU_NAN and K != 0:
                    result = (1 / K) * sqrt(L**2 + 5 * DL**2)

            elif merkmal == 3 and element in ["Kreis", "Halbkugel", "Zylinder", "Kegel"]:
                K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
                D = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_D]
                if K != MU_NAN and D != MU_NAN and K != 0:
                    result = (D / K) * sqrt(26 / 4)

            elif merkmal == 4 and element == "Zylinder":
                L = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_L]
                K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
                D = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_D]
                if K != MU_NAN and L != MU_NAN and D != MU_NAN and K != 0:
                    result = (1 / K) * sqrt((26 / 4) * D**2 + 10 * L**2)

            elif merkmal == 5 and element == "Halbkugel":
                L = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_L]
                K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
                if K != MU_NAN and L != MU_NAN and K != 0:
                    result = (4 * L) / K

            elif merkmal == 5 and element == "Kegel":
                L = self.modell.const_list.const_map[TKompConstants.TC_3d_FORM_L]
                K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
                D = self.modell.const_list.const_map[TKompConstants.TC_3d_DUME_D]
                if K != MU_NAN and L != MU_NAN and D != MU_NAN and K != 0:
                    result = (4 / K) * sqrt(L**2 + D**2)

            return result

        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN


class TK_3d_Ri_WE(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1327, const_list, "W<sub>E</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.id: int
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )

        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LME"], TKompConstants["TC_3d_Ri_LE"]]
        self.addConstNeededToModell()

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        result = float("nan")
        e = self.modell.Element1
        if e in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if e in ["Gerade", "Ebene"]:
                    result = 1
            else:  # Methode B
                if e in ["Gerade", "Ebene"]:
                    if self.modell.punktmusterR2 == 1:  # Gleichmäßig verteilt
                        result = math.sqrt((12 * (self.messpunkt_anzahl - 1)) / (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1)))
                    elif self.modell.punktmusterR2 == 2:  # Zwei Radialschnitte
                        result = math.sqrt(4 / self.messpunkt_anzahl)
                    elif self.modell.punktmusterR2 == 3:  # Kreisförmig
                        result = math.sqrt(8 / self.messpunkt_anzahl)
                elif e in ["Zylinder", "Kegel"]:
                    if self.modell.punktmusterR2 == 1:  # Gleichmäßig verteilt
                        result = math.sqrt((24 * (self.messpunkt_anzahl - 1)) / (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1)))
                    elif self.modell.punktmusterR2 == 2:  # Zwei Radialschnitte
                        result = math.sqrt(8 / self.messpunkt_anzahl)
        return result

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if not (self.modell.Element1 in ["Punkt", "Kreis"]):
            LME = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LME]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LME != float("nan") and LME != 0:
                result = LE / LME
        return result


class TK_3d_Ri_DeltaXE1(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1328, const_list, "&Delta;X<sub>E1</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.id: int
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LME"], TKompConstants["TC_3d_Ri_LE"]]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        e = self.modell.Element1
        if e in ["Punkt", "Kreis"]:
            LME = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LME]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LME != float("nan") and LME != 0:
                result = LE / LME
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeA":
            result = 1
        else:  # Methode B
            e = self.modell.Element1
            if e == "Punkt":
                result = math.sqrt(1 / self.messpunkt_anzahl)
            elif e == "Kreis":
                result = math.sqrt(2 / self.messpunkt_anzahl)

        return result


class TK_3d_Ri_DeltaXE2(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1329, const_list, "&Delta;X<sub>E2</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LME"], TKompConstants["TC_3d_Ri_LE"]]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        e = self.modell.Element2
        if e in ["Punkt", "Kreis"]:
            LME = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LME]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LME != float("nan") and LME != 0:
                result = LE / LME
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeA":
            result = 1
        else:  # Methode B
            e = self.modell.Element2
            if e == "Punkt":
                result = math.sqrt(1 / self.messpunkt_anzahl)
            elif e == "Kreis":
                result = math.sqrt(2 / self.messpunkt_anzahl)

        return result


class TK_3d_Ri_DeltaXET1(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1330, const_list, "&Delta;X<sub>TE1</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LME"],
            TKompConstants["TC_3d_Ri_LE"],
            TKompConstants["TC_3d_KMG_A"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        e = self.modell.Element1
        if e in ["Punkt", "Kreis"] and self.modell.taster1 == 2:
            LME = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LME]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LME != float("nan") and LME != 0:
                result = LE / LME
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeA":
            result = 1
        else:  # Methode B
            e = self.modell.Element1
            if e in ["Punkt", "Kreis"] and self.modell.taster1 == 2:
                if self.messpunkt_anzahl == 4:
                    result = math.sqrt(2 / 3)
                elif self.messpunkt_anzahl in [5, 6]:
                    result = math.sqrt(0.5)
                elif self.messpunkt_anzahl > 6:
                    result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl)

        return result


class TK_3d_Ri_DeltaXET2(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1331, const_list, "&Delta;X<sub>TE2</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )

        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LME"],
            TKompConstants["TC_3d_Ri_LE"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        e = self.modell.Element2
        if e in ["Punkt", "Kreis"] and self.modell.taster1 == 2:
            LME = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LME]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LME != float("nan") and LME != 0:
                result = LE / LME
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeA":
            result = 1
        else:  # Methode B
            e = self.modell.Element2
            if e in ["Punkt", "Kreis"] and self.modell.taster1 == 2:
                if self.messpunkt_anzahl == 4:
                    result = math.sqrt(2 / 3)
                elif self.messpunkt_anzahl in [5, 6]:
                    result = math.sqrt(0.5)
                elif self.messpunkt_anzahl > 6:
                    result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl)

        return result


class TK_3d_Ri_WB(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1332, const_list, "W<sub>B</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.id: int
        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LMB"],
            TKompConstants["TC_3d_Koax_LB"],
            TKompConstants["TC_3d_KMG_A"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if self.modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LMB]
            LB = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LB]

            if LB != float("nan") and LMB != float("nan") and LMB != 0:
                result = LB / LMB
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititivty_c1() != float("nan"):
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                    result = 1
            else:  # Methode B
                if self.messpunkt_anzahl > 1:
                    # Gerade, Ebene und Punkt/NDEF
                    if self.modell.Bezug1 in ["Gerade", "Ebene"] and \
                        self.modell.Bezug2 in ["Punkt", None]:
                        result = math.sqrt((12 * (self.messpunkt_anzahl - 1)) / (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1)))
                    # Gerade, Ebene und Gerade
                    elif self.modell.Bezug1 in ["Gerade", "Ebene"] and \
                         self.modell.Bezug2 == "Gerade":
                        result = math.sqrt(4 / self.messpunkt_anzahl)
                    # Gerade, Ebene und Ebene
                    elif self.modell.Bezug1 in ["Gerade", "Ebene"] and \
                         self.modell.Bezug2 == "Ebene":
                        result = math.sqrt(8 / self.messpunkt_anzahl)
                    # Zylinder, Kegel und Punkt
                    elif self.modell.Bezug1 in ["Zylinder", "Kegel"] and \
                         self.modell.Bezug2 == "Punkt":
                        result = math.sqrt((24 * (self.messpunkt_anzahl - 1)) / (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1)))
                    # Zylinder, Kegel und Gerade
                    elif self.modell.Bezug1 in ["Zylinder", "Kegel"] and \
                         self.modell.Bezug2 == "Gerade":
                        result = math.sqrt(8 / self.messpunkt_anzahl)
        return result
    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = self.messpunkt_anzahl - 1
        else:
            result = self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Bezug1))

        if result != float("nan"):
            result = abs(result)

        return result


class TK_3d_Ri_DeltaXB1(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1333, const_list, "&Delta;X<sub>B1</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr

        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LMB"],
            TKompConstants["TC_3d_Ri_LE"],
            TKompConstants["TC_3d_KMG_A"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if self.modell.Bezug1 in ["Punkt", "Kreis"]:
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LMB]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LMB != float("nan") and LMB != 0:
                result = LE / LMB
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.data.KennwertArt.name == "M3D_MethodeA":
            result = 1
        else:  # Methode B
            if self.modell.Bezug1 == "Punkt":
                result = math.sqrt(1 / self.messpunkt_anzahl)
            elif self.modell.Bezug1 == "Kreis":
                result = math.sqrt(2 / self.messpunkt_anzahl)
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = self.messpunkt_anzahl - 1
        else:
            result = self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Bezug1))

        if result != float("nan"):
            result = abs(result)

        return result



class TK_3d_Ri_DeltaXB2(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1334, const_list, "&Delta;X<sub>B2</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr

        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LMB"],
            TKompConstants["TC_3d_Ri_LE"],
            TKompConstants["TC_3d_KMG_A"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if self.modell.Bezug2 in ["Punkt", "Kreis"]:
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LMB]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LMB != float("nan") and LMB != 0:
                result = LE / LMB
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.data.KennwertArt.name == "M3D_MethodeA":
            result = 1
        else:  # Methode B
            if self.modell.Bezug2 == "Punkt":
                result = math.sqrt(1 / self.messpunkt_anzahl)
            elif self.modell.Bezug2 == "Kreis":
                result = math.sqrt(2 / self.messpunkt_anzahl)
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = self.messpunkt_anzahl - 1
        else:
            result = self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Bezug2))

        if result != float("nan"):
            result = abs(result)

        return result


class TK_3d_Ri_DeltaXBT1(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1335, const_list, "&Delta;X<sub>TB1</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr

        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LMB"],
            TKompConstants["TC_3d_Ri_LE"],
            TKompConstants["TC_3d_KMG_A"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if self.modell.Bezug1 in ["Punkt", "Kreis"] and self.modell.taster2 == 2:
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LMB]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LMB != float("nan") and LMB != 0:
                result = LE / LMB
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititivty_c1() != float("nan"):
            if self.data.KennwertArt.name == "M3D_MethodeA":
                result = 1
            else:  # Methode B
                if self.modell.Bezug1 in ["Punkt", "Kreis"]:
                    if self.messpunkt_anzahl == 4:
                        result = 0.82
                    elif self.messpunkt_anzahl in [5, 6]:
                        result = 0.71
                    elif self.messpunkt_anzahl > 6:
                        result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl)
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = self.messpunkt_anzahl - 1
        else:
            result = self.anzahl_messungen * (self.messpunkt_anzahl - 4)

        if result != float("nan"):
            result = abs(result)

        return result


class TK_3d_Ri_DeltaXBT2(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1336, const_list, "&Delta;X<sub>TB2</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr

        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_Ri_LMB"],
            TKompConstants["TC_3d_Ri_LE"]
        ]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if self.modell.Bezug2 in ["Punkt", "Kreis"] and self.modell.taster2 == 2:
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LMB]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]

            if LE != float("nan") and LMB != float("nan") and LMB != 0:
                result = LE / LMB
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititivty_c1() != float("nan"):
            if self.data.KennwertArt.name == "M3D_MethodeA":
                result = 1
            else:  # Methode B
                if self.modell.Bezug2 in ["Punkt", "Kreis"]:
                    if self.messpunkt_anzahl == 4:
                        result = math.sqrt(2 / 3)
                    elif self.messpunkt_anzahl in [5, 6]:
                        result = math.sqrt(0.5)
                    elif self.messpunkt_anzahl > 6:
                        result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl)
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff

        result = float("nan")
        if self.data.KennwertArt.name == "M3D_MethodeB":
            result = self.messpunkt_anzahl - 1
        else:
            result = self.anzahl_messungen * (self.messpunkt_anzahl - 4)

        if result != float("nan"):
            result = abs(result)

        return result



class TK_3d_Ri_DeltaEKMG(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1338, const_list, "&Delta;E<sub>KMG</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr

        if self.modell.merkmal == 1:  # Parallelität
            self.ConstNeeded += [
                TKompConstants["TC_3d_KMG_K"],
                TKompConstants["TC_3d_Ri_LA"],
                TKompConstants["TC_3d_Ri_LE"]
            ]
        elif self.modell.merkmal == 2:  # Rechtwinkligkeit
            self.ConstNeeded += [
                TKompConstants["TC_3d_KMG_K"],
                TKompConstants["TC_3d_Ri_LE"]
            ]
        elif self.modell.merkmal == 3:  # Neigung
            self.ConstNeeded += [
                TKompConstants["TC_3d_KMG_K"],
                TKompConstants["TC_3d_Ri_LE"],
                TKompConstants["TC_3d_Ri_Alpha"]
            ]
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.AVAL

        result = float("nan")
        if self.modell.merkmal == 1:  # Parallelität
            K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
            LA = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LA]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]
            if self.ist_zahl(K) and self.ist_zahl(LA) and self.ist_zahl(LE) and K != 0:
                result = (2 / K) * min(LA, LE)
        elif self.modell.merkmal == 2:  # Rechtwinkligkeit
            K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]
            if self.ist_zahl(K) and self.ist_zahl(LE) and K != 0:
                result = (2 / K) * LE
        elif self.modell.merkmal == 3:  # Neigung
            K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]
            alpha = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_Alpha]
            if self.ist_zahl(K) and self.ist_zahl(alpha) and self.ist_zahl(LE) and K != 0:
                result = (2 / K) * math.pow(math.sin(alpha), 2) * LE
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        return 0.5

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Ri_XTER(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1371, const_list, "&Delta;X<sub>TER</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr

        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_LT"],
            TKompConstants["TC_3d_Ri_LTE1"],
            TKompConstants["TC_3d_Ri_LTE2"],
            TKompConstants["TC_3d_Ri_LME"],
            TKompConstants["TC_3d_Ri_LE"],
            TKompConstants["TC_3d_KMG_MpeML"]
        ]
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.AVAL

        result = float("nan")
        LT = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_LT]
        MPEml = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_MpeML]
        LTE1 = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LTE1]
        LTE2 = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LTE2]

        if self.ist_zahl(MPEml) and self.ist_zahl(LT) and LT != 0 and self.ist_zahl(LTE1) and self.ist_zahl(LTE2):
            result = (LTE1 + LTE2) / (2 * LT) * MPEml
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        return 0.5

    def sensititivty_c1(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.SensC1

        if self.modell.taster2 == 2:  # Nur wenn verschiedene Taster
            Lme = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LME]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]
            if LE != float("nan") and Lme != float("nan") and Lme != 0:
                result = LE / Lme
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff
        result = 0
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Ri_XTBR(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1372, const_list, "&Delta;X<sub>TBR</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr

        # Hinzufügen der erforderlichen Konstanten
        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_LT"],
            TKompConstants["TC_3d_KMG_MpeML"],
            TKompConstants["TC_3d_Ri_LTB1"],
            TKompConstants["TC_3d_Ri_LTB2"],
            TKompConstants["TC_3d_Ri_LMB"],
            TKompConstants["TC_3d_Ri_LE"]
        ]
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.AVAL

        result = float("nan")
        LT = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_LT]
        MPEml = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_MpeML]
        LTB1 = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LTB1]
        LTB2 = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LTB2]

        if self.ist_zahl(MPEml) and self.ist_zahl(LT) and LT != 0 and self.ist_zahl(LTB1) and self.ist_zahl(LTB2):
            result = ((LTB1 + LTB2) / (2 * LT)) * MPEml
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        return 0.5

    def sensititivty_c1(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.SensC1

        if self.modell.taster2 == 2:  # Nur wenn verschiedene Taster
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LMB]
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Ri_LE]
            if self.ist_zahl(LMB) and self.ist_zahl(LE) and LMB > 0:
                result = LE / LMB
        return result

    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff
        result = 0
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Ri_Aj(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1376, const_list, "A<sub>j</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL

        A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
        if self.ist_zahl(A):
            result = A / 3
        return result

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        return math.sqrt(2)

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Sym_XE1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1339, const_list, "X<sub>E1</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        return 0.5

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                result = 1
            else:  # other method
                if self.messpunkt_anzahl >= self.mindestpunkt_anzahl(self.modell.Element1):
                    if self.modell.Element1 < "E3D_Kreis":
                        result = math.sqrt(1 / self.messpunkt_anzahl)
                    else:
                        result = math.sqrt(2 / self.messpunkt_anzahl)
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl - 1)
                    else:
                        result = 0
                else:  # Neither Method A nor B
                    mpa = self.mindestpunkt_anzahl(self.modell.Element1)
                    if self.messpunkt_anzahl > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl - mpa) / self.anzahl_messungen
                    else:
                        result = 0
        return abs(result) if result != float("nan") else result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Sym_WE1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1340, const_list, 'W<sub>E1</sub>')
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"], TKompConstants["TC_3d_Sym_LE"], TKompConstants["TC_3d_Sym_LME"]]
        self.copy_methode("TK_3d_Sym_XE1")

    def messpunkt_anzahl(self) -> int:
        result = 0
        if self.sensititvity_c1() != float("nan"):
            for komp in self.modell:
                classname = komp.__class__.__name__
                if classname == "TK_3d_Sym_XE1":
                    result = komp.messpunkt_anzahl()
        return result

    def sensititvity_c1(self) -> float:
        result = float("nan")
        if self.archiv:
            result = self.arch_data.SensC1
        else:
            if self.modell.Element1 in ["E3D_Gerade", "E3D_Ebene", "E3D_Zylinder", "E3D_Kegel"]:
                LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LE]
                Lme = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LME]
                if self.ist_zahl(LE) and self.ist_zahl(Lme) and Lme != 0:
                    f = 0.5 if self.modell.Element2 > 0 else 1
                    result = f * LE / (2 * Lme)
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            result = self.arch_data.BVAL
        elif self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                if self.messpunkt_anzahl() > 1 and self.ist_zahl(self.standard_unsicherheit_su()):
                    result = 1
            else:
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Element1):
                    if self.modell.Element1 in ["E3D_Gerade", "E3D_Ebene"]:
                        if self.modell.winkelE1 == 1:
                            result = math.sqrt(12 / self.messpunkt_anzahl())
                        elif self.modell.winkelE1 == 2:
                            result = math.sqrt(4 / self.messpunkt_anzahl())
                        elif self.modell.winkelE1 == 3:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
                    elif self.modell.Element1 in ["E3D_Zylinder", "E3D_Kegel"]:
                        if self.modell.winkelE1 == 1:
                            result = math.sqrt(24 / self.messpunkt_anzahl())
                        elif self.modell.winkelE1 == 2:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
                    else:
                        result = 0
        return result

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            result = self.arch_data.AVAL
        elif self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komp("Komp_3d_Sym_XE1")
            if A is not None:
                result = A.standard_unsicherheit_su()
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            result = self.arch_data.UNSB
        else:
            fpv = self.b_val()
            std = self.standard_unsicherheit_su()
            ci = self.sensititvity_c1()
            v = float("nan")
            if self.ist_zahl(ci):
                if self.data.KennwertArt == "M3D_MethodeA":
                    v = std
                elif self.ist_zahl(std):
                    v = std
                else:
                    A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                    if A != float("nan"):
                        v = A / 3
                if self.ist_zahl(v) and self.ist_zahl(fpv):
                    result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            result = self.arch_data.FreiEff
        else:
            if self.data.KennwertArt == "M3D_MethodeB":
                result = 0
            else:
                U = self.unsicherheitsbeitrag
                if U != float("nan"):
                    if self.data.KennwertArt == "M3D_MethodeA":
                        if self.messpunkt_anzahl() > 1:
                            result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                        else:
                            result = 0
                    else:
                        mpa = self.mindestpunkt_anzahl(self.modell.Element1)
                        if self.messpunkt_anzahl() > mpa:
                            if self.anzahl_messungen != 0:
                                result = (U ** 4) / (self.messpunkt_anzahl() - mpa) / self.anzahl_messungen
                        else:
                            result = 0
        return abs(result) if result != float("nan") else result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Sym_XE2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1341, const_list, "X<sub>E2</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        return 0.5

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                result = 1
            else:  # other method
                chk = self.modell.Element1 if self.modell.Element1 < 4 else self.modell.Element1 - 1
                if self.messpunkt_anzahl >= chk:
                    if self.modell.Element1 < "E3D_Kreis":
                        result = math.sqrt(1 / self.messpunkt_anzahl)
                    else:
                        result = math.sqrt(2 / self.messpunkt_anzahl)
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl - 1)
                    else:
                        result = 0
                else:  # Neither Method A nor B
                    mpa = self.mindestpunkt_anzahl(self.modell.Element1)
                    if self.messpunkt_anzahl > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl - mpa) / self.anzahl_messungen
                    else:
                        result = 0
        return abs(result) if result != float("nan") else result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)



class TK_3d_Sym_WE2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1342, const_list, "W<sub>E2</sub>")
        self.fields_to_edit = []
        self.lfdnr = lfdnr
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"], TKompConstants["TC_3d_Sym_LE"], TKompConstants["TC_3d_Sym_LME"]]
        self.copy_methode("TK_3d_Sym_XE2")

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        result = float("nan")
        if self.modell.Element1 in ["E3D_Gerade", "E3D_Ebene", "E3D_Zylinder", "E3D_Kegel"]:
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LE]
            Lme = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LME]
            if self.ist_zahl(LE) and self.ist_zahl(Lme) and Lme != 0:
                result = 0.5 * LE / (2 * Lme)
        return result

    def messpunkt_anzahl(self) -> int:
        result = 0
        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XE2")
            if A is not None:
                result = A.messpunkt_anzahl()
        return result

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                if self.messpunkt_anzahl() > 1 and self.ist_zahl(self.standard_unsicherheit_su()):
                    result = 1
            else:  # other method
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Element2):
                    if self.modell.Element2 in ["E3D_Gerade", "E3D_Ebene"]:
                        if self.modell.WinkelE2 == 1:  # MusterE1
                            result = math.sqrt(12 / self.messpunkt_anzahl())
                        elif self.modell.WinkelE2 == 2:
                            result = math.sqrt(4 / self.messpunkt_anzahl())
                        elif self.modell.WinkelE2 == 3:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
                    elif self.modell.Element2 in ["E3D_Zylinder", "E3D_Kegel"]:
                        if self.modell.WinkelE2 == 1:
                            result = math.sqrt(24 / self.messpunkt_anzahl())
                        elif self.modell.WinkelE2 == 2:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
                    else:
                        result = 0
        return result

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL
        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XE2")
            if A is not None:
                result = A.standard_unsicherheit_su()
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl() > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                    else:
                        result = 0
                else:  # Neither Method A nor B
                    mpa = self.mindestpunkt_anzahl(self.modell.Element2)
                    if self.messpunkt_anzahl() > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl() - mpa) / self.anzahl_messungen
                    else:
                        result = 0
        return abs(result) if result != float("nan") else result

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


from functools import cached_property

class TK_3d_Sym_DeltaXTE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1343, const_list, "&Delta;X<sub>TE</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"]]


    def sensititvity_c1(self) -> float:
        """Berechnet die Sensitivität C1."""
        if self.archiv:
            return self.arch_data.SensC1
        if self.modell.taster1 == 2:
            return 1
        return float("nan")

    def b_val(self) -> float:
        """Berechnet den B-Wert basierend auf der Messpunktanzahl."""
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                if self.messpunkt_anzahl() > 1 and self.ist_zahl(self.standard_unsicherheit_su()):
                    result = 1
            else:  # Andere Methode
                if self.messpunkt_anzahl() >= 4:
                    if self.modell.Element1 > "E3D_Ebene" or self.modell.taster1 == 1:
                        if self.messpunkt_anzahl() == 4:
                            result = math.sqrt(2 / 3)
                        elif self.messpunkt_anzahl() in [5, 6]:
                            result = math.sqrt(0.5)
                        else:
                            result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl())
                    else:  # Punkt, Gerade, Ebene
                        if self.modell.taster1 == 2:
                            if self.messpunkt_anzahl() < 6:
                                if self.messpunkt_anzahl() == 4:
                                    result = math.sqrt(4 / 3)
                                else:
                                    result = math.sqrt(5 / 4)
                            elif self.messpunkt_anzahl() == 6:
                                result = math.sqrt(3 / 4)
                            else:
                                result = 1.8 * math.sqrt(2 / self.messpunkt_anzahl())
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        """Berechnet den effektiven Freiheitsgrad."""
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        elif self.sensititvity_c1() != float("nan"):
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl() > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                    else:
                        result = 0
                else:  # Weder Methode A noch B
                    if self.messpunkt_anzahl() != 4 and self.anzahl_messungen != 0:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 4) / self.anzahl_messungen
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)


from functools import cached_property

class TK_3d_Sym_XB1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1344, const_list, "X<sub>B1</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.lfdnr = lfdnr
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"]]

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        return 0.5  # Abh. von B17, aber B17 ist immer <> 0

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                if self.messpunkt_anzahl() > 1 and self.ist_zahl(self.standard_unsicherheit_su()):
                    result = 1
            else:  # Andere Methode
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Bezug1):
                    if ord(self.modell.Bezug1) < 4:
                        result = math.sqrt(1 / self.messpunkt_anzahl())
                    else:
                        result = math.sqrt(2 / self.messpunkt_anzahl())
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        elif self.sensititvity_c1() != float("nan"):
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl() > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                    else:
                        result = 0
                else:  # Weder Methode A noch B
                    mpa = self.mindestpunkt_anzahl(self.modell.Bezug1)
                    if self.messpunkt_anzahl() > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl() - mpa) / self.anzahl_messungen
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Sym_WB1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1345, const_list, "W<sub>B1</sub>")
        self.fields_to_edit = []
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"], TKompConstants["TC_3d_Sym_LB"], TKompConstants["TC_3d_Sym_LMB"]]
        self.lfdnr = lfdnr
        self.copy_methode("TK_3d_Sym_XB1")

    def messpunkt_anzahl(self) -> int:
        result = 0
        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XB1")  # Komponente mit ID=1344
            if A is not None:
                result = A.messpunkt_anzahl()
        return result

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1

        result = float("nan")
        if self.modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
            LB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LB]
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LMB]
            if self.ist_zahl(LMB) and self.ist_zahl(LB) and LMB != 0:
                f = 0.5 if ord(self.modell.Bezug2) > 0 else 1
                result = f * LB / (2 * LMB)
        return result

    def b_val(self) -> float:
        """Berechnet den B-Wert basierend auf der Anzahl der Messpunkte und des Bezuges."""
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                result = 1
            else:  # Andere Methode
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Bezug1):
                    if self.modell.Bezug1 in ["Gerade", "Ebene"]:
                        winkel_b1 = self.modell.WinkelB1
                        if winkel_b1 == 1:
                            result = math.sqrt(12 / self.messpunkt_anzahl())
                        elif winkel_b1 == 2:
                            result = math.sqrt(4 / self.messpunkt_anzahl())
                        elif winkel_b1 == 3:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
                    elif self.modell.Bezug1 in ["Zylinder", "Kegel"]:
                        winkel_b1 = self.modell.WinkelB1
                        if winkel_b1 == 1:
                            result = math.sqrt(24 / self.messpunkt_anzahl())
                        elif winkel_b1 == 2:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
        return result

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL

        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XB1")  # Komponente mit ID=1344
            if A is not None:
                result = A.standard_unsicherheit_su()
        return result

    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        """Berechnet den effektiven Freiheitsgrad."""
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            U = self.unsicherheitsbeitrag()
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl() > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                    else:
                        result = 0
                else:  # Weder Methode A noch B
                    mpa = self.mindestpunkt_anzahl(self.modell.Bezug1)
                    if self.messpunkt_anzahl() > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl() - mpa) / self.anzahl_messungen
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


from functools import cached_property

class TK_3d_Sym_XB2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1346, const_list, "X<sub>B2</sub>")
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"]]
        self.lfdnr = lfdnr

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        return 0.5

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                result = 1
            else:  # Andere Methode
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Bezug2):
                    if ord(self.modell.Bezug2) < 4:
                        result = math.sqrt(1 / self.messpunkt_anzahl())
                    else:
                        result = math.sqrt(2 / self.messpunkt_anzahl())
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl() > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                    else:
                        result = 0
                else:  # Weder Methode A noch B
                    mpa = self.mindestpunkt_anzahl(self.modell.Bezug2)
                    if self.messpunkt_anzahl() > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl() - mpa) / self.anzahl_messungen
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL

        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XB1")  # Komponente mit ID=1344
            if A is not None:
                result = A.standard_unsicherheit_su()
        return result


class TK_3d_Sym_WB2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1347, const_list, "W<sub>B2</sub>")
        self.fields_to_edit = []
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"], TKompConstants["TC_3d_Sym_LB"], TKompConstants["TC_3d_Sym_LMB"]]
        self.lfdnr = lfdnr

    def messpunkt_anzahl(self) -> int:
        result = 0
        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XB2")
            # Komponente mit ID=1346
            if A is not None:
                result = A.messpunkt_anzahl()
        return result

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        else:
            LB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LB]
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LMB]
            if self.modell.Bezug1 == self.modell.Bezug2 and \
               self.modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                if self.ist_zahl(LB) and self.ist_zahl(LMB) and LMB > 0:
                    return 0.5 * LB / 2 / LMB
        return float("nan")

    def b_val(self) -> float:
        """Berechnet den B-Wert für WB2, abhängig von der Messpunktanzahl und dem Modellbezug."""
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                result = 1
            else:  # Andere Methode
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Bezug2):
                    if self.modell.Bezug1 in ["Gerade", "Ebene"]:
                        if self.modell.WinkelB2 == 1:
                            result = math.sqrt(12 / self.messpunkt_anzahl())
                        elif self.modell.WinkelB2 == 2:
                            result = math.sqrt(4 / self.messpunkt_anzahl())
                        elif self.modell.WinkelB2 == 3:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
                    elif self.modell.Bezug2 in ["Zylinder", "Kegel"]:
                        if self.modell.WinkelB2 == 1:
                            result = math.sqrt(24 / self.messpunkt_anzahl())
                        elif self.modell.WinkelB2 == 2:
                            result = math.sqrt(8 / self.messpunkt_anzahl())
        return result

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL

        if self.sensititvity_c1() != float("nan"):
            A = self.modell.find_komponente_by_classname("TK_3d_Sym_XB2")  # Komponente mit ID=1346
            if A is not None:
                result = A.standard_unsicherheit_su()
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            U = self.unsicherheitsbeitrag
            if U != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl() > 1:
                        result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                    else:
                        result = 0
                else:  # Weder Methode A noch B
                    mpa = self.mindestpunkt_anzahl(self.modell.Bezug2)
                    if self.messpunkt_anzahl() > mpa:
                        if self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl() - mpa) / self.anzahl_messungen
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        """Überprüft, ob der Wert eine gültige Zahl ist."""
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Sym_DeltaXTB(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1348, const_list, "ΔX<sub>TB</sub>")
        self.fields_to_edit = ['EF_Term0', 'EF_Kennwertart', 'EF_MPAnzahl']
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"]]
        self.lfdnr = lfdnr

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        else:
            if self.modell.taster1 == 2:
                return 1
            return float("nan")

    def b_val(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.BVAL

        if self.sensititvity_c1() != float("nan"):
            if self.data.KennwertArt == "M3D_MethodeA":
                if self.messpunkt_anzahl() > 1 and self.ist_zahl(self.standard_unsicherheit_su()):
                    result = 1
            else:  # Andere Methode
                if self.messpunkt_anzahl() >= 4:
                    if (self.modell.Bezug1 > "Ebene") or (self.modell.taster2 == 1):
                        if self.messpunkt_anzahl() == 4:
                            result = math.sqrt(2 / 3)
                        elif self.messpunkt_anzahl() in [5, 6]:
                            result = math.sqrt(0.5)
                        else:
                            result = 1.3 * math.sqrt(2 / self.messpunkt_anzahl())
                    else:  # Punkt, Gerade, Ebene
                        if self.modell.taster2 == 2:
                            if self.messpunkt_anzahl() < 6:
                                if self.messpunkt_anzahl() == 4:
                                    result = math.sqrt(4 / 3)
                                else:
                                    result = math.sqrt(5 / 4)
                            elif self.messpunkt_anzahl() == 6:
                                result = math.sqrt(3 / 4)
                            else:
                                result = 1.8 * math.sqrt(2 / self.messpunkt_anzahl())
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        ci = self.sensititvity_c1()
        v = float("nan")

        if self.ist_zahl(ci):
            if self.data.KennwertArt == "M3D_MethodeA":
                v = std
            elif self.ist_zahl(std):
                v = std
            else:
                A = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if A != float("nan"):
                    v = A / 3

            if self.ist_zahl(v) and self.ist_zahl(fpv):
                result = v * fpv * ci
        return result

    def effektiver_freiheitsgrad(self) -> float:
        result = 0
        if self.archiv:
            return self.arch_data.FreiEff

        if self.data.KennwertArt == "M3D_MethodeB":
            result = 0
        else:
            if self.sensititvity_c1() != float("nan"):  # Spalte F ci
                U = self.unsicherheitsbeitrag
                if U != float("nan"):
                    if self.data.KennwertArt == "M3D_MethodeA":
                        if self.messpunkt_anzahl() > 1:
                            result = (U ** 4) / (self.messpunkt_anzahl() - 1)
                        else:
                            result = 0
                    else:
                        if self.messpunkt_anzahl() != 4 and self.anzahl_messungen != 0:
                            result = (U ** 4) / (self.messpunkt_anzahl() - 4) / self.anzahl_messungen
        if result != float("nan"):
            result = abs(result)
        return result

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)


class TK_3d_Sym_DeltaLkmg(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1349, const_list, "ΔE<sub>KMG</sub>")
        self.ConstNeeded += [TKompConstants["TC_3d_Sym_DE"], TKompConstants["TC_3d_Sym_DB"], TKompConstants["TC_3d_Sym_LE"],
                             TKompConstants["TC_3d_KMG_K"], TKompConstants["TC_3d_Sym_LMB"]]
        self.fields_to_edit = []

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        else:
            return 1

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        else:
            # Berechne den Wert basierend auf der Verteilung
            if self.data.Verteilung == "V3D_Arcsin":
                dis = 2
            elif self.data.Verteilung == "V3D_Rechteck":
                dis = 3
            elif self.data.Verteilung == "V3D_Normal":
                dis = 4
            elif self.data.Verteilung == "V3d_Dreieck":
                dis = 6
            else:
                dis = 1
            return 1 / math.sqrt(dis)

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL

        if self.sensititvity_c1() != float("nan"):
            DE = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_DE] # B12
            DB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_DB] # B21
            LE = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LE]  # B13
            if LE == float("nan"):
                LE = 0
            K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]  # B24
            LMB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LMB] # B22
            if LMB == float("nan"):
                LMB = 0
            if DE != float("nan") and DB != float("nan") and K != float("nan") and K != 0:
                mx = math.pow(max(DE, DB) / 2, 2)
                mn = math.pow(min(LE, LMB), 2)
                result = math.sqrt(mx + mn) / K
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        ci = self.sensititvity_c1()
        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        if ci != float("nan") and fpv != float("nan") and std != float("nan"):
            result = std * fpv * ci
        return result


class TK_3d_Sym_DeltaXTR(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1373, const_list, "ΔX<sub>TR</sub>")
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_LT"], TKompConstants["TC_3d_KMG_MpeML"],
                             TKompConstants["TC_3d_Sym_LTB"], TKompConstants["TC_3d_Sym_LTE"]]
        self.fields_to_edit = []

    def sensititvity_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        else:
            if self.modell.taster1 == 2:
                return 1
            return float("nan")

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        else:
            # Berechne den Wert basierend auf der Verteilung
            if self.data.Verteilung == "V3D_Arcsin":
                dis = 2
            elif self.data.Verteilung == "V3D_Rechteck":
                dis = 3
            elif self.data.Verteilung == "V3D_Normal":
                dis = 4
            elif self.data.Verteilung == "V3d_Dreieck":
                dis = 6
            else:
                dis = 1
            return 1 / math.sqrt(dis)

    def standard_unsicherheit_su(self) -> float:
        result = float("nan")
        if self.archiv:
            return self.arch_data.AVAL

        if self.sensititvity_c1() != float("nan"):
            LT = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_LT]
            LTE = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LTE]
            LTB = self.modell.const_list.const_map[TKompConstants.TC_3d_Sym_LTB]
            MPEml = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_MpeML]

            if (LT != float("nan") and LT > 0 and MPEml != float("nan")
                and LTB != float("nan") and LTE != float("nan")):
                result = (LTE + LTB) * MPEml / LT / 2
        return result

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        """Berechnet den Unsicherheitsbeitrag für DeltaXTR."""
        result = float("nan")
        if self.archiv:
            return self.arch_data.UNSB

        ci = self.sensititvity_c1()
        fpv = self.b_val()
        std = self.standard_unsicherheit_su()
        if ci != float("nan") and fpv != float("nan") and std != float("nan"):
            result = std * fpv * ci
        return result


class TK_3d_Koax_XE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1350, const_list, "X<sub>E</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        else:
            if self.modell.Element1 in ["Kreis", "Zylinder", "Kegel"]:
                if self.data.KennwertArt == "M3D_MethodeA":
                    if self.messpunkt_anzahl > 1:
                        return 1
                elif self.messpunkt_anzahl > TMU_3DElement.get(self.modell.Element1) - 1:
                    return math.sqrt(2 / self.messpunkt_anzahl)
            return float("nan")

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
                result = self.messpunkt_anzahl - 1
            else:
                result = self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1))
        if result != float("nan"):
            return abs(result)


class TK_3d_Koax_WE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1351, const_list, "W<sub>E</sub>")
        self.ConstNeeded += [TKompConstants["TC_3d_Koax_LME"], TKompConstants["TC_3d_Koax_LE"]]
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.SensC1
        else:
            le = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LE]
            lme = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LME]
            if self.modell.Element1 in ["Kreis", "Zylinder", "Kegel"] and le is not None and lme is not None and lme != 0:
                return le / (2 * lme)
            return float("nan")

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.BVAL
        else:
            sensitivity_c1 = self.sensititivty_c1()
            if sensitivity_c1 != float("nan"):
                if self.data.KennwertArt == "M3D_MethodeA":
                    return 1
                else:  # Methode B
                    if self.messpunkt_anzahl >= self.mindestpunkt_anzahl(self.modell.Element1):
                        if self.modell.Element1 == "Kreis":
                            return math.sqrt(8 / self.messpunkt_anzahl)
                        elif self.modell.Element1 in ["Zylinder", "Kegel"]:
                            if self.modell.punktmuster == 1:  # gleichmäßige Punktanordnung
                                return math.sqrt((24 * (self.messpunkt_anzahl - 1)) /
                                                 (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1)))
                            elif self.modell.punktmuster == 2:  # Punktanordnung auf Kreisumfang
                                return math.sqrt(8 / self.messpunkt_anzahl)
        return float("nan")

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.arch_data.FreiEff
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return abs(self.messpunkt_anzahl - 1)
            else:
                return abs(self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1)))


class TK_3d_Koax_DeltaXTE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1352, const_list, "&Delta;X<sub>TE</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
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
                result = 1.0
            elif self.messpunkt_anzahl > 0:
                if self.modell.tasterschaft1 == 2:  # Taster 1/E Schaft parallel
                    if self.messpunkt_anzahl == 4:
                        result = MU_NAN  # entfällt
                    elif self.messpunkt_anzahl == 5:
                        result = 1.12
                    elif self.messpunkt_anzahl == 6:
                        result = 0.87
                    else:  # > 6
                        result = 1.8
                elif self.modell.tasterschaft1 == 1:  # Taster 1/E Schaft senkrecht
                    if self.messpunkt_anzahl == 5:
                        result = 0.71
                    elif self.messpunkt_anzahl == 6:
                        result = 0.71
                    else:  # > 6
                        result = 1.3
            return result
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.FreiEff
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return self.messpunkt_anzahl - 1
            else:
                return self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1))
        except Exception as e:
            print(f"Fehler in EffektiverFreiheitsgrad: {e}")
            return MU_NAN


class TK_3d_Koax_XB1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1353, const_list, "X<sub>B1</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        if self.modell.Bezug1 in ["Kreis", "Zylinder", "Kegel"]:
            self.ConstNeeded += [TKompConstants["TC_3d_Koax_LA"], TKompConstants["TC_3d_Koax_LMB"]]
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

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1
            result = MU_NAN
            if self.modell.Bezug1 in ["Kreis", "Zylinder", "Kegel"]:
                la = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LA]
                lmb = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LMB]
                if la != MU_NAN and lmb != MU_NAN and lmb != 0:
                    result = (la / lmb) - 0.5
            else:
                result = 1
            return result
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            result = MU_NAN
            if self.archiv:
                return self.arch_data.bval
            if self.data.KennwertArt.name == "M3D_MethodeA":
                result = 1.0
            elif self.messpunkt_anzahl >= 3 and self.modell.Bezug1 in ["Kreis", "Zylinder", "Kegel"]:
                result = math.sqrt(2 / self.messpunkt_anzahl)
            return result
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.FreiEff
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return self.messpunkt_anzahl - 1
            else:
                return self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1))
        except Exception as e:
            print(f"Fehler in EffektiverFreiheitsgrad: {e}")
            return MU_NAN


class TK_3d_Koax_WB1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1354, const_list, "W<sub>B</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        if self.modell.Bezug1 in ["Zylinder", "Kegel"] and not self.modell.Bezug2:
            self.ConstNeeded += [TKompConstants["TC_3d_Koax_LA"], TKompConstants["TC_3d_Koax_LMB"]]
        self.fields_to_edit = []
        self.copy_methode("TK_3d_Koax_XB1")
        self.addConstNeededToModell()

    def messpunkt_anzahl(self) -> int:
        try:
            result = 0
            a = self.modell.find_komponente_by_classname("TK_3d_Koax_XB1")
            if a is not None:
                result = a.messpunkt_anzahl()
            return result
        except Exception as e:
            print(f"Fehler in messpunkt_anzahl: {e}")
            return 0

    def anzahl_messungen(self) -> int:
        try:
            result = 0
            a = self.modell.find_komponente_by_classname("TK_3d_Koax_XB1")
            if a is not None:
                result = a.anzahl_messungen()
            return result
        except Exception as e:
            print(f"Fehler in anzahl_messungen: {e}")
            return 0

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval
            result = MU_NAN
            a = self.modell.find_komponente_by_classname("TK_3d_Koax_XB1")
            if a is not None:
                result = a.standard_unsicherheit_su()
            return result
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1
            result = MU_NAN
            if self.modell.Bezug2:
                result = 0
            elif self.modell.Bezug1 in ["Zylinder", "Kegel"] and not self.modell.Bezug2:
                la = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LA]
                lmb = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LMB]
                if la != MU_NAN and lmb != MU_NAN and lmb != 0:
                    result = la / lmb
            return result
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            result = MU_NAN
            if self.archiv:
                return self.arch_data.bval
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if not self.modell.Bezug2:
                    result = 1
            else:  # Methode B
                result = 1  # b = 1 für alle außer den unten abgehandelten Beispielen
                if self.messpunkt_anzahl() >= self.mindestpunkt_anzahl(self.modell.Bezug1):
                    if self.modell.Element1 in ["Zylinder", "Kegel"]:
                        if self.modell.winkelE1 == 1:  # Gleichmäßige Punktanordnung
                            result = math.sqrt((24 * (self.messpunkt_anzahl() - 1)) /
                                               (self.messpunkt_anzahl() * (self.messpunkt_anzahl() + 1)))
                        elif self.modell.winkelE1 == 2:  # Punkt auf Kreisumfang
                            result = math.sqrt(8 / self.messpunkt_anzahl())
            return result
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.FreiEff
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return self.messpunkt_anzahl() - 1
            else:
                return self.anzahl_messungen() * (self.messpunkt_anzahl() - self.mindestpunkt_anzahl(self.modell.Element1))
        except Exception as e:
            print(f"Fehler in EffektiverFreiheitsgrad: {e}")
            return MU_NAN


class TK_3d_Koax_XB2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1355, const_list, "X<sub>B2</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        self.ConstNeeded += [TKompConstants["TC_3d_Koax_LA"], TKompConstants["TC_3d_Koax_LMB"]]
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

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1
            result = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                result = 1.0
            else:  # Methode B
                if self.modell.Bezug2 in ["Kreis", "Zylinder", "Kegel"]:
                    la = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LA]
                    lmb = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LMB]
                    if la != MU_NAN and lmb != MU_NAN and lmb != 0:
                        result = (la / lmb) + 0.5
            return result
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            result = MU_NAN
            if self.archiv:
                return self.arch_data.bval
            if self.sensititivty_c1() != MU_NAN:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    result = 1.0
                else:  # Methode B
                    if self.modell.Bezug2 in ["Kreis", "Zylinder", "Kegel"] and self.messpunkt_anzahl > 3:
                        result = math.sqrt(2 / self.messpunkt_anzahl)
            return result
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.FreiEff
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return self.messpunkt_anzahl - 1
            else:
                return self.anzahl_messungen * (self.messpunkt_anzahl - self.mindestpunkt_anzahl(self.modell.Element1))
        except Exception as e:
            print(f"Fehler in EffektiverFreiheitsgrad: {e}")
            return MU_NAN



class TK_3d_Koax_DeltaXTB(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1356, const_list, "&Delta;X<sub>TB</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
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
            result = MU_NAN
            if self.archiv:
                result = self.arch_data.BVAL
            else:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    result = 1.0
                else:  # Method B
                    if self.messpunkt_anzahl == 5:
                        if self.modell.tasterschaft2 == 2:
                            result = 1.12  # Taster 1/E Schaft parallel
                        else:
                            result = 0.71  # senkrecht
                    elif self.messpunkt_anzahl == 6:
                        if self.modell.tasterschaft2 == 2:
                            result = 0.87  # Taster 1/E Schaft parallel
                        else:
                            result = 0.71  # senkrecht
                    elif self.messpunkt_anzahl > 6:
                        if self.modell.tasterschaft2 == 2:
                            result = 1.8  # Taster 1/E Schaft parallel
                        else:
                            result = 1.3  # senkrecht
            return result
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.FreiEff
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return self.messpunkt_anzahl - 1
            else:
                return self.anzahl_messungen * (self.messpunkt_anzahl - 4)
        except Exception as e:
            print(f"Fehler in EffektiverFreiheitsgrad: {e}")
            return MU_NAN


class TK_3d_Koax_DeltaEKMG(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1357, const_list, "&Delta;E<sub>KMG</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        self.fields_to_edit = []
        self.ConstNeeded += [
            TKompConstants["TC_3d_Koax_LMB"],
            TKompConstants["TC_3d_Koax_DE"],
            TKompConstants["TC_3d_Koax_DB"],
            TKompConstants["TC_3d_Koax_LB"],
            TKompConstants["TC_3d_KMG_K"]
        ]
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL
            result = 0.0
            de = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_DE]
            db = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_DB]
            k = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]

            d = max(de, db)
            if d != MU_NAN and k != MU_NAN and k != 0:
                result = d / (2 * k)
            return result
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1
            lb = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LB]
            lmb = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LMB]

            if lb != MU_NAN and lmb != MU_NAN and lmb != 0:
                c = lb / lmb
                if c < 1:
                    c = 1
                return c
            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.BVAL
            return 0.5
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN


class TK_3d_Koax_DeltaXTR(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1374, const_list, "&Delta;X<sub>TR</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        self.fields_to_edit = []
        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_LT"],
            TKompConstants["TC_3d_KMG_MpeML"],
            TKompConstants["TC_3d_Koax_LTB"],
            TKompConstants["TC_3d_Koax_LTE"]
        ]
        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.AVAL

            lt = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_LT]
            mpeml = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_MpeML]
            ltb = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LTB]
            lte = self.modell.const_list.const_map[TKompConstants.TC_3d_Koax_LTE]

            if all(val != MU_NAN for val in [lt, mpeml, ltb, lte]) and lt != 0:
                return ((ltb + lte) / (2 * lt)) * mpeml
            return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.BVAL
            return 0.5
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN



import math

class TK_3d_KoaxGA_XE1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1358, const_list, "X<sub>E1</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_A"],
            TKompConstants["TC_3d_KoaxGA_LE"],
            TKompConstants["TC_3d_KoaxGA_LA"]
        ]
        if self.modell.Element1 == "Kreis":
            self.ConstNeeded += [TKompConstants["TC_3d_KoaxGA_LME"]]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1
            la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]
            le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]

            if self.modell.Element1 == "Kreis":
                lme = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LME]
                if all(val != MU_NAN for val in [le, la, lme]) and la != 0 and lme != 0:
                    return (le / 4 / la) + (le / 2 / lme)
            else:
                if all(val != MU_NAN for val in [le, la]) and la != 0:
                    return le / 2 / la
            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if self.modell.Element1 in ["Kreis", "Zylinder", "Kegel"]:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                        self.messpunkt_anzahl > 1 and
                        self.standard_unsicherheit_su() != MU_NAN):
                        return 1.0
                else:
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                        self.messpunkt_anzahl >= (self.modell.Element1_3d.value - 1)):
                        return math.sqrt(2 / self.messpunkt_anzahl)
            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb
            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()

            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheits_beitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            result = 0
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            ci = self.sensititivty_c1()

            if u == MU_NAN or ci == MU_NAN:
                return 0

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl > 1:
                    result = (u ** 4) / (self.messpunkt_anzahl - 1)
                else:
                    result = 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                result = 0
            else:
                if self.anzahl_messungen > 0:
                    diff = self.messpunkt_anzahl - (TMU_3DElement.get(self.modell.Element1) - 1)
                    d2 = diff if diff > 0 else 0
                    if d2 != 0:
                        result = (u ** 4) / d2 / self.anzahl_messungen

            if result != MU_NAN:
                result = abs(result)
            return result
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN

TMU_3DElement = {
    "NDEF": 0,
    "Punkt": 1,
    "Gerade": 2,
    "Ebene": 3,
    "Kreis": 4,
    "Halbkugel": 5,
    "Zylinder": 6,
    "Kegel": 7,
}
TMU_3DElementR = {
    0:"NDEF",
    1:"Punkt",
    2:"Gerade",
    3:"Ebene",
    4:"Kreis",
    5:"Halbkugel",
    6:"Zylinder",
    7:"Kegel",
}


class TK_3d_KoaxGA_WE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1359, const_list, "W<sub>E</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = []

        self.ConstNeeded += [TKompConstants["TC_3d_KMG_A"]]
        if modell.Element1 in ["Zylinder", "Kegel"]:
            self.ConstNeeded += [
                TKompConstants["TC_3d_KoaxGA_LME"],
                TKompConstants["TC_3d_KoaxGA_LE"]
            ]

        self.addConstNeededToModell()

    def messpunkt_anzahl(self) -> int:
        try:
            if self.sensititivty_c1() == MU_NAN:
                return 0

            a = self.modell.find_komponente_by_classname("TK_3d_KoaxGA_XE1")  # ID 1358
            if a is not None:
                return a.messpunkt_anzahl()
            return 0
        except Exception as e:
            print(f"Fehler in messpunkt_anzahl: {e}")
            return 0

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval
            if self.sensititivty_c1() == MU_NAN:
                return MU_NAN

            a = self.modell.find_komponente_by_classname("TK_3d_KoaxGA_XE1")  # ID 1358
            if a is not None:
                return a.standard_unsicherheit_su()
            return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            result = MU_NAN
            if self.modell.Bezug2 in ["Zylinder", "Kegel"]:
                lme = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LME]
                le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
                if all(val != MU_NAN for val in [le, lme]) and lme > 0:
                    result = le / 2 / lme
            return result
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if self.sensititivty_c1() == MU_NAN:
                return MU_NAN

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if (self.data.Verteilung.name == "V3D_AnzahlMP" and self.messpunkt_anzahl() > 1):
                    if self.standard_unsicherheit_su() != MU_NAN:
                        return 1.0
            else:
                if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                    self.messpunkt_anzahl() >= (TMU_3DElement.get(self.modell.Element1) - 1)):
                    if self.modell.winkelE1 == 1:
                        return math.sqrt(24 / self.messpunkt_anzahl())
                    elif self.modell.winkelE1 == 2:
                        return math.sqrt(8 / self.messpunkt_anzahl())

            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()
            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            if u == MU_NAN or self.sensititivty_c1() == MU_NAN:
                return 0

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl() > 1:
                    return abs((u ** 4) / (self.messpunkt_anzahl() - 1))
                return 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                return 0
            else:
                if self.anzahl_messungen > 0:
                    diff = self.messpunkt_anzahl() - (TMU_3DElement.get(self.modell.Element1) - 1)
                    d2 = diff if diff > 0 else 0
                    if d2 != 0:
                        return abs((u ** 4) / d2 / self.anzahl_messungen)
            return 0
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN



class TK_3d_KoaxGA_XE2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1360, const_list, "X<sub>E2</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

        if (modell.Element1 == "Kreis" and
                modell.Element2 == "Kreis"):
            self.ConstNeeded += [
                TKompConstants["TC_3d_KoaxGA_LE"],
                TKompConstants["TC_3d_KoaxGA_LA"],
                TKompConstants["TC_3d_KoaxGA_LME"],
                TKompConstants["TC_3d_KMG_A"]
            ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            if (self.modell.Element1 == "Kreis" and
                    self.modell.Element2 == "Kreis"):
                le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
                la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]
                lme = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LME]

                if all(val != MU_NAN for val in [le, la, lme]) and la > 0 and lme > 0:
                    return (le / 4 / la) + (le / 2 / lme)
            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if self.sensititivty_c1() == MU_NAN:
                return MU_NAN

            if (self.modell.Element1 == "Kreis" and
                    self.modell.Element2 == "Kreis"):

                if self.data.KennwertArt.name == "M3D_MethodeA":
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                            self.messpunkt_anzahl > 1 and
                            self.standard_unsicherheit_su() != MU_NAN):
                        return 1.0
                else:
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                            self.messpunkt_anzahl > (TMU_3DElement.get(self.modell.Element2) - 1)):
                        return math.sqrt(2 / self.messpunkt_anzahl)

            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()
            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            if u == MU_NAN or self.sensititivty_c1() == MU_NAN:
                return 0

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl > 1:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 1))
                return 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                return 0
            else:
                if self.anzahl_messungen > 0:
                    diff = self.messpunkt_anzahl - (TMU_3DElement.get(self.modell.Element2) - 1)
                    d2 = diff if diff > 0 else 0
                    if d2 != 0:
                        return abs((u ** 4) / d2 / self.anzahl_messungen)

            return 0
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN



class TK_3d_KoaxGA_DeltaXTE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1361, const_list, "&Delta;X<sub>TE</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

        if modell.taster1 == 2:
            self.ConstNeeded += [
                TKompConstants["TC_3d_KoaxGA_LE"],
                TKompConstants["TC_3d_KoaxGA_LA"],
                TKompConstants["TC_3d_KMG_A"]
            ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            if self.modell.Methode_3d_TasterAnzahl1 == 2:
                le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
                la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]

                if all(val != MU_NAN for val in [le, la]) and la > 0:
                    return le / 2 / la
            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if self.sensititivty_c1() == MU_NAN:
                return MU_NAN

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                        self.messpunkt_anzahl > 1 and
                        self.standard_unsicherheit_su() != MU_NAN):
                    return 1.0
            else:
                if self.data.Verteilung.name == "V3D_AnzahlMP" and self.messpunkt_anzahl >= 4:
                    if self.messpunkt_anzahl == 4:
                        return math.sqrt(2 / 3)
                    elif self.messpunkt_anzahl in [5, 6]:
                        return math.sqrt(0.5)
                    else:
                        return 1.3 * math.sqrt(2 / self.messpunkt_anzahl)

            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()
            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            if u == MU_NAN or self.sensititivty_c1() == MU_NAN:
                return 0

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl > 1:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 1))
                return 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                return 0
            else:
                if self.anzahl_messungen > 0 and self.messpunkt_anzahl > 4:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 4) / self.anzahl_messungen)

            return 0
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN



class TK_3d_KoaxGA_XB1(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1362, const_list, "X<sub>B1</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KoaxGA_LE"],
            TKompConstants["TC_3d_KoaxGA_LA"],
            TKompConstants["TC_3d_KMG_A"]
        ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
            la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]

            if all(val != MU_NAN for val in [le, la]) and la != 0:
                if (self.modell.Bezug1 == "Kreis" and self.modell.Bezug2 == "Kreis"):
                    return le / 4 / la
                else:
                    return le / 2 / la

            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if self.sensititivty_c1() == MU_NAN:
                return MU_NAN

            bezug1_enum = TMU_3DElement.get(self.modell.Bezug1)

            if self.modell.Bezug1 in ["Kreis", "Zylinder", "Kegel"]:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                            self.messpunkt_anzahl > 1 and
                            self.standard_unsicherheit_su() != MU_NAN):
                        return 1.0
                else:
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                            self.messpunkt_anzahl >= (bezug1_enum - 1)):
                        return math.sqrt(2 / self.messpunkt_anzahl)

            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()
            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            if u == MU_NAN or self.sensititivty_c1() == MU_NAN:
                return 0

            bezug1_enum = TMU_3DElement.get(self.modell.Bezug1)

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl > 1:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 1))
                return 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                return 0
            else:
                if self.anzahl_messungen > 0:
                    diff = self.messpunkt_anzahl - (bezug1_enum - 1)
                    d2 = diff if diff > 0 else 0
                    if d2 != 0:
                        return abs((u ** 4) / d2 / self.anzahl_messungen)

            return 0
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN



class TK_3d_KoaxGA_XB2(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1363, const_list, "X<sub>B2</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KoaxGA_LE"],
            TKompConstants["TC_3d_KoaxGA_LA"],
            TKompConstants["TC_3d_KMG_A"]
        ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
            la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]

            if all(val != MU_NAN for val in [le, la]) and la > 0:
                if self.modell.Bezug1 == "Kreis" and self.modell.Bezug2 == "Kreis":
                    return le / 4 / la

            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if not (self.modell.Bezug1 == "Kreis" and TMU_3DElement.get(self.modell.Bezug2) > 0):
                return MU_NAN

            if self.modell.Bezug2 == "Kreis":
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                            self.messpunkt_anzahl > 1 and
                            self.standard_unsicherheit_su() != MU_NAN):
                        return 1.0
                else:
                    bezug2_enum = TMU_3DElement.get(self.modell.Bezug2)
                    if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                            self.messpunkt_anzahl >= (bezug2_enum - 1)):
                        return math.sqrt(2 / self.messpunkt_anzahl)

            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()
            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            if u == MU_NAN or self.sensititivty_c1() == MU_NAN:
                return 0

            bezug2_enum = TMU_3DElement.get(self.modell.Bezug2)

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl > 1:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 1))
                return 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                return 0
            else:
                if self.anzahl_messungen > 0:
                    diff = self.messpunkt_anzahl - (bezug2_enum - 1)
                    d2 = diff if diff > 0 else 0
                    if d2 != 0:
                        return abs((u ** 4) / d2 / self.anzahl_messungen)

            return 0
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN



class TK_3d_KoaxGA_DeltaXTB(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1364, const_list, "&Delta;X<sub>TB</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]

        self.ConstNeeded += [
            TKompConstants["TC_3d_KoaxGA_LE"],
            TKompConstants["TC_3d_KoaxGA_LA"],
            TKompConstants["TC_3d_KMG_A"]
        ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sens_c1

            if self.modell.taster1 == 2:
                le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
                la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]
                if all(val != MU_NAN for val in [le, la]) and la > 0:
                    return le / 2 / la

            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            if self.sensititivty_c1() == MU_NAN:
                return MU_NAN

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                        self.messpunkt_anzahl > 1 and
                        self.standard_unsicherheit_su() != MU_NAN):
                    return 1.0
            else:
                if (self.data.Verteilung.name == "V3D_AnzahlMP" and
                        self.messpunkt_anzahl >= 4):
                    if self.messpunkt_anzahl == 4:
                        return math.sqrt(2 / 3)
                    elif self.messpunkt_anzahl in [5, 6]:
                        return math.sqrt(0.5)
                    else:
                        return 1.3 * math.sqrt(2 / self.messpunkt_anzahl)

            return MU_NAN
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            if ci == MU_NAN:
                return MU_NAN

            std = self.standard_unsicherheit_su()
            fpv = self.b_val()
            if fpv == MU_NAN or ci == MU_NAN:
                return MU_NAN

            v = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                v = std
            elif std != MU_NAN:
                v = std
            else:
                a3 = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A]
                if a3 != MU_NAN:
                    v = a3 / 3

            if v != MU_NAN:
                return v * fpv * ci
            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

    def effektiver_freiheitsgrad(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.frei_eff

            u = self.unsicherheitsbeitrag
            if u == MU_NAN or self.sensititivty_c1() == MU_NAN:
                return 0

            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.messpunkt_anzahl > 1:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 1))
                return 0
            elif self.data.KennwertArt.name == "M3D_MethodeB":
                return 0
            else:
                if self.anzahl_messungen > 0 and self.messpunkt_anzahl > 4:
                    return abs((u ** 4) / (self.messpunkt_anzahl - 4) / self.anzahl_messungen)

            return 0
        except Exception as e:
            print(f"Fehler in effektiver_freiheitsgrad: {e}")
            return MU_NAN



class TK_3d_KoaxGA_DeltaLkmg(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1365, const_list, "&Delta;L<sub>KMG</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = []

        self.ConstNeeded += [
            TKompConstants["TC_3d_KoaxGA_DE"],
            TKompConstants["TC_3d_KoaxGA_LE"],
            TKompConstants["TC_3d_KMG_K"]
        ]

        self.addConstNeededToModell()

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            verteilung = self.data.Verteilung.name
            dis = {
                "V3D_Arcsin": 2,
                "V3D_Rechteck": 3,
                "V3D_Normal": 4,
                "V3d_Dreieck": 6
            }.get(verteilung, 1)

            return 1.0 / math.sqrt(dis)
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval

            de = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_DE]
            le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
            k = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_K]

            if MU_NAN in [de, le, k] or k == 0:
                return MU_NAN

            return math.sqrt((de / 2) ** 2 + le ** 2) / k
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            fpv = self.b_val()
            std = self.standard_unsicherheit_su()

            if all(val != MU_NAN for val in [ci, fpv, std]):
                return std * fpv * ci

            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN


class TK_3d_KoaxGA_DeltaXTR(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1375, const_list, "&Delta;X<sub>TR</sub>")
        self.lfdnr = lfdnr
        self.fields_to_edit = []

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_LT"],
            TKompConstants["TC_3d_KMG_MpeML"],
            TKompConstants["TC_3d_KoaxGA_LA"],
            TKompConstants["TC_3d_KoaxGA_LE"],
            TKompConstants["TC_3d_KoaxGA_LTB"],
            TKompConstants["TC_3d_KoaxGA_LTE"]
        ]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.sensc1

            if self.modell.Methode_3d_TasterAnzahl1 == 2:
                la = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LA]
                le = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LE]
                if self.ist_zahl(la) and self.ist_zahl(le) and la != 0:
                    return le / 4 / la
            return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititivty_c1: {e}")
            return MU_NAN

    def b_val(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.bval

            verteilung = self.data.Verteilung.name
            dis = {
                "V3D_Arcsin": 2,
                "V3D_Rechteck": 3,
                "V3D_Normal": 4,
                "V3d_Dreieck": 6
            }.get(verteilung, 1)

            return 1.0 / math.sqrt(dis)
        except Exception as e:
            print(f"Fehler in b_val: {e}")
            return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.aval

            if not self.ist_zahl(self.sensititivty_c1()):
                return 0

            lt = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_LT]
            ltb = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LTB]
            lte = self.modell.const_list.const_map[TKompConstants.TC_3d_KoaxGA_LTE]
            mpe_ml = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_MpeML]

            if all(self.ist_zahl(val) for val in [lt, ltb, lte, mpe_ml]) and lt > 0:
                return (lte + ltb) * mpe_ml / lt / 2

            return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

    def ist_zahl(self, value) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb

            ci = self.sensititivty_c1()
            fpv = self.b_val()
            std = self.standard_unsicherheit_su()

            if all(self.ist_zahl(x) for x in [ci, fpv, std]):
                return std * fpv * ci

            return MU_NAN
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN


class TK_3d_PktPkt_dPgeo(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1391, const_list, "&delta;P<sub>Geometrie</sub>")
        self.lfdnr = lfdnr

        self.einheit = "mm"
        self.einheit_ergebnis = "mm"
        self.dez = 5

        self.ConstNeeded += [
            TKompConstants["TC_3d_KMG_A"],
            TKompConstants["TC_3d_PktPkt_dist"]
        ]

        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            K = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A] * 1_000_000  # in mm?
            d = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_dist]  # mm

            if K == 0:
                return MU_NAN
            wert = d / K
            return self.tabelle1_su(wert)  # externe Tabelle 1 Funktion, wie im Original
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN


class TK_3d_PktPkt_dPyKMG(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1392, const_list, "&delta;P<sub>y KMG</sub>")
        self.lfdnr = lfdnr

        self.einheit = "mm"
        self.einheit_ergebnis = "mm"
        self.dez = 5

        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            return self.tabelle1_su(self.data.TermL0)
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su: {e}")
            return MU_NAN

class Sicher:
    def __init__(self):
        self.dist = None
        self.AnzSims = None
        self.AnzBe = None
        self.AnzTe = None
        self.KMG_AmpX = None
        self.KMG_AmpY = None
        self.WinkelSegBE = None
        self.WinkelSegTE = None
        self.Dia1_BE = None
        self.Dia2_TE = None
        self.SimSU = None

class TK_3d_PktPkt_dPZuf(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1393, const_list, "&delta;P<sub>Zuf</sub>")
        self.lfdnr = lfdnr
        self.Sicher = Sicher()
        self.einheit = "mm"
        self.einheit_ergebnis = "mm"
        self.dez = 5

        self.ConstNeeded += [
            # 'TC_3d_KMG_K',
            TKompConstants["TC_3d_PktPkt_dist"],
            TKompConstants["TC_3d_PktPkt_nTastBe"],
            TKompConstants["TC_3d_PktPkt_nTastTe"],
            TKompConstants["TC_3d_PktPkt_WinkelSeg_BE"],
            TKompConstants["TC_3d_PktPkt_WinkelSeg_TE"],
            TKompConstants["TC_3d_PktPkt_AnzSims"],
            TKompConstants["TC_3d_KMG_AmpX"],
            TKompConstants["TC_3d_KMG_AmpY"],
            TKompConstants["TC_3d_PktPkt_Dia_BE"],
            TKompConstants["TC_3d_PktPkt_Dia_TE"]]

        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.sim_su = MU_NAN
        self.sicher = {
            'dist': None,
            'AnzSims': None,
            'AnzBe': None,
            'AnzTe': None,
            'KMG_AmpX': None,
            'KMG_AmpY': None,
            'WinkelSegBE': None,
            'WinkelSegTE': None,
            'Dia1_BE': None,
            'Dia2_TE': None
        }

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        # Konstanten auslesen
        dist = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_dist]
        AnzSims = round(self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_AnzSims])
        AnzBe = round(self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_nTastBe])
        AnzTe = round(self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_nTastTe])
        WinkelSegBE = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_WinkelSeg_BE]
        WinkelSegTE = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_WinkelSeg_TE]
        KMG_AmpX = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_AmpX]
        KMG_AmpY = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_AmpY]
        Dia1_BE = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Dia_BE]
        Dia2_TE = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Dia_TE]

        # Prüfen ob sich Eingaben geändert haben (Cache-Check)
        if (
                dist != self.Sicher.dist or
                AnzSims != self.Sicher.AnzSims or
                AnzBe != self.Sicher.AnzBe or
                AnzTe != self.Sicher.AnzTe or
                KMG_AmpX != self.Sicher.KMG_AmpX or
                KMG_AmpY != self.Sicher.KMG_AmpY or
                WinkelSegBE != self.Sicher.WinkelSegBE or
                WinkelSegTE != self.Sicher.WinkelSegTE or
                Dia1_BE != self.Sicher.Dia1_BE or
                Dia2_TE != self.Sicher.Dia2_TE
        ):
            # Änderungen erkannt → neu berechnen
            self.Sicher.dist = dist
            self.Sicher.AnzSims = AnzSims
            self.Sicher.AnzBe = AnzBe
            self.Sicher.AnzTe = AnzTe
            self.Sicher.KMG_AmpX = KMG_AmpX
            self.Sicher.KMG_AmpY = KMG_AmpY
            self.Sicher.WinkelSegBE = WinkelSegBE
            self.Sicher.WinkelSegTE = WinkelSegTE
            self.Sicher.Dia1_BE = Dia1_BE
            self.Sicher.Dia2_TE = Dia2_TE

            # Simulationsparameter setzen
            global num_sims, kmg_ampx, kmg_ampy
            num_sims = AnzSims
            kmg_ampx = KMG_AmpX
            kmg_ampy = KMG_AmpY

            # Elemente erzeugen (entspricht TSimKreis)
            element1 = Kreis(midx=0, midy=0, dia=Dia1_BE, numpoints=AnzBe, segment=WinkelSegBE)
            element2 = Kreis(midx=dist, midy=0, dia=Dia2_TE, numpoints=AnzTe, segment=WinkelSegTE)

            # Simulation (Doit)
            xbar, std, su = mu_position(element1, element2, AnzSims, KMG_AmpX, KMG_AmpY)

            self.Sicher.SimSU = self.tabelle1_su(std)  # speichern
        else:
            su = self.Sicher.SimSU  # unverändert

        return self.Sicher.SimSU

    @cached_property
    def unsicherheitsbeitrag(self) -> float:
        try:
            if self.archiv:
                return self.arch_data.unsb
            siai = self.standard_unsicherheit_su()
            b = self.b_val()
            g = self.g_val()
            ci = self.sensititivty_c1()
            if any(map(lambda x: x is None or math.isnan(x), [siai, b, g, ci])):
                return MU_NAN
            return siai * b * g * ci
        except Exception as e:
            print(f"Fehler in unsicherheitsbeitrag: {e}")
            return MU_NAN

class TSimKreis:
    def __init__(self, kElementNr, x, y, dia, nPts, Segment):
        self.kElementNr = kElementNr
        self.x = x
        self.y = y
        self.dia = dia
        self.nPts = nPts
        self.Segment = Segment


class Punkt:
    coord_x = 0
    coord_y = 0

    def __init__(self, x=0.0, y=0.0):  # constructor
        self.coord_x = x
        self.coord_y = y
        self.punkt_wolke = np.empty(shape=(num_sims, 2))

    def wolke_erzeugen(self):
        self.punkt_wolke = rng.standard_normal(size=(num_sims, 2))
        for i in range(num_sims):
            self.punkt_wolke[i, 0] = self.coord_x + kmg_ampx / 3. * self.punkt_wolke[i, 0]
            self.punkt_wolke[i, 1] = self.coord_y + kmg_ampy / 3. * self.punkt_wolke[i, 1]


class Kreis(Punkt):
    """ Kreis Objekt """
    # coord_x=0
    # coord_y=0
    dia = 0
    anz_punkte = 0
    k_segment = 360
    Schrittwinkel = 0.0

    def __init__(self, midx=0.0, midy=0.0, dia=0.0, numpoints=8, segment=360):  # constructor
        super().__init__(midx, midy)  # initialisierung Punkt()
        # self.coord_x = midx
        # self.coord_y = midy
        self.dia = dia
        self.anz_punkte = numpoints
        self.k_segment = segment
        self.ideal = np.empty(shape=(self.anz_punkte, 2))  # np.empty([8,2], dtype = float )
        self.calc()  # idealkreis mit diesen Parametern erzeugen
        self.wolke_erzeugen()  # Montecarlo Simulation:  Kreismittelpunkte erzeugen

    def calc(self):
        """ Kreisberechnung Idealkreis """
        self.schrittwinkel = (self.k_segment * np.pi / 180) / self.anz_punkte
        for i in range(0, self.anz_punkte):
            self.ideal[i, 0] = self.coord_x + self.dia / 2 * np.cos(i * self.schrittwinkel)
            self.ideal[i, 1] = self.coord_y + self.dia / 2 * np.sin(i * self.schrittwinkel)

    """ ------------------------------------------------------------------------
      Kreisberechnung Ausgleichskreis mit scipy

    def calc_ausgleichskreisA(self, points ):
        x = points[:,0] # Split x and y coordinates
        y = points[:,1]
        x_m = np.mean(x)  # coordinates of the barycenter
        y_m = np.mean(y)
        def calc_R(xc, yc):
            " "" calculate the distance of each 2D points from the center (xc, yc) "" "
            return np.sqrt((x-xc)**2 + (y-yc)**2)
        # @countcalls
        def f_2(c):
            " "" calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) "" "
            Ri = calc_R(*c)
            return Ri - Ri.mean()
        center_estimate = x_m, y_m
        " "" kleinste Quadrate für Ausgleichskreis "" "
        center_2, ier = optimize.leastsq(f_2, center_estimate)
        xc_2, yc_2 = center_2
        return xc_2, yc_2          # radius?
   ------------------------------------------------------------------------------  """

    def calc_ausgleichskreis(self, points):
        xk = points[:, 0]  # x und y herauslösen
        yk = points[:, 1]

        # Finde Kreisgleichung
        A = np.column_stack((2. * xk, 2 * yk, np.ones_like(xk)))
        rhs = xk * xk + yk * yk
        # Berechne Lösung des Ausgleichsproblem
        a, b, c = la.lstsq(A, rhs, rcond=None)[0]
        # r = np.sqrt(c+a**2+b**2) r=Radius: wird nicht benötigt
        # xc_2, yc_2 = a, b
        return a, b  # Mittelpunkt des Ausgleichskreises

    def wolke_erzeugen(self, zufall=None):
        """ Erzeugt zufällige Punktwolke; bei Bedarf mit übergebenem Zufallsfeld """
        for s in range(num_sims):
            # Wenn keine gemeinsame Zufallswolke übergeben wurde → eigene erzeugen
            if zufall is None:
                zufall_akt = rng.standard_normal(size=(self.anz_punkte, 2))
            else:
                zufall_akt = zufall[s]

            punkte = np.empty_like(zufall_akt)
            for i in range(self.anz_punkte):
                punkte[i, 0] = self.ideal[i, 0] + kmg_ampx / 3.0 * zufall_akt[i, 0]
                punkte[i, 1] = self.ideal[i, 1] + kmg_ampy / 3.0 * zufall_akt[i, 1]

            self.punkt_wolke[s] = self.calc_ausgleichskreis(punkte)


class FrmMCSimClass:
    @staticmethod
    def doit(anz_sims, kmg_amp_x, kmg_amp_y, element1, element2):
        # Übergabe an das globale Simulationsmodul
        global num_sims, kmg_ampx, kmg_ampy

        num_sims = anz_sims
        kmg_ampx = kmg_amp_x
        kmg_ampy = kmg_amp_y

        # Konvertiere deine TSimKreis-Objekte in Kreis-Objekte für die Simulation
        kreis1 = Kreis(midx=element1.x,midy=element1.y,dia=element1.dia,numpoints=element1.nPts,segment=element1.Segment)

        kreis2 = Kreis(midx=element2.x,midy=element2.y,dia=element2.dia,numpoints=element2.nPts,segment=element2.Segment)

        # Berechne Standardunsicherheit
        _, _, su = mu_position(kreis1, kreis2)
        return su

    @staticmethod
    def hide():
        pass

# Objekt wie gehabt
FrmMCSim = FrmMCSimClass()


class TK_3d_PktPkt_dTaster(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1394, const_list, "&delta;T<sub>Tasterwechsel</sub>")
        self.lfdnr = lfdnr

        self.einheit = "mm"
        self.einheit_ergebnis = "mm"
        self.dez = 5

        self.ConstNeeded += [TKompConstants["TC_3d_PktPkt_Wechsel"]]
        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            tasterwechsel = round(self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Wechsel]) == 1
            if tasterwechsel:
                return self.tabelle1_su(0.0000943)
            else:
                return 0.0
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (Taster): {e}")
            return MU_NAN

class TK_3d_PktPkt_dAbwTemp(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1395, const_list, "&delta;(&theta;)")
        self.lfdnr = lfdnr

        self.einheit = "°C"
        self.einheit_ergebnis = ""
        self.dez = 5

        self.ConstNeeded += [
            TKompConstants["TC_3d_PktPkt_Temp"],
            TKompConstants["TC_3d_PktPkt_dist"],
            TKompConstants["TC_AusdehnKoeffMO"]
        ]
        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            a = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_dist]  # in mm
            alpha = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffMO]  # Ausdehnungskoeff.
            if a is not None and alpha is not None:
                return a * alpha
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in sensititvity_c1 (AbwTemp): {e}")
            return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            temp = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Temp]  # °C
            if temp is not None:
                wert = abs((temp - 20.0) / math.sqrt(3))
                return self.tabelle1_su(wert)
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (AbwTemp): {e}")
            return MU_NAN


class TK_3d_PktPkt_AbwTempAusd(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1396, const_list, "&delta;(&alpha;) * &delta;(&theta;)")
        self.lfdnr = lfdnr

        self.einheit = ""
        self.einheit_ergebnis = ""
        self.dez = 5

        self.ConstNeeded += [
            TKompConstants["TC_3d_PktPkt_Temp"],
            TKompConstants["TC_3d_PktPkt_dist"],
            TKompConstants["TC_AusdehnKoeffMO"]
        ]
        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        try:
            return self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_dist]
        except Exception as e:
            print(f"Fehler in sensititvity_c1 (AbwTempAusd): {e}")
            return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        try:
            temp = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Temp]
            alpha = self.modell.const_list.const_map[TKompConstants.TC_AusdehnKoeffMO]
            if temp is not None and alpha is not None:
                u_alpha = 0.2 * alpha / math.sqrt(3)
                u_theta = abs(temp - 20.0) / math.sqrt(3)
                wert = u_theta * u_alpha
                return self.tabelle1_su(wert)
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (AbwTempAusd): {e}")
            return MU_NAN


class TK_3d_PktPkt_dFormAbwBE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1397, const_list, "&Delta;F<sub>BE</sub>(n<sub>BE</sub>;M<sub>BE</sub>)")
        self.lfdnr = lfdnr

        self.einheit = ""
        self.einheit_ergebnis = ""
        self.dez = 5

        self.ConstNeeded += [
            TKompConstants["TC_3d_PktPkt_SigBe"],
            TKompConstants["TC_3d_KMG_A"],
            TKompConstants["TC_3d_PktPkt_nTastBe"],
            TKompConstants["TC_3d_PktPkt_MBe"]
        ]
        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            sig_be = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_SigBe]
            a = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A] / 1000  # umgerechnet in µm
            n_tast_be = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_nTastBe]
            m_be = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_MBe]

            if None not in (sig_be, a, n_tast_be, m_be):
                basis = 3 * math.sqrt(16 * sig_be**2 - 3 * a**2)
                faktor = abs(0.65 * (1 + math.exp(-(n_tast_be - 1) / (0.2 * m_be))) + 0.35 - 1.0)
                wert = basis * faktor
                return self.tabelle1_su(wert)
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (dFormAbwBE): {e}")
            return MU_NAN


class TK_3d_PktPkt_dFormAbwTE(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1398, const_list, "&Delta;F<sub>TE</sub>(n<sub>TE</sub>;M<sub>TE</sub>)")
        self.lfdnr = lfdnr

        self.einheit = ""
        self.einheit_ergebnis = ""
        self.dez = 5

        self.ConstNeeded += [
            TKompConstants["TC_3d_PktPkt_SigTe"],
            TKompConstants["TC_3d_KMG_A"],
            TKompConstants["TC_3d_PktPkt_nTastTe"],
            TKompConstants["TC_3d_PktPkt_Mte"]
        ]
        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            sig_te = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_SigTe]
            a = self.modell.const_list.const_map[TKompConstants.TC_3d_KMG_A] / 1000.0  # mm → µm
            n_tast_te = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_nTastTe]
            m_te = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Mte]

            if None not in (sig_te, a, n_tast_te, m_te):
                basis = 3 * math.sqrt(16 * sig_te**2 - 3 * a**2)
                faktor = abs(0.65 * (1 - math.exp(-(n_tast_te - 1) / (0.2 * m_te))) + 0.35 - 1.0)
                wert = basis * faktor
                return self.tabelle1_su(wert)
            else:
                return MU_NAN
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (dFormAbwTE): {e}")
            return MU_NAN


class TK_3d_PktPkt_dWinkelSektor(TMU_3DKomponente):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1399, const_list, "&delta;(&Delta;&alpha;(&psi;&deg;))")
        self.lfdnr = lfdnr

        self.einheit = ""
        self.einheit_ergebnis = ""
        self.dez = 5

        self.ConstNeeded += [
            TKompConstants["TC_3d_PktPkt_Gamma0"],
            TKompConstants["TC_3d_PktPkt_Gamma1"],
            TKompConstants["TC_3d_PktPkt_ScanKgl"]
        ]
        self.fields_to_edit = ["EF_Verteilung", "EF_StreuungsParam"]

        self.addConstNeededToModell()

    def standard_unsicherheit_su(self) -> float:
        try:
            gamma0 = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Gamma0]
            gamma1 = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_Gamma1]
            scan_kgl = self.modell.const_list.const_map[TKompConstants.TC_3d_PktPkt_ScanKgl]

            if None in (gamma0, gamma1, scan_kgl):
                return MU_NAN

            if scan_kgl == 0:
                e = 360
            elif gamma1 == 0:
                return MU_NAN
            else:
                e = scan_kgl

            wert = gamma0 * math.exp(-e / gamma1)
            return self.tabelle1_su(wert)
        except Exception as e:
            print(f"Fehler in standard_unsicherheit_su (dWinkelSektor): {e}")
            return MU_NAN
