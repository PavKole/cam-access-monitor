#  Cam Access Monitor

Система для **видеонаблюдения за камерой** и **учёта проходов по пропускам**.  
Принимает RTSP-поток с IP-камеры, сохраняет кадры, логирует события в PostgreSQL и отдаёт веб-интерфейс для просмотра.

 Мини проект, но построен как настоящий: Docker, REST API, БД, reverse proxy, эмулятор камеры.

---


<img width="1189" height="549" alt="123" src="https://github.com/user-attachments/assets/d4a7a479-4af3-4e04-9f80-7299be7a06ac" />




---

##  Что может

- Подключается к RTSP-потоку (эмулятор камеры — MediaMTX).
- Сохраняет кадры с камеры каждые N секунд (`ffmpeg`).
- Принимает события проходов по REST API (`POST /events`).
- Хранит события в PostgreSQL.
- Отдаёт:
  - веб-интерфейс: последний кадр + список событий;
  - API: список событий, health-check, последний кадр.
- Всё упаковано в Docker Compose.
- Nginx работает как reverse proxy: один порт — сайт + API + кадры.

---

##  Стек технологий

| Слой | Технология |
|------|------------|
| Контейнеризация | Docker, Docker Compose |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic 2 |
| БД | PostgreSQL 16 |
| Видео | ffmpeg (захват кадров), MediaMTX (RTSP-сервер / эмулятор камеры) |
| Frontend | HTML + чистый JavaScript |
| Reverse proxy | Nginx 1.27 |
| ASGI-сервер | Uvicorn |

---

##  Структура

```
cam-access-monitor/
├── backend/                  # FastAPI-приложение
│   ├── app/
│   │   ├── main.py           # роуты
│   │   ├── db.py             # подключение к PostgreSQL
│   │   ├── models.py         # ORM-модель Event
│   │   └── schemas.py        # Pydantic-схемы
│   ├── Dockerfile
│   └── requirements.txt
├── capture/
│   └── capture.sh            # скрипт захвата кадров с камеры
├── frontend/
│   └── index.html            # веб-интерфейс
├── nginx/
│   └── default.conf          # конфиг reverse proxy
├── db/
│   └── init.sql              # SQL-миграция (создание таблиц)
├── docs/
│   └── screenshot.png        # скриншот интерфейса
├── docker-compose.yml
├── .env.example              # пример переменных окружения
├── .gitignore
└── README.md
```

---

##  Старт

### Требования

- Docker Engine 20.10+
- Docker Compose v2
- ffmpeg (для захвата кадров и публикации тестового потока)

### Установка ffmpeg (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y ffmpeg
```

### 1. Клонировать репозиторий

```bash
git clone https://github.com/<логин>/cam-access-monitor.git
cd cam-access-monitor
```

### 2. Создать `.env`

```bash
cp .env.example .env
```

При необходимости — открой `.env` и смени пароль к БД.

### 3. Запустить контейнеры

```bash
docker compose up -d --build
```

Проверить статус:

```bash
docker compose ps
```

Должны подняться четыре контейнера:

- `cam-db` — PostgreSQL
- `cam-mediamtx` — эмулятор RTSP-камеры
- `cam-backend` — FastAPI
- `cam-nginx` — reverse proxy

### 4. Запустить «камеру» — публикация тестового потока

В отдельном терминале:

```bash
ffmpeg -re -f lavfi -i testsrc=size=1280x720:rate=25 \
       -c:v libx264 -preset ultrafast -tune zerolatency \
       -f rtsp -rtsp_transport tcp rtsp://localhost:8554/cam1
