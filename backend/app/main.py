"""
Основное приложение FastAPI.
Роуты:
  GET  /health  — проверка, что сервис жив
  POST /events  — принять событие прохода
  GET  /events  — последние N событий
  GET  /frame   — последний кадр с камеры
"""

import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db import get_db, engine, Base
from models import Event
from schemas import EventCreate, EventOut


app = FastAPI(
    title="Cam Access Monitor API",
    description="API для системы видеонаблюдения и учёта пропусков",
    version="1.0.0",
)


# При старте создаём таблицы (если их нет).
Base.metadata.create_all(bind=engine)


# Директория с кадрами (монтируется из хоста)
FRAMES_DIR = Path(os.getenv("FRAMES_DIR", "/frames"))


@app.get("/health")
def health():
    """Простой health-check — чтобы проверять, что сервис отвечает."""
    return {"status": "ok"}


@app.post("/events", response_model=EventOut, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Регистрирует проход по пропуску.
    """
    new_event = Event(
        card_id=event.card_id,
        user_name=event.user_name,
        direction=event.direction,
        gate=event.gate,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@app.get("/events", response_model=list[EventOut])
def list_events(limit: int = 10, db: Session = Depends(get_db)):
    """
    Возвращает последние N событий (по умолчанию 10).
    """
    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .limit(min(limit, 100))
        .all()
    )
    return events


@app.get("/frame")
def latest_frame():
    """
    Отдаёт последний сохранённый кадр с камеры.
    """
    if not FRAMES_DIR.exists():
        raise HTTPException(status_code=404, detail="Директория с кадрами не найдена")

    # Ищем самый свежий frame_*.jpg
    files = sorted(FRAMES_DIR.glob("frame_*.jpg"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="Кадров ещё нет")

    return FileResponse(files[0], media_type="image/jpeg")
