"""
Pydantic-схемы — описывают, какие данные FastAPI принимает и отдаёт.
Если клиент пришлёт что-то не то — FastAPI вернёт понятную ошибку 422.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Схема для POST /events — что присылает считыватель пропусков."""
    card_id: str = Field(..., min_length=1, max_length=64, description="Номер карты")
    user_name: Optional[str] = Field(None, max_length=128, description="Имя владельца")
    direction: str = Field(..., pattern="^(in|out)$", description="Направление: in или out")
    gate: Optional[str] = Field(None, max_length=64, description="Турникет/дверь")


class EventOut(BaseModel):
    """Схема для GET /events — что возвращаем клиенту."""
    id: int
    card_id: str
    user_name: Optional[str]
    direction: str
    gate: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True    # чтобы Pydantic умел читать ORM-объекты