```

Оставь терминал открытым — это и есть «камера».

### 5. Запустить захват кадров

Во втором терминале:

```bash
./capture/capture.sh
```

Скрипт начнёт сохранять кадры в папку `frames/` раз в 5 секунд.

### 6. Открыть интерфейс

В браузере:

```
http://localhost/
```

Что будет:
- живой кадр с камеры (обновляется каждые 5 секунд);
- список последних событий;
- кнопки «Обновить» и «Симулировать проход».

---

##  API

Все эндпоинты доступны через Nginx на порту 80.

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/health` | Проверка, что backend жив |
| POST | `/api/events` | Зарегистрировать событие прохода |
| GET | `/api/events?limit=N` | Последние N событий (по умолчанию 10) |
| GET | `/frame` | Последний кадр с камеры (JPEG) |
| GET | `/docs` | Swagger-документация (автогенерируется FastAPI) |

### Пример: отправить событие

```bash
curl -X POST http://localhost/api/events \
     -H "Content-Type: application/json" \
     -d '{
           "card_id": "CARD-001",
           "user_name": "Иван Иванов",
           "direction": "in",
           "gate": "main"
         }'
```

### Пример: получить список событий

```bash
curl http://localhost/api/events?limit=5 | python3 -m json.tool
```

### Пример: получить кадр

```bash
curl http://localhost/frame -o frame.jpg
file frame.jpg   # JPEG image data
```

### Валидация

FastAPI автоматически проверяет входные данные:

- `card_id` — строка 1–64 символа;
- `direction` — только `in` или `out`;
- при нарушении — ответ `422 Unprocessable Entity` с описанием.

---

##  Как это работает

### MediaMTX — эмулятор камеры

Мы не используем настоящую IP-камеру. MediaMTX поднимает RTSP-сервер, а `ffmpeg` **публикует** в него синтетический поток `testsrc` (цветные полосы + часы). Всё это доступно по адресу:

```
rtsp://localhost:8554/cam1
```

Это выглядит как настоящая камера — любой клиент (ffprobe, VLC, OpenCV) может к ней подключиться.

### capture.sh — захват кадров

Скрипт каждые N секунд вызывает `ffmpeg`, который берёт **один кадр** из потока и сохраняет как JPEG:

```bash
ffmpeg -rtsp_transport tcp -i "$RTSP_URL" \
       -frames:v 1 -q:v 2 -vf "scale=1280:-1" \
       -y "$OUT"
```

Кадры попадают в `frames/`, старые автоматически удаляются.

### Backend на FastAPI

- Порт 8000 внутри контейнера.
- Читает переменные окружения из `.env`.
- Работает с PostgreSQL через SQLAlchemy.
- Отдаёт последний кадр через `FileResponse`, читая его прямо из смонтированной папки `frames/`.

### Nginx

Проксирует запросы и отдаёт статику:

- `/` → статика из `frontend/`
- `/api/*` → backend
- `/frame` → backend
- `/docs` → backend (Swagger UI)

Использует `resolver 127.0.0.11` (DNS Docker), чтобы корректно резолвить имя `backend` в момент запроса.

---

##  Пример сценария работы

1. `cam-mediamtx` поднимает RTSP-сервер.
2. `ffmpeg` публикует тестовый поток в `rtsp://mediamtx:8554/cam1`.
3. `capture.sh` берёт кадры раз в 5 секунд и сохраняет их в `frames/`.
4. `cam-backend` принимает события проходов через `/events` и хранит их в PostgreSQL.
5. `cam-backend` отдаёт последний кадр через `/frame`.
6. `cam-nginx` раздаёт UI и проксирует API.
7. Пользователь открывает `http://localhost/` и видит всё в реальном времени.

---

##  Тестирование

Проверить каждый компонент отдельно:

```bash
# Камера работает?
ffprobe -v error -show_streams rtsp://localhost:8554/cam1

# Backend жив?
curl -s http://localhost/api/health

# События пишутся?
curl -X POST http://localhost/api/events \
     -H "Content-Type: application/json" \
     -d '{"card_id":"TEST","direction":"in"}'
curl -s http://localhost/api/events | python3 -m json.tool

# Кадр отдаётся?
curl -s http://localhost/frame -o test.jpg && file test.jpg
```


## 📄 Лицензия

MIT — см. [LICENSE](LICENSE).
