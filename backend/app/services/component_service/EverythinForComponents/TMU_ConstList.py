from enum import Enum

from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import KMG
from app.models.ANAMU import ANAKONST


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
    TC_3d_KMG_A = 102
    TC_3d_KMG_K = 103
    TC_3d_KMG_Uc = 104
    TC_3d_KMG_alphaM = 105
    TC_3d_KMG_Tm = 106
    TC_3d_KMG_deltaTm = 107
    TC_3d_KMG_alphaW = 108
    TC_3d_KMG_Tw = 109
    TC_3d_KMG_deltaTw = 110
    TC_3d_DUME_D = 111
    TC_3d_DUME_alpha = 112
    TC_3d_DUME_l = 113
    TC_3d_FORM_L = 114
    TC_3d_FORM_DL = 115
    TC_3d_FORM_F = 116
    TC_3d_ABST_L = 117
    TC_3d_ABST_LM1 = 118
    TC_3d_ABST_LE1 = 119
    TC_3d_ABST_LM2 = 120
    TC_3d_ABST_LE2 = 121
    TC_3d_Ri_LA = 122
    TC_3d_Ri_Alpha = 123
    TC_3d_Ri_LME = 124
    TC_3d_Ri_LE = 125
    TC_3d_Ri_LMB = 126
    TC_3d_Sym_DE = 127
    TC_3d_Sym_LE = 128
    TC_3d_Sym_DB = 129
    TC_3d_Sym_LMB = 130
    TC_3d_Koax_DE = 131
    TC_3d_Koax_LE = 132
    TC_3d_Koax_LA = 133
    TC_3d_Koax_DB = 134
    TC_3d_Koax_LB = 135
    TC_3d_Koax_LMB = 136
    TC_3d_KoaxGA_DE = 137
    TC_3d_KoaxGA_LME = 138
    TC_3d_KoaxGA_LE = 139
    TC_3d_KoaxGA_LB = 140
    TC_3d_KMG_LT = 141
    TC_3d_DUME_LM = 142
    TC_3D_DUME_LS = 143
    TC_3D_ABST_LTE = 144
    TC_3D_ABST_LTB = 145
    TC_3d_Ri_LTE1 = 146
    TC_3d_Ri_LTE2 = 147
    TC_3d_Ri_LTB1 = 148
    TC_3d_Ri_LTB2 = 149
    TC_3d_Sym_LME = 150
    TC_3d_Sym_LB = 151
    TC_3d_Sym_LTE = 152
    TC_3d_Sym_LTB = 153
    TC_3d_Koax_LME = 154
    TC_3d_Koax_LT_entfaellt = 155
    TC_3d_Koax_LTB = 156
    TC_3d_Koax_LTE = 157
    TC_3d_KoaxGA_LA = 158
    TC_3d_KoaxGA_LTB = 159
    TC_3d_KoaxGA_LTE = 160
    TC_3d_KMG_MpeML = 161
    TC_Gewinde_Steigung = 162
    TC_3D_NennLaenge_LD = 163
    TC_3d_FORM_FN = 164
    TC_3d_FORM_FKMG = 165
    TC_3d_KMG_AUFLOES = 166
    TC_3d_PktPkt_dist = 167
    TC_3d_PktPkt_Wechsel = 168
    TC_3d_PktPkt_nTastBe = 169
    TC_3d_PktPkt_nTastTe = 170
    TC_3d_PktPkt_SigBe = 171
    TC_3d_PktPkt_SigTe = 172
    TC_3d_PktPkt_ScanKgl = 173
    TC_3d_PktPkt_MBe = 174
    TC_3d_PktPkt_Mte = 175
    TC_3d_PktPkt_Temp = 176
    TC_3d_PktPkt_Gamma0 = 177
    TC_3d_PktPkt_Gamma1 = 178
    TC_3d_PktPkt_WinkelSeg_BE = 179
    TC_3d_PktPkt_WinkelSeg_TE = 180
    TC_3d_PktPkt_AnzSims = 181
    TC_3d_PktPkt_Dia_BE = 182
    TC_3d_PktPkt_Dia_TE = 183
    TC_3d_KMG_AmpX = 184
    TC_3d_KMG_AmpY = 185

    def add_by_value(self, value: int):
        try:
            konst = TKompConstants(value)  # Enum-Zugriff über den Wert (int)
            return konst
        except ValueError:
            print(f"Ungültiger Wert: {value} ist kein gültiger TKompConstants-Eintrag")

    def add_by_name(self, name: str):
        try:
            # Enum-Zugriff über den Namen (string)
            konst = TKompConstants[name]
            return konst
        except KeyError:
            print(f"Ungültiger Name: {name} ist kein gültiger TKompConstants-Eintrag")


