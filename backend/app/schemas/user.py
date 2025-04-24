from typing import Literal

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["user", "admin"]


class UserOut(BaseModel):
    id: int
    username: str
    role: str
