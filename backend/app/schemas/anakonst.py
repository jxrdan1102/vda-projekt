from typing import Optional

from pydantic import BaseModel


class AnakonstBase(BaseModel):
    fk_anamu: Optional[str] = None
    constnum: Optional[int] = None
    constval: Optional[int] = None
    remark: Optional[int] = None

    class Config:
        orm_mode = True


class Anakonst(AnakonstBase):
    pass


class AnakonstUpdate(AnakonstBase):
    pass