class TMU_ConstList(BaseModel):
    const_map: dict[TKompConstants, float] = {}

    @field_validator("const_map", mode="before")
    @classmethod
    def parse_const_map(cls, v):
        # Falls Keys als Strings ankommen
        if isinstance(v, dict):
            new_map = {}
            for k, val in v.items():
                if isinstance(k, str):
                    try:
                        enum_key = TKompConstants[k]
                    except KeyError:
                        raise ValueError(f"Ungültiger Schlüssel: {k}")
                else:
                    enum_key = k
                new_map[enum_key] = float(val)
            return new_map
        raise ValueError("const_map muss ein Dictionary sein")

    async def load_constants(self, anamu_id: int, db: AsyncSession):
        print("reached it")
        stmt = select(ANAKONST).where(ANAKONST.fk_anamu == anamu_id)
        result = await db.execute(stmt)
        constants = result.scalars().all()  # GIBT MODELLE, keine Tupel

        for const in constants:
            try:
                enum_key = TKompConstants(const.constnum)
                self.const_map[enum_key] = const.constval
            except ValueError:
                print(f"Unbekannter constnum {const.constnum} → nicht im Enum enthalten")




    async def load_kmg_constants(self, fk_kmgs: int, db: AsyncSession):
        stmt = select(KMG).where(KMG.id == fk_kmgs)
        result = await db.execute(stmt)
        kmg = result.scalar_one_or_none()

        if not kmg:
            print("Kein KMG gefunden für ANAMU", fk_kmgs)
            return

        for enum_key, attr_name in KMG_ENUM_MAPPING.items():
            value = getattr(kmg, attr_name, None)
            if value is not None:
                self.const_map[enum_key] = value
                print(f"Setze Konstante {enum_key.name} ({enum_key.value}) = {value}")
            else:
                print(f"Attribut {attr_name} nicht vorhanden oder leer im KMG")

    class Config:
        use_enum_values = False
        json_encoders = {TKompConstants: lambda v: v.name}


KMG_ENUM_MAPPING = {
    TKompConstants.TC_3d_KMG_A: "kmg_a",
    TKompConstants.TC_3d_KMG_K: "kmg_k",
    TKompConstants.TC_3d_KMG_Uc: "kmg_uc",
    TKompConstants.TC_3d_KMG_alphaM: "kmg_alpha_m",
    TKompConstants.TC_3d_KMG_LT: "kmg_lt",
    TKompConstants.TC_3d_KMG_MpeML: "kmg_mpeml",
}


