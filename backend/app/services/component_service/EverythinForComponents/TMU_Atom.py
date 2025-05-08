from abc import ABC


class TMU_Atom(ABC):

    def __init__(self, AnID: int, AName: str):
        self.id = AnID
        self.name = AName
        self.remark = ""
        self.archiv = False
        self.einheit = ""
        self.dez = 0

