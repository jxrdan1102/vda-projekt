from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    class Config:
        orm_mode = True