parameter_mapping = {
    TKompConstants.TC_Messbereich: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Nennmass: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_ObAbmass: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_UntAbmass: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Einheit: {'einheit': '', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Messwert: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_MesskraftME: {'einheit': 'N', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_MesskraftSchwankungME: {'einheit': 'N', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_TempME: {'einheit': '°C', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_TempMO: {'einheit': '°C', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_TempEN: {'einheit': '°C', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_AusdehnKoeffME: {'einheit': '1/°K', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_AusdehnKoeffMO: {'einheit': '1/°K', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_AusdehnKoeffEN: {'einheit': '1/°K', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_DurchmesserMessflaeche: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_DurchmesserMesseinsatzME: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_BreiteMessflaecheMO: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_BreiteMessflaecheEN: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_FaktorKennlinieME: {'einheit': '', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_ParameterKennlinieME: {'einheit': 'µm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_NichtLinearKennlinieME: {'einheit': 'µm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_MantellinieMO: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_MantellinieME: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_MantellinieEN: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_NennmassEN: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_ZeitDeltaMessungEN_MO: {'einheit': 'min', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_ZeitDrift: {'einheit': 'µm/min', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_DurchmesserEN: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Winkelabweichung_von_90_Grad: {'einheit': '°', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Radius_der_Zone_des_Spiels: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Laenge_kurze_Kante_PEM: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Tol_Abw_Spanne_ISO_3650: {'einheit': 'µm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Elast_Modul_Normal: {'einheit': 'N/m²', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Elast_Modul_MO: {'einheit': 'N/m²', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Poisson_Koeff_Normal: {'einheit': '', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Poisson_Koeff_MO: {'einheit': '', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Korrelationskoeffizient: {'einheit': '', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Schrittweite_Geradheitskalibrierung_EN: {'einheit': 'mm', 'übersetzung': ' Schrittweite bei der Geradheitskalibrierung des EN', 'kategorie': ''},
    TKompConstants.TC_Positionsgenauigkeit_Kalibrierung_MO: {'einheit': 'mm', 'übersetzung': ' Positionsgenauigkeit bei Kalibrierung des MO', 'kategorie': ''},
    TKompConstants.TC_Betrag_max_Abweichung_Bezugsgerade: {'einheit': 'µm', 'übersetzung': ' Betrag der maximalen Abweichung von der Bezugsgerade', 'kategorie': ''},
    TKompConstants.TC_Laenge_stehender_Schenkel_EN: {'einheit': 'mm', 'übersetzung': ' Länge des stehenden Schenkels (EN)', 'kategorie': ''},
    TKompConstants.TC_Abstand_Stuetzpunkte_EN: {'einheit': 'mm', 'übersetzung': ' Abstand der Stützpunkte am EN', 'kategorie': ''},
    TKompConstants.TC_Geradheit_Messplatte_EN: {'einheit': 'µm', 'übersetzung': ' Geradheit der Messplatte im Bereich des EN', 'kategorie': ''},
    TKompConstants.TC_Positionsabweichung_Stuetzpunkte_EN: {'einheit': 'mm', 'übersetzung': ' Positionsabweichung der Stützpunkte des EN', 'kategorie': ''},
    TKompConstants.TC_Kalibrierung_Geradheit_EN: {'einheit': 'µm', 'übersetzung': ' Kalibrierung der Geradheit des EN', 'kategorie': ''},
    TKompConstants.TC_Laenge_stehender_Schenkel_MO: {'einheit': 'mm', 'übersetzung': ' Länge des stehenden Schenkels des MO', 'kategorie': ''},
    TKompConstants.TC_Stuetzpunktabstand_MO: {'einheit': 'mm', 'übersetzung': ' Stützpunktabstand des MO', 'kategorie': ''},
    TKompConstants.TC_Geradheit_Messplatte_MO: {'einheit': 'µm', 'übersetzung': ' Geradheit der Messplatte im Bereich des MO', 'kategorie': ''},
    TKompConstants.TC_Positionsabweichung_Stuetzpunkte_MO: {'einheit': 'mm', 'übersetzung': ' Positionsabweichung der Stützpunkte des MO', 'kategorie': ''},
    TKompConstants.TC_Kalibrierung_Geradheit_MO: {'einheit': 'µm', 'übersetzung': ' Kalibrierung der Geradheit des MO', 'kategorie': ''},
    TKompConstants.TC_Kalibrierung_Ebenheit_Messplatte: {'einheit': 'µm', 'übersetzung': ' Kalibrierung der Ebenheit der Messplatte', 'kategorie': ''},
    TKompConstants.TC_Positionsgenauigkeit_Stuetzpunkte: {'einheit': 'mm', 'übersetzung': ' Positionsgenauigkeit der Stützpunkte', 'kategorie': ''},
    TKompConstants.TC_Schrittweite_Geradheitskalibrierung_MO: {'einheit': 'mm', 'übersetzung': ' Schrittweite bei Geradheitskalibrierung des MO', 'kategorie': ''},
    TKompConstants.TC_Hoehendifferenz_Stuetzpunkte: {'einheit': 'mm', 'übersetzung': ' H÷hendifferenz der Stützpunkte', 'kategorie': ''},
    TKompConstants.TC_Laenge_Messobjekt: {'einheit': 'mm', 'übersetzung': ' Länge des Messobjekts', 'kategorie': ''},
    TKompConstants.TC_Anzahl_Verschiebungen_MO: {'einheit': '', 'übersetzung': ' Anzahl der Verschiebungen des MO', 'kategorie': ''},
    TKompConstants.TC_Messbereichsendwert_Messeinrichtung: {'einheit': 'mm', 'übersetzung': ' Messbereichsendwert der Messeinrichtung', 'kategorie': ''},
    TKompConstants.TC_Hoehe_zu_Rechtwinkligkeit: {'einheit': 'mm', 'übersetzung': ' Zur Rechtwinkligkeit geh÷rende H÷he', 'kategorie': ''},
    TKompConstants.TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke: {'einheit': '', 'übersetzung': ' Anzahl Messwerte pro Teilmessstrecke', 'kategorie': ''},
    TKompConstants.TC_Rh_Anzahl_Teilmessstrecken: {'einheit': '', 'übersetzung': ' Anzahl  Teilmessstrecken', 'kategorie': ''},
    TKompConstants.TC_Rh_Ortabhaengige_Unsicherheit_in_y: {'einheit': 'mm', 'übersetzung': ' Ortsabhängige Unsicherheit in y-Richtung', 'kategorie': ''},
    TKompConstants.TC_Rh_Gradient_in_Rillenrichtung: {'einheit': 'µm/mm', 'übersetzung': ' Gradient in Rillenrichtung', 'kategorie': ''},
    TKompConstants.TC_Rh_Messpunktabstand: {'einheit': 'µm', 'übersetzung': ' Messpunktabstand', 'kategorie': ''},
    TKompConstants.TC_Rh_Tiefpasswellenlaengen: {'einheit': 'µm', 'übersetzung': ' Tiefpasswellenlängen', 'kategorie': ''},
    TKompConstants.TC_Rh_Kennwertaenderungsfaktor: {'einheit': '', 'übersetzung': ' Tastspitzenabhängige Kennwertänderung', 'kategorie': ''},
    TKompConstants.TC_Rh_Gemessene_Kenngroesse: {'einheit': 'µm', 'übersetzung': ' Gemessener Kennwert', 'kategorie': ''},
    TKompConstants.TC_Rh_Anzahl_Wiederholungsmessungen_geaenderter_Antastort: {'einheit': '', 'übersetzung': ' Anzahl Wiederholmessungen bei unterschiedlichen Antastorten', 'kategorie': ''},
    TKompConstants.TC_Rh_Anzahl_Wiederholmessungen_selber_Antastort: {'einheit': '', 'übersetzung': ' Anzahl Wiederholmessungen am selben Antastort', 'kategorie': ''},
    TKompConstants.TC_Fm_Anzahl_Wiederholmessungen_StreuungAnzeige: {'einheit': '', 'übersetzung': ' Anzahl Messungen (Streuung der Anzeige)', 'kategorie': ''},
    TKompConstants.TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten: {'einheit': 'µm', 'übersetzung': ' Abstand zwischen zwei benachbarten Profilpunkten', 'kategorie': ''},
    TKompConstants.TC_Fm_Grenzwellenlaenge: {'einheit': 'µm', 'übersetzung': ' Grenzwellenlänge', 'kategorie': ''},
    TKompConstants.TC_Fm_Messwert_MO: {'einheit': 'µm', 'übersetzung': ' Richtiger Wert des Vergr÷ßerungsnormals', 'kategorie': ''},
    TKompConstants.TC_Fm_Richtiger_Wert_Rundheit_Kugelnormal: {'einheit': 'µm', 'übersetzung': ' Richtiger Wert der Rundheit des Kugelnormals', 'kategorie': ''},
    TKompConstants.TC_Fm_Messunsicherheit_der_Kalibrierung_Kugelnormal: {'einheit': 'µm', 'übersetzung': ' Messunsicherheit der Kalibrierung von Kugelnormal', 'kategorie': ''},
    TKompConstants.TC_Fm_Gemessenden_Exzentrizitaet: {'einheit': 'mm', 'übersetzung': ' Gemessenden Exzentrizität', 'kategorie': ''},
    TKompConstants.TC_Fm_Aussendurchmesser_MO: {'einheit': 'mm', 'übersetzung': ' Außendurchmesser des MO', 'kategorie': ''},
    TKompConstants.TC_Fm_Tastkugeldurchmesser: {'einheit': 'mm', 'übersetzung': ' Tastkugeldurchmesser', 'kategorie': ''},
    TKompConstants.TC_Fm_Innendurchmesser_MO: {'einheit': 'mm', 'übersetzung': ' Innendurchmesser des MO', 'kategorie': ''},
    TKompConstants.TC_Fm_Kippung_MO_XAchse: {'einheit': 'µm/10mm', 'übersetzung': ' Kippung des MO zu X-Achse', 'kategorie': ''},
    TKompConstants.TC_Fm_Kippung_MO_YAchse: {'einheit': 'µm/10mm', 'übersetzung': ' Kippung des MO zu Y-Achse', 'kategorie': ''},
    TKompConstants.TC_Fm_Radius_MO: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_Fm_Neigung_Zylinderachse_MO_zu_Flaeche_XOY: {'einheit': 'Grad', 'übersetzung': ' Neigung der Zylinderachse des MO zu Fläche XOY', 'kategorie': ''},
    TKompConstants.TC_Fm_Formabweichung_Normal: {'einheit': 'µm', 'übersetzung': ' Formabweichung des Normals', 'kategorie': ''},
    TKompConstants.TC_Fm_Kalibrierung_Normal: {'einheit': 'µm', 'übersetzung': ' Kalibrierung des Normals (Messunsicherheit)', 'kategorie': ''},
    TKompConstants.TC_Fm_Standardabweichung_Wiederholmessungen_Normal: {'einheit': 'µm', 'übersetzung': ' Standardabweichung der Wiederholmessungen des Normals', 'kategorie': ''},
    TKompConstants.TC_Fm_AnzahlMessungen_Fuehrungsabweichung: {'einheit': '', 'übersetzung': ' Anzahl Messungen (Führungabweichung)', 'kategorie': ''},
    TKompConstants.TC_Fm_Gemessene_Rundheit_EN: {'einheit': 'µm', 'übersetzung': ' Gemessene Rundheit des Kugelnormals (EN)', 'kategorie': ''},
    TKompConstants.TC_Gewinde_Steigung: {'einheit': 'mm', 'übersetzung': ' Gewindesteigung', 'kategorie': ''},
    TKompConstants.TC_KTMG_Gemessener_Abstand: {'einheit': 'mm', 'übersetzung': ' Gemessener Abstand (< 100 mm)', 'kategorie': ''},
    TKompConstants.TC_KTMG_Konstanter_Anteil_EMPE: {'einheit': 'µm', 'übersetzung': ' Konstanter Anteil A des Grenzwerts E(MPE) der Längenmessabw.', 'kategorie': ''},
    TKompConstants.TC_KTMG_Anzahl_Messpunkte: {'einheit': '', 'übersetzung': ' Anzahl der Messpunkte', 'kategorie': ''},
    TKompConstants.TC_KTMG_Gemessener_Winkel: {'einheit': 'Grad', 'übersetzung': ' Gemessener Winkel', 'kategorie': ''},
    TKompConstants.TC_KTMG_Laenge_kleinster_Schenkel: {'einheit': 'mm', 'übersetzung': ' Länge des kleinsten Schenkels (kleiner 100 mm)', 'kategorie': ''},
    TKompConstants.TC_KTMG_Gemessene_Geradheit: {'einheit': 'µm', 'übersetzung': ' Gemessene Geradheit', 'kategorie': ''},
    TKompConstants.TC_KTMG_Sektor_Kreis: {'einheit': 'Grad', 'übersetzung': ' Kreisabschnitt', 'kategorie': ''},
    TKompConstants.TC_3d_KMG_A: {'einheit': '', 'übersetzung': ' Konstanter Teil A des Grenzwertes MPE(E) der Längenmessabw.', 'kategorie': '5'},
    TKompConstants.TC_3d_KMG_K: {'einheit': '', 'übersetzung': ' Faktor K des Grenzwertes der Längenmeßabw. MPE(E)=(A+L/K) µm', 'kategorie': '5'},
    TKompConstants.TC_3d_KMG_LT: {'einheit': 'mm', 'übersetzung': ' Tasterlänge für spezifizierte Mehrfachtaster-Lageabweichung (LT)', 'kategorie': '5'},
    TKompConstants.TC_3d_KMG_Uc: {'einheit': 'µm', 'übersetzung': ' Kalibrierunsicherheit des Kugelnormal-Durchmessers (µm) - U(C)', 'kategorie': '5'},
    TKompConstants.TC_3d_KMG_alphaM: {'einheit': '10-6/K', 'übersetzung': ' Ausdehnungskoeffizient der KMG-Maßstäbe (10-6/K) - Alpha M', 'kategorie': '5'},
    TKompConstants.TC_3d_KMG_MpeML: {'einheit': 'µm', 'übersetzung': ' Grenzwert für Mehrtaster-Lageabweichung MPE(ML)', 'kategorie': '5'},
    TKompConstants.TC_3d_KMG_Tm: {'einheit': '°C', 'übersetzung': ' Mittlere Temperatur der KMG-Maßstäbe (°C) - tM', 'kategorie': '4'},
    TKompConstants.TC_3d_KMG_deltaTm: {'einheit': 'K', 'übersetzung': ' Max. Abweichung von der mittleren Temperatur (K) - Maßstab', 'kategorie': '4'},
    TKompConstants.TC_3d_KMG_alphaW: {'einheit': '10-6/K', 'übersetzung': ' Ausdehnungskoeffizient des Werkstücks (10-6/K)', 'kategorie': '4'},
    TKompConstants.TC_3d_KMG_Tw: {'einheit': '°C', 'übersetzung': ' Mittlere Temperatur des Werkstücks (°C)', 'kategorie': '4'},
    TKompConstants.TC_3d_KMG_deltaTw: {'einheit': 'K', 'übersetzung': ' Max. Abweichung von der mittleren Temperatur (K) - Werkstück', 'kategorie': '4'},
    TKompConstants.TC_3d_DUME_D: {'einheit': 'mm', 'übersetzung': ' Nennmaß des Durchmessers (D)', 'kategorie': '1'},
    TKompConstants.TC_3d_DUME_alpha: {'einheit': '°', 'übersetzung': ' Winkelbereich der Meßpunkte am Umfang (Standard 360°)', 'kategorie': '1'},
    TKompConstants.TC_3d_DUME_l: {'einheit': 'mm', 'übersetzung': ' Zylinder: Länge des Formelements (Gesamtlänge bis Rand)', 'kategorie': '1'},
    TKompConstants.TC_3d_DUME_LM: {'einheit': 'mm', 'übersetzung': ' Kegel: Messlänge (Bereich der Messpunkte)', 'kategorie': '1'},
    TKompConstants.TC_3d_FORM_L: {'einheit': 'mm', 'übersetzung': ' Nennmaß der Länge (gr÷ßere Länge) (L)', 'kategorie': '1'},
    TKompConstants.TC_3d_FORM_DL: {'einheit': 'mm', 'übersetzung': ' Nennmaß der Breite (kleinere Länge) (l)', 'kategorie': '1'},
    TKompConstants.TC_3d_FORM_F: {'einheit': 'µm', 'übersetzung': ' Formabweichung am Normal aufgrund der Tasterbiegung (µm)', 'kategorie': '3'},
    TKompConstants.TC_3d_FORM_FN: {'einheit': 'µm', 'übersetzung': ' Formabweichung (Rundheit) am Normal aus Zertifikat F(N)', 'kategorie': '2'},
    TKompConstants.TC_3d_FORM_FKMG: {'einheit': 'µm', 'übersetzung': ' Formabweichung (Rundheit) am Normal aus Messung F(KMG)', 'kategorie': '2'},
    TKompConstants.TC_3d_ABST_L: {'einheit': 'mm', 'übersetzung': ' Nennmaß des Abstandes (bei Position theoretischens Maß)', 'kategorie': '1'},
    TKompConstants.TC_3d_ABST_LM1: {'einheit': 'mm', 'übersetzung': ' Messlänge am tolerierten Element (Bereich der Messpunkte) - L(ME)', 'kategorie': '1'},
    TKompConstants.TC_3d_ABST_LE1: {'einheit': 'mm', 'übersetzung': ' Abstand des Schwerpunktes von der Nullebene -  L(SE)', 'kategorie': '1'},
    TKompConstants.TC_3d_ABST_LM2: {'einheit': 'mm', 'übersetzung': ' Messlänge am Bezugselement (Bereich der Messpunkte) - L(MB)', 'kategorie': '1'},
    TKompConstants.TC_3d_ABST_LE2: {'einheit': 'mm', 'übersetzung': ' Abstand des Schwerpunktes von der Nullebene - L(SB)', 'kategorie': '1'},
    TKompConstants.TC_3D_ABST_LTE: {'einheit': 'mm', 'übersetzung': ' Tasterlänge E  L(TE)', 'kategorie': '3'},
    TKompConstants.TC_3D_ABST_LTB: {'einheit': 'mm', 'übersetzung': ' Tasterlänge B  L(TB)', 'kategorie': '3'},
    TKompConstants.TC_3d_Ri_LA: {'einheit': 'mm', 'übersetzung': ' Kleinster Abstand des tolerierten Elements vom Bezugselement - L(A)', 'kategorie': '1'},
    TKompConstants.TC_3d_Ri_Alpha: {'einheit': '°', 'übersetzung': ' Nennwert des Winkels (in Grad) - Alpha', 'kategorie': '1'},
    TKompConstants.TC_3d_Ri_LME: {'einheit': 'mm', 'übersetzung': ' Messlänge am tolerierten Element (Bereich der Messpunkte)- L(ME)', 'kategorie': '1'},
    TKompConstants.TC_3d_Ri_LE: {'einheit': 'mm', 'übersetzung': ' Auswertelänge (Länge des tolerierten Elements) - L(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_Ri_LMB: {'einheit': 'mm', 'übersetzung': ' Messlänge am Bezugselements (Bereich der Messpunkte) - L(MB)', 'kategorie': '1'},
    TKompConstants.TC_3d_Ri_LTE1: {'einheit': 'mm', 'übersetzung': ' Tasterlänge 1 L(TE1)', 'kategorie': '3'},
    TKompConstants.TC_3d_Ri_LTE2: {'einheit': 'mm', 'übersetzung': ' Tasterlänge 2 L(TE2)', 'kategorie': '3'},
    TKompConstants.TC_3d_Ri_LTB1: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_3d_Ri_LTB2: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_3d_Sym_DE: {'einheit': 'mm', 'übersetzung': ' Breite bzw. Durchmesser des tolerierten Elements - D(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_Sym_LE: {'einheit': 'mm', 'übersetzung': ' Länge des tolerierten Elements - L(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_Sym_LME: {'einheit': 'mm', 'übersetzung': ' Messlänge am tolerierten Element (Bereich der Messpunkte) - L(ME)', 'kategorie': '1'},
    TKompConstants.TC_3d_Sym_DB: {'einheit': 'mm', 'übersetzung': ' Breite bzw. Durchmesser des Bezugselements - D(B)', 'kategorie': '1'},
    TKompConstants.TC_3d_Sym_LB: {'einheit': 'mm', 'übersetzung': ' Länge des Bezugselements (Länge bis zum Rand) - L(B)', 'kategorie': '1'},
    TKompConstants.TC_3d_Sym_LMB: {'einheit': 'mm', 'übersetzung': ' Messlänge des Bezugselements (Bereich der Messpunkte) - L(MB)', 'kategorie': '1'},
    TKompConstants.TC_3d_Sym_LTE: {'einheit': 'mm', 'übersetzung': ' Tasterlänge E L(TE)', 'kategorie': '3'},
    TKompConstants.TC_3d_Sym_LTB: {'einheit': 'mm', 'übersetzung': ' Tasterlänge B L(TB)', 'kategorie': '3'},
    TKompConstants.TC_3d_Koax_DE: {'einheit': 'mm', 'übersetzung': ' Durchmesser des tolerierten Elements - D(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_LE: {'einheit': 'mm', 'übersetzung': ' Länge des tolerierten Elements - L(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_LA: {'einheit': 'mm', 'übersetzung': ' Gr÷ßter Abstand des tol. Elements zur Mitte des Bezugselements-L(A)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_DB: {'einheit': 'mm', 'übersetzung': ' Gr÷ßter Durchmesser des Bezugselements - D(B)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_LB: {'einheit': 'mm', 'übersetzung': ' Länge des Bezugselements (Gesamtlänge bis zum Rand) -  L(B)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_LMB: {'einheit': 'mm', 'übersetzung': ' Messlänge am Bezugselement (Bereich der Messpunkte) - L(MB)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_LME: {'einheit': 'mm', 'übersetzung': ' Messlänge am tolerierten Element (Bereich der Messpunkte) - L(ME)', 'kategorie': '1'},
    TKompConstants.TC_3d_Koax_LT_entfaellt: {'einheit': 'mm', 'übersetzung': ' -', 'kategorie': ''},
    TKompConstants.TC_3d_Koax_LTB: {'einheit': 'mm', 'übersetzung': ' Tasterlänge B- L(TB)', 'kategorie': '3'},
    TKompConstants.TC_3d_Koax_LTE: {'einheit': 'mm', 'übersetzung': ' Tasterlänge E- L(TE)', 'kategorie': '3'},
    TKompConstants.TC_3d_KoaxGA_DE: {'einheit': 'mm', 'übersetzung': ' Durchmesser des tolerierten Elements - D(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_KoaxGA_LME: {'einheit': 'mm', 'übersetzung': ' Messlänge am tolerierten Element (Bereich der Messpunkte) L(ME)', 'kategorie': '1'},
    TKompConstants.TC_3d_KoaxGA_LE: {'einheit': 'mm', 'übersetzung': ' Auswertelänge am tolerierten Element (Länge bis zum Rand) - L(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_KoaxGA_LB: {'einheit': 'mm', 'übersetzung': ' Bezugslänge (Mittenabstand der beiden Bezugselemente) - L(E)', 'kategorie': '1'},
    TKompConstants.TC_3d_KoaxGA_LA: {'einheit': 'mm', 'übersetzung': '!!! siehe oben  TC_3d_Koax_LA\t\tGr÷ßter Abstand des tol. Elements zur Mitte des Bezugselements-L(A)', 'kategorie': '1'},
    TKompConstants.TC_3d_KoaxGA_LTB: {'einheit': 'mm', 'übersetzung': '!!!=  TC_3d_Koax_LTB\t\tTasterlänge B- L(TB)', 'kategorie': '3'},
    TKompConstants.TC_3d_KoaxGA_LTE: {'einheit': 'mm', 'übersetzung': '!!!= TC_3d_Koax_LTE\t\tTasterlänge E- L(TE)', 'kategorie': '3'},
    TKompConstants.TC_3D_NennLaenge_LD: {'einheit': 'mm', 'übersetzung': '\tNennmaß der Länge bzw. Durchmessers L(D)', 'kategorie': '1'},
    TKompConstants.TC_3d_KMG_AUFLOES: {'einheit': '°', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_dist: {'einheit': 'mm', 'übersetzung': '', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_Wechsel: {'einheit': 'ja/nein', 'übersetzung': 'Tasterwechsel', 'kategorie': '3'},
    TKompConstants.TC_3d_PktPkt_nTastBe: {'einheit': '', 'übersetzung': 'Anzahl Antastungen Bezugselement', 'kategorie': '2'},
    TKompConstants.TC_3d_PktPkt_nTastTe: {'einheit': '', 'übersetzung': 'Anzahl Antastungen toleriertes Element', 'kategorie': '2'},
    TKompConstants.TC_3d_PktPkt_SigBe: {'einheit': 'mm', 'übersetzung': 'Standardabweichung bei Antastung des BE', 'kategorie': '2'},
    TKompConstants.TC_3d_PktPkt_SigTe: {'einheit': 'mm', 'übersetzung': 'Standardabweichung bei Antastung des TE', 'kategorie': '2'},
    TKompConstants.TC_3d_PktPkt_ScanKgl: {'einheit': 'Grad', 'übersetzung': 'Bereich zum Scannen von Kugeln', 'kategorie': '1'},
    TKompConstants.TC_3d_PktPkt_MBe: {'einheit': 'W/L', 'übersetzung': 'Maximale Harmonik des Profils des BE . Apriori', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_Mte: {'einheit': 'W/L', 'übersetzung': 'Maximale Harmonik des Profils des BE . Apriori', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_Temp: {'einheit': '°C', 'übersetzung': 'Raumtemperatur', 'kategorie': '4'},
    TKompConstants.TC_3d_PktPkt_Gamma0: {'einheit': 'mm', 'übersetzung': 'Koeff fόr ZufAbw aufgrund Winkel de Sektor', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_Gamma1: {'einheit': 'Grad', 'übersetzung': 'Koeff fόr ZufAbw aufgrund Winkel de Sektor', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_WinkelSeg_BE: {'einheit': 'Grad', 'übersetzung': 'Winkel Antastbereich (Segment) BE', 'kategorie': '1'},
    TKompConstants.TC_3d_PktPkt_WinkelSeg_TE: {'einheit': 'Grad', 'übersetzung': 'Winkel Antastbereich (Segment) tolerirtes Element', 'kategorie': '1'},
    TKompConstants.TC_3d_PktPkt_AnzSims: {'einheit': '', 'übersetzung': 'Anzahl Simulationen pro Messpunkt', 'kategorie': ''},
    TKompConstants.TC_3d_PktPkt_Dia_BE: {'einheit': 'mm', 'übersetzung': 'Durchmesser Kreis 1 BE', 'kategorie': '1'},
    TKompConstants.TC_3d_PktPkt_Dia_TE: {'einheit': 'mm', 'übersetzung': 'Durchmesser Kreis 2 BE', 'kategorie': '1'},
    TKompConstants.TC_3d_KMG_AmpX: {'einheit': 'mm', 'übersetzung': 'Amplidude Streuung X', 'kategorie': ''},
    TKompConstants.TC_3d_KMG_AmpY: {'einheit': 'mm', 'übersetzung': 'Amplidude Streuung Y', 'kategorie': ''},
}

def export_ts_mapping(mapping: dict, filename: str = "tcParameterMapping.ts"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("export const tcMapping: Record<number, {\n")
        f.write("  key: string,\n")
        f.write("  einheit: string,\n")
        f.write("  übersetzung: string,\n")
        f.write("  kategorie: number\n")
        f.write("}> = {\n")

        for enum_key, data in mapping.items():
            key_id = enum_key.value
            key_str = enum_key.name
            einheit = data.get('einheit', '')
            übersetzung = data.get('übersetzung', '')
            try:
                kategorie = int(data.get('kategorie', 0))
            except (ValueError, TypeError):
                kategorie = 0

            f.write(
                f"  {key_id}: {{ key: \"{key_str}\", einheit: \"{einheit}\", "
                f"übersetzung: \"{übersetzung}\", kategorie: {kategorie} }},\n"
            )

        f.write("};\n")
    print(f"✅ Datei '{filename}' erfolgreich erstellt.")

if __name__ == "__main__":
    export_ts_mapping(parameter_mapping)