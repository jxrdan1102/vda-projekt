from app.database.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(1024), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship('User', back_populates='refresh_tokens')