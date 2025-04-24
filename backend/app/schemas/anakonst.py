from pydantic import BaseModel


class AnakonstBase(BaseModel):
    fk_anamu: str | None = None
    constnum: int | None = None
    constval: int | None = None
    remark: int | None = None

    class Config:
        orm_mode = True


class Anakonst(AnakonstBase):
    pass


class AnakonstUpdate(AnakonstBase):
    pass
