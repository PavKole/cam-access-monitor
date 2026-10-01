"""
ORM-модель события прохода.
SQLAlchemy сопоставляет её с таблицей events.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(String(64), nullable=False, index=True)
    user_name = Column(String(128), nullable=True)
    direction = Column(String(8), nullable=False)   # 'in' или 'out'
    gate = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
