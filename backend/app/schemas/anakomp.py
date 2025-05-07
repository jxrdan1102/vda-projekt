from pydantic import BaseModel


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
        orm_mode = True

class AnakompForAnamuR(BaseModel):
    fk_mod_components: int
    remark: str | None = None
    terml0: float | None = None
    terml1: float | None = None
    wertart: int | None = None
    freigrad: int | None = None
    verteilung: int | None = None

    class Config:
        orm_mode = True
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
    verteilung: int | None = None