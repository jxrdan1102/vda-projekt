import math
from functools import cached_property
from math import pi, sqrt

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import MU_NAN
from app.services.component_service.componente3D import TMU_3DKomponente


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