import math
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union, Set

from app.services.component_service.EverythinForComponents import TMU_Atom

from app.services.component_service.EverythinForComponents.TMU_ConstList import TMU_ConstList

from app.services.component_service.component_factory import ComponentFactory

from app.services.component_service.component_abstract import TMU_Komponente

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from pydantic import BaseModel
from sqlalchemy.orm.instrumentation import instance_state


# Definiere Enum für die zulässigen Prozess-Typen
class TMU_AufgabeModell(Enum):
    aPruefprozess = 'aPruefprozess'
    aKalibrierprozess = 'aKalibrierprozess'
    a3D_Pruefprozess = 'a3D_Pruefprozess'
    aUnbekannt = 'aUnbekannt'
# Konstanten
MU_NAN = float('nan')

# Hilfsfunktionen, um die Berechnungen zu ermöglichen
def power(value, exp):
    return value ** exp if not math.isnan(value) else MU_NAN

@dataclass
class TMU_Winkel:
    flag: bool
    data: Union[int, tuple]

    def __init__(self, flag: bool, value):
        self.flag = flag
        if flag:
            if isinstance(value, int):
                self.data = value  # Speichert `l` als Integer
            else:
                raise ValueError("Bei flag=True muss ein Integer übergeben werden.")
        else:
            if isinstance(value, tuple) and len(value) == 4:
                self.data = value  # Speichert die 4 Bytes als Tuple
            else:
                raise ValueError("Bei flag=False müssen genau 4 Byte-Werte übergeben werden.")

class TMU_Geometry(Enum):
    Geometrie_undefiniert = 0
    Flaeche = 1
    Kugel = 2
    Zylinder = 3
    HohlZylinder = 4  # Hohlzylinder wurde hinzugefügt



class TMU_3DElement(Enum):
    E3D_NDEF = 0
    E3D_Punkt = 1
    E3D_Gerade = 2
    E3D_Ebene = 3
    E3D_Kreis = 4
    E3D_Halbkugel = 5
    E3D_Zylinder = 6
    E3D_Kegel = 7


from typing import List, Optional
from datetime import datetime


