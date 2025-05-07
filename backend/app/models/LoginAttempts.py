from app.database.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(512), index=True)
    attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, default=func.now())