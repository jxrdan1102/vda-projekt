from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class TEXTKAT(Base):
    __tablename__ = "textkat"

    id = Column(Integer, primary_key=True, index=True)
    textnum = Column(String(255), index=True)
    deutsch = Column(String(255))
    englisch = Column(String(255))
    spanisch = Column(String(255))
    french = Column(String(255))
    italian = Column(String(255))