# Assuming the other classes like TMU_ConstList, TMU_Atom, TMU_Winkel, etc., are defined elsewhere in Python
class TMU_ModellSchema(BaseModel):
    aufgabe: int
    modell_id: int
    mit_berechnung_toleranzfaktor: bool = False
    const_list: TMU_ConstList = TMU_ConstList()  # Angenommen, du hast eine Klasse TMU_ConstList, die du hier als Option mitgeben kannst
    modell_name: str = ""
    AufgabeModell: Optional[TMU_AufgabeModell] = None  # Kannst du nach Bedarf definieren
    i_aufgabe: int = 0
    i_geometrie_me: int = 0
    i_geometrie_en: int = 0
    i_geometrie_mo: int = 0
    i_bezug1: int = 0
    i_bezug2: int = 0
    read_only: bool = False
    modell_desc: str = ""
    methode: int = 0
    gegenstand: int = 0
    mess_einsatz: int = 0
    einstellmass: int = 0
    modell_created: datetime = datetime.now()
    modell_modified: datetime = datetime.now()
    archiv: bool = False
    formel_anteil: str = ""
    formel_beschreibung: str = ""
    const_needed: Set[TKompConstants] = set()  # Liste von TKompConstants

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class TMU_Modell(List[TMU_Komponente]):
    def __init__(self, schema: TMU_ModellSchema):
        super().__init__()
        self.mit_berechnung_toleranzfaktor = schema.mit_berechnung_toleranzfaktor
        self.aufgabe = schema.aufgabe
        self.modell_name = schema.modell_name
        self.modell_id = schema.modell_id
        self.AufgabeModell = schema.AufgabeModell
        self.i_aufgabe = schema.i_aufgabe
        self.i_geometrie_me = schema.i_geometrie_me
        self.i_geometrie_en = schema.i_geometrie_en
        self.i_geometrie_mo = schema.i_geometrie_mo
        self.i_bezug1 = schema.i_bezug1
        self.i_bezug2 = schema.i_bezug2
        self.read_only = schema.read_only
        self.modell_desc = schema.modell_desc
        self.methode = schema.methode
        self.gegenstand = schema.gegenstand
        self.mess_einsatz = schema.mess_einsatz
        self.einstellmass = schema.einstellmass
        self.modell_created = schema.modell_created
        self.modell_modified = schema.modell_modified
        self.archiv = schema.archiv
        self.formel_anteil = schema.formel_anteil
        self.formel_beschreibung = schema.formel_beschreibung
        self.const_needed = schema.const_needed
        self.const_list = schema.const_list


    def addComponent(self, component_id: int):
        self.append(ComponentFactory.get_component(self, component_id))


    def SetBerechnungToleranzfaktor(self, ja: bool):
        self.mit_berechnung_toleranzfaktor = ja

    def Clear(self):
        self.Constlist.clear()
        self.iGeometrie_ME = 0  # Corresponds to ord(Flaeche)
        self.iGeometrie_MO = 0
        self.iGeometrie_EN = 0  # Corresponds to ord(Geometrie_undefiniert)
        self.Winkel['l'] = 0
        self.iBezug1 = 0
        self.iBezug2 = 0

    def AddKompwithID(self, kompID: int):
        # Dynamically creates components based on the ID
        component_map = {
            1001: "TK_KalibrierungME",
            1002: "TK_ErmittelteMessabweichungME",
            1003: "TK_AufloesungME",
            1004: "TK_BiegungME",
            1005: "TK_Ebenheit_1_2_ME",
            1006: "TK_Ebenheit_1_2_MO",
            1007: "TK_ParallelitaetMessflaechenME",
            1008: "TK_KorrParallelitaet_MO",
            1009: "TK_TempDifferenz_MO_ME",
            1010: "TK_AbweichungMittlereTemp_MO_ME",
            1011: "TK_VerformungMO",
            1012: "TK_Korr_Biegung_ME",
            1013: "TK_RundheitMessflaeche_1_2_MO",
            1014: "TK_Zylindrizitaet_MO_1_2",
            1015: "TK_Korr_Zylin_ME_1_2",
            1016: "TK_Korr_Zylin_GN_1_2",
            1017: "TK_Korr_Rundheit_ME_1_2",
            1018: "TK_Korr_Rundheit_EN_1_2",
            1019: "TK_Korr_Rundheit_GN_1_2",
            1020: "TK_Korr_Ebenheit_1_2",
            1021: "TK_Korr_Parallelitaet_EN",
            1022: "TK_Verformung_MOsph_MEplan",
            1023: "TK_Verformung_MOsph_MEsph",
            1024: "TK_Verformung_MOzyl_MEsph",
            1025: "TK_Aufloesung_ME_Einstell",
            1026: "TK_Abweichung_Nennmass_EN",
            1027: "TK_Kalibrierung_EN",
            1028: "TK_Korr_TempDifferenz_EN_ME",
            1029: "TK_Korr_TempDifferenz_EN_ME_20",
            1030: "TK_Kalibrierung_GN",
            1031: "TK_Drift_GN",
            1032: "TK_Korr_Abplattung_Messkraft",
            10321: "TK_Korr_Abplattung_Messkraft_ME_MO",
            10322: "TK_Korr_Abplattung_Messkraft_ME_GN",
            10323: "TK_Korr_Abplattung_Messkraft_ME_BN",
            1033: "TK_Kalibrierung_Faktor_Kennlinie_ME",
            1034: "TK_Kalibrierung_Parm_Kennlinie_ME",
            1035: "TK_Nichtlinearitaet_Kennlinie_ME",
            1036: "TK_Zeitdrift_ME",
            1037: "TK_Verformung_Differenz_MO_GN",
            1038: "TK_AufloesungMO",
            1039: "TK_AnstellwinkelHebel",
            1040: "TK_Wiederholpraezision",
            1041: "TK_NichtZentrischeAntastung",
            1042: "TK_StreuungMesskraft",
            1043: "TK_AbweichungPoissonKoeffizientMO_EN",
            1044: "TK_AbweichungElastizitaetsModul_MO_EN",
            1045: "TK_Messkraft_3Draht_Methode",
            1046: "TK_KalibrierungMessdraehte",
            1047: "TK_Zylindrizitaet_Messdraehte",
            1048: "TK_GewindeProfilwinkel",
            1049: "TK_Messkraft_2Kugel_Methode",
            1050: "TK_KalibrierungMesskugeln",
            1051: "TK_RundheitMesskugeln",
            1052: "TK_Geradheit_stehender_Schenkel_EN",
            1053: "TK_Geradheit_stehender_Schenkel_MO",
            1054: "TK_Geradheit_liegender_Schenkel_EN",
            1055: "TK_Geradheit_liegender_Schenkel_MO",
            1056: "TK_Neigung_Winkelnormal_EN",
            1057: "TK_Neigung_Messobjekts_MO",
            1059: "TK_Kalibrierung_Geradheit_stehender_Schenkel_EN",
            1060: "TK_Kalibrierung_Geradheit_stehender_Schenkel_MO",
            1061: "TK_Kalibrierung_Geradheit_Hoehenmessgeraets",
            1062: "TK_Geradheitabweichung_Hoehenmessgeraets",
            1063: "TK_Positioniergenauigkeit_Taster_X_Achse",
            1064: "TK_Ebenheit_Messplatte",
            1065: "TK_Kalibrierung_Ebenheit_Messplatte",
            1066: "TK_Geradheit_Schenkelinnenseite",
            1067: "TK_Kalibrierung_Geradheit_Schenkelinnenseite",
            1071: "TK_Strichbreite_EN",
            1072: "TK_Strichbreite_MO",
            1073: "TK_Strichbreite_ME",
            1074: "TK_Winkel_Achsen_MO_ME",
            1075: "TK_Anzahl_Verschiebungen_MO",
            1076: "TK_Kalibrierung_Rechwinkligkeit",
            1077: "TK_Ermittelte_Rechwinkligkeit",
            1078: "TK_Rh_Kalibrierung_Einstellnormal_EN",
            1079: "TK_Rh_Drift_Richtiger_Wert_vom_EN",
            1080: "TK_Rh_Unterschied_Kalibrierort_EN",
            1081: "TK_Rh_Wiederholpraezision_Antastung_MO",
            1082: "TK_Rh_Topografie_MO",
            1083: "TK_Rh_Fuehrungsabweichung",
            1084: "TK_Rh_Drift_Fuehrungsabweichung",
            1085: "TK_Rh_Grundrauschen",
            1086: "TK_Rh_Drift_Grundrauschen",
            1087: "TK_Rh_Verformung_MO",
            1088: "TK_Rh_Abweichung_Tastspitzenradius_vom_Nennwert",
            1089: "TK_Rh_Messunsicherheit_Kalibrierung_Tastspitzenradius",
            1090: "TK_Rh_Unbekannte_systematische_Abweichung",
            1091: "TK_Rh_Kalibrierung_Einstellnormal_EN_TG",
            1092: "TK_Rh_Drift_Richtiger_Wert_von_EN_TG",
            1093: "TK_Rh_Kalibrierort_Kalibrierung_EN_TG",
            1094: "TK_Rh_Wiederholpraezision_Antastung_TG",
            1095: "TK_Rh_Fuehrungsabweichung_TG",
            1096: "TK_Rh_Grundrauschen_TG",
            1097: "TK_Rh_Verformung_EN_TG",
            1098: "TK_Rh_Abweichung_Tastspitzenradius_Nennwert",
            1099: "TK_Rh_Messunsicherheit_Kalibrierung_Tastspitzenradius_TG",
            1100: "TK_Fm_Streuung_Anzeige_ME_in_jedem_Profilpunkt",
            1101: "TK_Fm_Homogenitaet_MO",
            1102: "TK_Fm_Reinigung_MO",
            1103: "TK_Fm_Dynamische_Eingenschaften_ME",
            1104: "TK_Fm_Rauschen_ME",
            1105: "TK_Fm_Streuung_Empfindlichkeit_ME",
            1106: "TK_Fm_Unsicherheit_Vergroesserungsnormal",
            1107: "TK_Fm_Streuung_Spindel_ME",
            1108: "TK_Fm_Linearitaet_ME",
            1109: "TK_Fm_Hysterese_ME",
            1110: "TK_Fm_Exzentrizitaet_MO_Aus",
            1111: "TK_Fm_Exzentrizitaet_MO_Inn",
            1112: "TK_Fm_Nivellierung_Zylinderachse_MO_Rund",
            1113: "TK_Fm_Nivellierung_Zylinderachse_MO_Gerade",
            1114: "TK_Fm_Deformation_MO",
            1115: "TK_Fm_Fuehrungsabweichung_ME",
            1116: "TK_Fm_Temperatur",
            1117: "TK_Fm_Drift_Empfindlichkeit_ME",
            1118: "TK_Fm_Messabweichung_Kalibrierung_ME_Tastsystem",
            1119: "TK_Fm_Kalibrierung_ME_Tastsystem",
            1121: "TK_KTMG_Abstand_system",
            1122: "TK_KTMG_Abstand_zufall",
            1123: "TK_KTMG_Winkel_system",
            1124: "TK_KTMG_Winkel_zufall",
            1125: "TK_KTMG_Winkel_plastVerform",
            1126: "TK_KTMG_Geradheit_system",
            1127: "TK_KTMG_Geradheit_zufall",
            1128: "TK_KTMG_Radius_system",
            1129: "TK_KTMG_Radius_zufall",
            1130: "TK_KTMG_Winkel_Tastspitzenradius",
            1301: "TK_3d_Dw",
            1302: "TK_3d_deltaDT",
            1303: "TK_3d_deltaDC",
            1304: "TK_3d_DeltaLkmg",
            1305: "TK_3d_Delta_LalphaM",
            1306: "TK_3d_Delta_LalphaW",
            1307: "TK_3d_Delta_L_tM",
            1308: "TK_3d_Delta_L_tW",
            1377: "TK_3d_Delta_L_t",
            1366: "TK_3d_DKegel_alpha",
            1367: "TK_3d_DKegel_LS",
            1309: "TK_3d_Fw",
            1310: "TK_3d_DeltaFT",
            1311: "TK_3d_DeltaFkmg",
            1369: "TK_3dForm_A1",
            1370: "TK_3dForm_A2",
            1312: "TK_3dA_X1",
            1313: "TK_3dA_W1",
            1314: "TK_3dA_DeltaXT1",
            1315: "TK_3dA_DeltaRT1",
            1316: "TK_3dA_X2",
            1317: "TK_3dA_W2",
            1318: "TK_3dA_DeltaXT2",
            1319: "TK_3dA_DeltaRT2",
            1320: "TK_3dA_DeltaDT",
            1321: "TK_3dA_DeltaDC",
            1322: "TK_3dA_DeltaLKMG",
            1323: "TK_3dA_LalphaM",
            1324: "TK_3dA_LalphaW",
            1325: "TK_3dA_LtM",
            1326: "TK_3dA_LtW",
            1368: "TK_3dA_DeltaXTR",
            1327: "TK_3d_Ri_WE",
            1328: "TK_3d_Ri_DeltaXE1",
            1329: "TK_3d_Ri_DeltaXE2",
            1330: "TK_3d_Ri_DeltaXET1",
            1331: "TK_3d_Ri_DeltaXET2",
            1332: "TK_3d_Ri_WB",
            1333: "TK_3d_Ri_DeltaXB1",
            1334: "TK_3d_Ri_DeltaXB2",
            1335: "TK_3d_Ri_DeltaXBT1",
            1336: "TK_3d_Ri_DeltaXBT2",
            1337: "TK_3d_Ri_DeltaEA",
            1338: "TK_3d_Ri_DeltaEKMG",
            1371: "TK_3d_Ri_XTER",
            1372: "TK_3d_Ri_XTBR",
            1376: "TK_3d_Ri_Aj",
            1339: "TK_3d_Sym_XE1",
            1340: "TK_3d_Sym_WE1",
            1341: "TK_3d_Sym_XE2",
            1342: "TK_3d_Sym_WE2",
            1343: "TK_3d_Sym_DeltaXTE",
            1344: "TK_3d_Sym_XB1",
            1345: "TK_3d_Sym_WB1",
            1346: "TK_3d_Sym_XB2",
            1347: "TK_3d_Sym_WB2",
            1348: "TK_3d_Sym_DeltaXTB",
            1349: "TK_3d_Sym_DeltaLkmg",
            1373: "TK_3d_Sym_DeltaXTR",
            1350: "TK_3d_Koax_XE",
            1351: "TK_3d_Koax_WE",
            1352: "TK_3d_Koax_DeltaXTE",
            1353: "TK_3d_Koax_XB1",
            1354: "TK_3d_Koax_WB1",
            1355: "TK_3d_Koax_XB2",
            1356: "TK_3d_Koax_DeltaXTB",
            1357: "TK_3d_Koax_DeltaEKMG",
            1374: "TK_3d_Koax_DeltaXTR",
            1358: "TK_3d_KoaxGA_XE1",
            1359: "TK_3d_KoaxGA_WE",
            1360: "TK_3d_KoaxGA_XE2",
            1361: "TK_3d_KoaxGA_DeltaXTE",
            1362: "TK_3d_KoaxGA_XB1",
            1363: "TK_3d_KoaxGA_XB2",
            1364: "TK_3d_KoaxGA_DeltaXTB",
            1365: "TK_3d_KoaxGA_DeltaLkmg",
            1375: "TK_3d_KoaxGA_DeltaXTR",
            1378: "TK_3d_ResKMG",
            1379: "TK_3d_Wi_WE",
            1380: "TK_3d_Wi_WB",
            1381: "TK_3d_Wi_DeltaEKMG",
            1391: "TK_3d_PktPkt_dPgeo",
            1392: "TK_3d_PktPkt_dPyKMG",
            1393: "TK_3d_PktPkt_dPZuf",
            1394: "TK_3d_PktPkt_dTaster",
            1395: "TK_3d_PktPkt_dAbwTemp",
            1396: "TK_3d_PktPkt_AbwTempAusd",
            1397: "TK_3d_PktPkt_dFormAbwBE",
            1398: "TK_3d_PktPkt_dFormAbwTE",
            1399: "TK_3d_PktPkt_dWinkelSektor",
        }

        # Create the component if ID is recognized, else return a message
        component_class = component_map.get(kompID, None)
        if component_class:
            # Simulate the creation of a component by printing the class name
            print(f"Creating component: {component_class} for ID {kompID}")
            return component_class  # In actual implementation, create an object of the class
        else:
            print(f"Invalid Component ID: {kompID}")
            return None

    def buildConstList(self):
        ConstNeeded = set()

        def AddToList(cid, aEinheit):
            if cid in ConstNeeded:
                self.ConstList.append({
                    'cid': cid,
                    'title': self.getConstTitle(cid),
                    'einheit': aEinheit
                })

        # Leere Liste
        self.ConstList.clear()

        if self.mitBerechnungToleranzFaktor:
            ConstNeeded = {'TC_Nennmass', 'TC_UntAbmass', 'TC_ObAbmass'}
        else:
            ConstNeeded = set()

        if self.AufgabeModell == "a3D_Pruefprozess":
            ConstNeeded.update({
                'TC_3d_KMG_A', 'TC_3d_KMG_K', 'TC_3d_KMG_Uc', 'TC_3d_KMG_alphaM',
                'TC_3d_KMG_LT'
            })

        for komponente in self:
            ConstNeeded.update(komponente.ConstNeeded)

        # Stammdaten
        AddToList('TC_Messbereich', 'mm')
        AddToList('TC_Nennmass', 'mm')
        AddToList('TC_ObAbmass', 'mm')
        AddToList('TC_UntAbmass', 'mm')
        AddToList('TC_Einheit', '')
        AddToList('TC_Messwert', 'mm')
        AddToList('TC_MesskraftME', 'N')
        AddToList('TC_MesskraftSchwankungME', 'N')
        AddToList('TC_TempME', '°C')
        AddToList('TC_TempMO', '°C')
        AddToList('TC_TempEN', '°C')
        AddToList('TC_AusdehnKoeffME', '1/°K')
        AddToList('TC_AusdehnKoeffMO', '1/°K')
        AddToList('TC_AusdehnKoeffEN', '1/°K')
        AddToList('TC_DurchmesserMessflaeche', 'mm')
        AddToList('TC_DurchmesserMesseinsatzME', 'mm')
        AddToList('TC_BreiteMessflaecheMO', 'mm')
        AddToList('TC_BreiteMessflaecheEN', 'mm')
        AddToList('TC_FaktorKennlinieME', '')
        AddToList('TC_ParameterKennlinieME', 'μm')
        AddToList('TC_NichtLinearKennlinieME', 'μm')
        AddToList('TC_MantellinieMO', 'mm')
        AddToList('TC_MantellinieME', 'mm')
        AddToList('TC_MantellinieEN', 'mm')
        AddToList('TC_NennmassEN', 'mm')
        AddToList('TC_ZeitDeltaMessungEN_MO', 'min')
        AddToList('TC_ZeitDrift', 'μm/min')
        AddToList('TC_DurchmesserEN', 'mm')

        # mit 2006.1 er Komponenten
        AddToList('TC_Winkelabweichung_von_90_Grad', '°')
        AddToList('TC_Radius_der_Zone_des_Spiels', 'mm')
        AddToList('TC_Laenge_kurze_Kante_PEM', 'mm')
        AddToList('TC_Tol_Abw_Spanne_ISO_3650', 'μm')
        AddToList('TC_Elast_Modul_Normal', 'N/m²')
        AddToList('TC_Elast_Modul_MO', 'N/m²')
        AddToList('TC_Poisson_Koeff_Normal', '')
        AddToList('TC_Poisson_Koeff_MO', '')
        AddToList('TC_Korrelationskoeffizient', '')

        # ------------------ Die Neuen 2007-03-22
        AddToList('TC_Schrittweite_Geradheitskalibrierung_EN', 'mm')  # 2043
        AddToList('TC_Positionsgenauigkeit_Kalibrierung_MO', 'mm')  # 2044
        AddToList('TC_Betrag_max_Abweichung_Bezugsgerade', 'μm')  # 2045
        AddToList('TC_Laenge_stehender_Schenkel_EN', 'mm')  # 2046
        AddToList('TC_Abstand_Stuetzpunkte_EN', 'mm')  # 2047
        AddToList('TC_Geradheit_Messplatte_EN', 'μm')  # 2048
        AddToList('TC_Positionsabweichung_Stuetzpunkte_EN', 'mm')  # 2049
        AddToList('TC_Kalibrierung_Geradheit_EN', 'μm')  # 2050
        AddToList('TC_Laenge_stehender_Schenkel_MO', 'mm')  # 2051
        AddToList('TC_Stuetzpunktabstand_MO', 'mm')  # 2052
        AddToList('TC_Geradheit_Messplatte_MO', 'μm')  # 2053
        AddToList('TC_Positionsabweichung_Stuetzpunkte_MO', 'mm')  # 2054
        AddToList('TC_Kalibrierung_Geradheit_MO', 'μm')  # 2055
        AddToList('TC_Kalibrierung_Ebenheit_Messplatte', 'μm')  # 2056
        AddToList('TC_Positionsgenauigkeit_Stuetzpunkte', 'mm')  # 2058
        AddToList('TC_Schrittweite_Geradheitskalibrierung_MO', 'mm')  # 2059
        AddToList('TC_Hoehendifferenz_Stuetzpunkte', 'mm')  # 2060
        AddToList('TC_Laenge_Messobjekt', 'mm')  # 2061
        AddToList('TC_Anzahl_Verschiebungen_MO', '')  # 2065
        AddToList('TC_Messbereichsendwert_Messeinrichtung', 'mm')  # 2066
        AddToList('TC_Hoehe_zu_Rechtwinkligkeit', 'mm')  # 2067

        # Formnormal
        AddToList('TC_Fm_Anzahl_Wiederholmessungen_StreuungAnzeige', '')  # 2078
        AddToList('TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten', 'μm')  # 2079
        AddToList('TC_Fm_Grenzwellenlaenge', 'μm')  # 2080
        AddToList('TC_Fm_Messwert_MO', 'μm')  # 2081
        AddToList('TC_Fm_Richtiger_Wert_Rundheit_Kugelnormal', 'μm')  # 2082
        AddToList('TC_Fm_Messunsicherheit_der_Kalibrierung_Kugelnormal', 'μm')  # 2083
        AddToList('TC_Fm_Gemessenden_Exzentrizitaet', 'mm')  # 2084
        AddToList('TC_Fm_Aussendurchmesser_MO', 'mm')  # 2085
        AddToList('TC_Fm_Tastkugeldurchmesser', 'mm')  # 2086
        AddToList('TC_Fm_Innendurchmesser_MO', 'mm')  # 2087
        AddToList('TC_Fm_Kippung_MO_XAchse', 'μm/10mm')  # 2088
        AddToList('TC_Fm_Kippung_MO_YAchse', 'μm/10mm')  # 2089
        AddToList('TC_Fm_Radius_MO', 'mm')  # 2090
        AddToList('TC_Fm_Neigung_Zylinderachse_MO_zu_Flaeche_XOY', 'Grad')  # 2091
        AddToList('TC_Fm_Formabweichung_Normal', 'μm')  # 2092
        AddToList('TC_Fm_Kalibrierung_Normal', 'μm')  # 2093
        AddToList('TC_Fm_Standardabweichung_Wiederholmessungen_Normal', 'μm')  # 2094
        AddToList('TC_Fm_AnzahlMessungen_Fuehrungsabweichung', '')  # 2095
        AddToList('TC_Fm_Gemessene_Rundheit_EN', 'μm')  # 2096
        AddToList('TC_Gewinde_Steigung', 'mm')  # 2097

        # Konturmessgerät
        AddToList('TC_KTMG_Gemessener_Abstand', 'mm')  # 2101
        AddToList('TC_KTMG_Konstanter_Anteil_EMPE', 'μm')  # 2102
        AddToList('TC_KTMG_Anzahl_Messpunkte', '')  # 2103
        AddToList('TC_KTMG_Gemessener_Winkel', 'Grad')  # 2104
        AddToList('TC_KTMG_Laenge_kleinster_Schenkel', 'mm')  # 2105
        AddToList('TC_KTMG_Gemessene_Geradheit', 'μm')  # 2106
        AddToList('TC_KTMG_Sektor_Kreis', 'Grad')  # 2107

        # 3D Technische Daten des KMG
        AddToList('TC_3d_KMG_A', '')  # 2301
        AddToList('TC_3d_KMG_K', '')  # 2302
        AddToList('TC_3d_KMG_LT', 'mm')  # 2340
        AddToList('TC_3d_KMG_Uc', 'μm')  # 2303
        AddToList('TC_3d_KMG_alphaM', '10-6/K')  # 2304
        AddToList('TC_3d_KMG_MPEML', 'μm')  # 2357

        # 3D Konstanten Aufgabe Durchmesser
        AddToList('TC_3d_DUME_D', 'mm')  # 2310
        AddToList('TC_3d_DUME_alpha', '°')  # 2311
        AddToList('TC_3d_DUME_l', 'mm')  # 2312
        AddToList('TC_3d_DUME_LM', 'mm')  # 2341

        # 3D Konstanten Aufgabe Form
        AddToList('TC_3d_FORM_L', 'mm')  # 2313
        AddToList('TC_3d_FORM_DL', 'mm')  # 2314
        AddToList('TC_3d_FORM_F', 'μm')  # 2315
        AddToList('TC_3d_FORM_FN', 'μm')  # 2359
        AddToList('TC_3d_FORM_FKMG', 'μm')  # 2360

        # 3D Konstanten Aufgabe Abstand
        AddToList('TC_3d_ABST_L', 'mm')  # 2316
        AddToList('TC_3d_ABST_LM1', 'mm')  # 2317
        AddToList('TC_3d_ABST_LE1', 'mm')  # 2358

        # Weitere Konstanten wie in Delphi
        AddToList('TC_KMG_Messschwankung', 'μm')  # 2305

    def getConstTitle(self, cid):
        # Simulierter Funktionsaufruf zur Bestimmung des Titels
        return f"Title of {cid}"

    def FindKomp(self, ACompID):
        atom = None
        idx = 0
        while atom is None and idx < self.count:
            if isinstance(self[idx], TMU_Atom) and self[idx].id == ACompID:
                atom = self[idx]
            else:
                idx += 1
        return atom

    def Geometrie_ME(self):
        return TMU_Geometry(self.iGeometrie_ME + 1)

    def Geometrie_MO(self):
        return TMU_Geometry(self.iGeometrie_MO + 1)

    def Geometrie_EN(self):
        return TMU_Geometry(self.iGeometrie_EN + 1)

    def Element1_3d(self):
        return TMU_3DElement(self.iGeometrie_EN)

    def Element2_3d(self):
        return TMU_3DElement(self.iGeometrie_MO)

    def Bezug1_3d(self):
        return TMU_3DElement(self.iBezug1)

    def Bezug2_3d(self):
        return TMU_3DElement(self.iBezug2)

    def WinkelE1_3d(self):
        return self.winkel.Winkel_Element1 + 1

    def WinkelE2_3d(self):
        return self.winkel.Winkel_Element2 + 1

    def WinkelB1_3d(self):
        return self.winkel.Winkel_Bezug1 + 1

    def WinkelB2_3d(self):
        return self.winkel.Winkel_Bezug2 + 1

    def Merkmal_3d(self):
        return self.iGeometrie_ME

    def SummeDerVarianzen(self):
        v = 0
        valid = False
        for item in self:
            if isinstance(item, TMU_Komponente) and item.varianz() != MU_NAN:
                print("meine varianz:",item, item.varianz(),"meine unsicherheit:",item.unsicherheitsbeitrag())
                v += item.varianz()
                valid = True
        return v if valid else MU_NAN

    def StandardUnsicherheit_Uy(self):
        uy = self.SummeDerVarianzen()
        print("varianz",uy)
        return math.sqrt(uy) if uy != MU_NAN else MU_NAN

    def V_eff(self):
        result = MU_NAN
        valid = False
        if self.AufgabeModell == "a3D_Pruefprozess":
            SummeEFG = 0
            U = self.StandardUnsicherheit_Uy()
            for item in self:
                if isinstance(item, TMU_Komponente):
                    vi = item.EffektiverFreiheitsgrad
                    if vi != MU_NAN:
                        SummeEFG += vi
            if (U + SummeEFG) == 0:
                result = 0
            elif power(U, 4) > (10000 * SummeEFG):
                result = 10000
            else:
                result = power(U, 4) / SummeEFG
        else:
            print("Hier bin iCh wieder", self)
            SummeUB = 0
            for item in self:
                if isinstance(item, TMU_Komponente):
                    ubi = item.UnsicherheitsBeitrag
                    vi = item.EffektiverFreiheitsgrad
                    print("lpl",ubi,vi)
                    if not math.isnan(ubi) and not math.isnan(vi) :
                        SummeUB += power(ubi, 4) / vi
                        valid = True
            if valid:
                print(SummeUB)
                uy = self.StandardUnsicherheit_Uy()
                print("lplp",uy)
                if uy != MU_NAN:
                    print("YEEEY",uy,SummeUB)
                    try:
                        if SummeUB == 0:
                            result = 500
                        else:
                            result = power(uy, 4) / SummeUB
                            print("t",result)
                    except:
                        result = MU_NAN
        return result

    def Erweiterungsfaktor_k(self):
        veff = self.V_eff()
        print("disneyland",veff)
        if not math.isnan(veff):
            if self.AufgabeModell == "a3D_Pruefprozess":
                result = 2.0
            else:
                if veff >= 500:
                    result = 2.00
                elif veff >= 100:
                    result = 2.02
                elif veff >= 50:
                    result = 2.05
                elif veff >= 45:
                    result = 2.06
                elif veff >= 40:
                    result = 2.06
                elif veff >= 35:
                    result = 2.07
                elif veff >= 30:
                    result = 2.09
                elif veff >= 25:
                    result = 2.11
                elif veff >= 20:
                    result = 2.13
                elif veff >= 19:
                    result = 2.14
                elif veff >= 18:
                    result = 2.15
                elif veff >= 17:
                    result = 2.16
                elif veff >= 16:
                    result = 2.17
                elif veff >= 15:
                    result = 2.18
                elif veff >= 14:
                    result = 2.20
                elif veff >= 13:
                    result = 2.21
                elif veff >= 12:
                    result = 2.23
                elif veff >= 11:
                    result = 2.25
                elif veff >= 10:
                    result = 2.28
                elif veff >= 8:
                    result = 2.37
                elif veff >= 7:
                    result = 2.43
                elif veff >= 6:
                    result = 2.52
                elif veff >= 5:
                    result = 2.65
                elif veff >= 4:
                    result = 2.87
                elif veff >= 3:
                    result = 3.31
                elif veff >= 2:
                    result = 4.53
                elif veff >= 1:
                    result = 13.97
        else:
            result = MU_NAN
        return result

    def MUPruefverfahren_U(self):
        k = self.Erweiterungsfaktor_k()
        uy = self.StandardUnsicherheit_Uy()
        print("Finale",uy,k)
        if k != MU_NAN and uy != MU_NAN:
            return k * uy
        return MU_NAN

    def BerechnungToleranzfaktor(self):
        u = self.MUPruefverfahren_U()
        og = 0  # Setze dies mit der tatsächlichen Logik
        ug = 0  # Setze dies mit der tatsächlichen Logik
        if u != MU_NAN and og != MU_NAN and ug != MU_NAN and og != ug:
            return (2 * u) / ((og - ug) * 1000) * 100
        return MU_NAN