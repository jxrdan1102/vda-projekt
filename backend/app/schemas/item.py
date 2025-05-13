from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str

    class Config:
        from_attributes = True


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    class Config:
        from_attributes = True
