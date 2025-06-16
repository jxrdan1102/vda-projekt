from pydantic import BaseModel


class AnakonstBase(BaseModel):
    fk_anamu: str | None = None
    constnum: int | None = None
    constval: float | None = None
    remark: int | None = None

    class Config:
        from_attributes = True

class AnakonstUpdateR(BaseModel):
    constval: float | None = None
    remark: int | None = None
    class Config:
        from_attributes = True

class AnakonstForAnamuR(BaseModel):
    id: int | None = None
    constnum: int | None = None
    constval: float | None = None
    class Config:
        from_attributes = True

class Anakonst(AnakonstBase):
    pass


class AnakonstUpdate(AnakonstBase):
    pass
