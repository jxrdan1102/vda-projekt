from enum import Enum
from typing import List, Set, Dict, Optional

from pydantic import BaseModel


class TKompConstants(Enum):
    TC_Messbereich = 1
    TC_Nennmass = 2
    TC_UntAbmass = 3
    TC_ObAbmass = 4
    TC_Einheit = 5
    TC_AusdehnKoeffME = 6
    TC_AusdehnKoeffEN = 7
    TC_AusdehnKoeffMO = 8
    TC_DurchmesserMessflaeche = 9
    TC_DurchmesserMesseinsatzME = 10
    TC_BreiteMessflaecheMO = 11
    TC_nicht_benutzt_BreiteMessflaecheGN = 12
    TC_BreiteMessflaecheEN = 13
    TC_FaktorKennlinieME = 14
    TC_ParameterKennlinieME = 15
    TC_NichtLinearKennlinieME = 16
    TC_Geometrie_ME = 17
    TC_Geometrie_MO = 18
    TC_Geometrie_GN = 19
    TC_Geometrie_BN = 20
    TC_MantellinieME = 21
    TC_MantellinieMO = 22
    TC_nicht_benutzt_TC_MantellinieGN = 23
    TC_MantellinieEN = 24
    TC_Messwert = 25
    TC_MesskraftME = 26
    TC_MesskraftSchwankungME = 27
    TC_NennmassEN = 28
    TC_nicht_benutzt_TC_NennmassGN = 29
    TC_TempME = 30
    TC_TempMO = 31
    TC_TempEN = 32
    TC_ZeitDeltaMessungEN_MO = 33
    TC_ZeitDrift = 34
    TC_DurchmesserEN = 35
    TC_Winkelabweichung_von_90_Grad = 36
    TC_Radius_der_Zone_des_Spiels = 37
    TC_Laenge_kurze_Kante_PEM = 38
    TC_Tol_Abw_Spanne_ISO_3650 = 39
    TC_Elast_Modul_Normal = 40
    TC_Elast_Modul_MO = 41
    TC_Poisson_Koeff_Normal = 42
    TC_Poisson_Koeff_MO = 43
    TC_Korrelationskoeffizient = 44
    TC_Schrittweite_Geradheitskalibrierung_EN = 45
    TC_Positionsgenauigkeit_Kalibrierung_MO = 46
    TC_Betrag_max_Abweichung_Bezugsgerade = 47
    TC_Laenge_stehender_Schenkel_EN = 48
    TC_Abstand_Stuetzpunkte_EN = 49
    TC_Geradheit_Messplatte_EN = 50
    TC_Positionsabweichung_Stuetzpunkte_EN = 51
    TC_Kalibrierung_Geradheit_EN = 52
    TC_Laenge_stehender_Schenkel_MO = 53
    TC_Stuetzpunktabstand_MO = 54
    TC_Geradheit_Messplatte_MO = 55
    TC_Positionsabweichung_Stuetzpunkte_MO = 56
    TC_Kalibrierung_Geradheit_MO = 57
    TC_Kalibrierung_Ebenheit_Messplatte = 58
    TC_Positionsgenauigkeit_Stuetzpunkte = 59
    TC_Schrittweite_Geradheitskalibrierung_MO = 60
    TC_Hoehendifferenz_Stuetzpunkte = 61
    TC_Laenge_Messobjekt = 62
    TC_Anzahl_Verschiebungen_MO = 63
    TC_Messbereichsendwert_Messeinrichtung = 64
    TC_Hoehe_zu_Rechtwinkligkeit = 65
    TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke = 66
    TC_Rh_Anzahl_Teilmessstrecken = 67
    TC_Rh_Ortabhaengige_Unsicherheit_in_y = 68
    TC_Rh_Gradient_in_Rillenrichtung = 69
    TC_Rh_Messpunktabstand = 70
    TC_Rh_Tiefpasswellenlaengen = 71
    TC_Rh_Kennwertaenderungsfaktor = 72
    TC_Rh_Gemessene_Kenngroesse = 73
    TC_Rh_Anzahl_Wiederholungsmessungen_geaenderter_Antastort = 74
    TC_Rh_Anzahl_Wiederholmessungen_selber_Antastort = 75
    TC_Fm_Anzahl_Wiederholmessungen_StreuungAnzeige = 76
    TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten = 77
    TC_Fm_Grenzwellenlaenge = 78
    TC_Fm_Messwert_MO = 79
    TC_Fm_Richtiger_Wert_Rundheit_Kugelnormal = 80
    TC_Fm_Messunsicherheit_der_Kalibrierung_Kugelnormal = 81
    TC_Fm_Gemessenden_Exzentrizitaet = 82
    TC_Fm_Aussendurchmesser_MO = 83
    TC_Fm_Tastkugeldurchmesser = 84
    TC_Fm_Innendurchmesser_MO = 85
    TC_Fm_Kippung_MO_XAchse = 86
    TC_Fm_Kippung_MO_YAchse = 87
    TC_Fm_Radius_MO = 88
    TC_Fm_Neigung_Zylinderachse_MO_zu_Flaeche_XOY = 89
    TC_Fm_Formabweichung_Normal = 90
    TC_Fm_Kalibrierung_Normal = 91
    TC_Fm_Standardabweichung_Wiederholmessungen_Normal = 92
    TC_Fm_AnzahlMessungen_Fuehrungsabweichung = 93
    TC_Fm_Gemessene_Rundheit_EN = 94
    TC_KTMG_Gemessener_Abstand = 95
    TC_KTMG_Konstanter_Anteil_EMPE = 96
    TC_KTMG_Anzahl_Messpunkte = 97
    TC_KTMG_Gemessener_Winkel = 98
    TC_KTMG_Laenge_kleinster_Schenkel = 99
    TC_KTMG_Gemessene_Geradheit = 100
    TC_KTMG_Sektor_Kreis = 101

    def add_by_value(self, value: int):
        try:
            konst = TKompConstants(value)  # Enum-Zugriff über den Wert (int)
            return konst
        except ValueError:
            print(f"Ungültiger Wert: {value} ist kein gültiger TKompConstants-Eintrag")

    def add_by_name(self, name: str):
        try:
            konst = TKompConstants[name]  # Enum-Zugriff über den Namen (string)
            return konst
        except KeyError:
            print(f"Ungültiger Name: {name} ist kein gültiger TKompConstants-Eintrag")


class TMU_ConstList:
    def __init__(self):
        self.const_map: dict[TKompConstants, float] = {}

    def set_const_val(self, const_id: TKompConstants, value: float):
        if const_id not in self.const_map:
            raise KeyError(f"{const_id} ist nicht in ConstNeeded definiert.")
        self.const_map[const_id] = value

    def get_const_val(self, const_id: TKompConstants) -> float:
        return self.const_map.get(const_id, 0.0)

    def to_list(self) -> list[tuple[TKompConstants, float]]:
        """Optional: falls du eine Liste von Tupeln brauchst."""
        return list(self.const_map.items())

    def init_from_needed_constants(self, needed_constants: Set[TKompConstants]):
        for const in needed_constants:
            if const not in self.const_map:
                self.const_map[const] = None  # oder z. B. 0.0

    def to_serializable(self):
        return {k.name: v for k, v in self.const_map.items()}

class TMU_ConstListResponse(BaseModel):
    const_map: Dict[str, Optional[float]]

    @classmethod
    def from_internal(cls, tmu: TMU_ConstList):
        return cls(const_map=tmu.to_serializable())