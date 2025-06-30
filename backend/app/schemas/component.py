from pydantic import BaseModel

from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec


class ComponentGetModell(BaseModel):
    id: int
    kompid: int
    modltxtid: int | None = None

    class Config:
        from_attributes = True


class ComponentRefBase(BaseModel):
    lfdnr: int | None = None
    kompid: int | None = None
    modltxtid: int | None = None
    messpunkt_anzahl: int | None = None
    terml0: float | None = None
    terml1: float | None = None
    wertart: int | None = None
    freigrad: int | None = None
    frei_n_1: int | None = None
    verteilung: int | None = None
    kflags: int | None = None

    class Config:
        from_attributes = True

class ComponentAddR(ComponentRefBase):
    pass

class ComponentGetR(BaseModel):
    id: int
    kompid: int
    modltxtid: int | None = None

    class Config:
        from_attributes = True

class ComponentGet(ComponentRefBase):
    pass


class ComponentRefCreate(ComponentRefBase):
    pass


class ComponentRefUpdate(ComponentRefBase):
    pass


class ComponentBack(BaseModel):
    data: TMuKompRec | None = None
    ConstNeeded: set[str] | None = None
    name: str | None = None
    id: int | None = None

    class Config:
        json_encoders = {str: lambda v: v.upper()}


class ComponentKompidOnly(BaseModel):
    kompid: int


class ComponentData(BaseModel):
    terml0: float | None = None
    terml1: float | None = None
    verteilung: int | None = None
    wertart: int | None = None
    freigrad: int | None = None
    frei_n_1: int | None = None


class TMU_Komponente_Pydantic(BaseModel):
    lfdnr: int
    name: str

    class Config:
        from_attributes = True