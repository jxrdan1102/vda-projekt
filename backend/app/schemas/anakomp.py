from pydantic import BaseModel

from app.schemas.component import ComponentGet


class AnakompBase(BaseModel):
    fk_anamu: int | None = None
    fk_mod_components: int | None = None
    remark: str | None = None
    terml0: float | None = None
    terml1: float | None = None
    wertart: int | None = None
    freigrad: int | None = None
    frei_n_1: int | None = None
    verteilung: int | None = None

    class Config:
        from_attributes = True

class AnakompForAnamuR(BaseModel):
    id: int
    fk_mod_components: int
    remark: str | None = None
    terml0: float | None = None
    terml1: float | None = None
    wertart: int | None = None
    freigrad: int | None = None
    frei_n_1: int | None = None
    verteilung: int | None = None
    messpunkt_anzahl: int | None = None
    anzahl_messungen: int | None = None
    berechnen: int | None = None
    komponente: ComponentGet  | None = None

    class Config:
        from_attributes = True
class Anakomp(AnakompBase):
    pass


class AnakompUpdate(AnakompBase):
    pass

class AnakompUpdateR(BaseModel):
    remark: str | None = None
    terml0: float | None = None
    terml1: float | None = None
    wertart: int | None = None
    freigrad: int | None = None
    messpunkt_anzahl: int | None = None
    anzahl_messungen: int | None = None
    frei_n_1: int | None = None
    verteilung: int | None = None
    berechnen: int | None = None