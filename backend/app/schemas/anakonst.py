from typing import Optional

from pydantic import BaseModel


class Anakonst(BaseModel):
    fk_anamu: Optional[str] = None
    constnum: Optional[int] = None
    constval: Optional[int] = None
    remark: Optional[int] = None

    class Config:
        orm_mode = True

class AnakonstUpdate(BaseModel):
    id: int
    fk_anamu: Optional[str] = None
    constnum: Optional[int] = None
    constval: Optional[int] = None
    remark: Optional[int] = None

    class Config:
        orm_mode = True