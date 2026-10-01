#!/bin/bash
# Скрипт захвата кадров с RTSP-камеры.
# Раз в N секунд берёт один кадр из потока и сохраняет в frames/.
# Автор: Павел

# ---- Настройки ----
RTSP_URL="${RTSP_URL:-rtsp://localhost:8554/cam1}"
INTERVAL="${CAPTURE_INTERVAL:-5}"
FRAMES_DIR="${FRAMES_DIR:-$(dirname "$0")/../frames}"
FRAME_WIDTH=1280       # ширина кадра (можно уменьшить для экономии места)
MAX_AGE_MIN=60         # кадры старше этого времени удаляем (минуты)

# ---- Подготовка ----
mkdir -p "$FRAMES_DIR"

echo "[$(date '+%F %T')] старт захвата кадров с $RTSP_URL, интервал $INTERVAL сек"

# ---- Бесконечный цикл ----
while true; do
    # Формируем имя файла с датой и временем
    STAMP=$(date +%Y%m%d_%H%M%S)
    OUT="$FRAMES_DIR/frame_${STAMP}.jpg"

    # Забираем один кадр с потока.
    # -frames:v 1   — взять ровно 1 кадр
    # -q:v 2        — высокое качество JPEG
    # -y            — перезаписать, если файл вдруг существует
    ffmpeg -rtsp_transport tcp -i "$RTSP_URL" \
           -frames:v 1 -q:v 2 -vf "scale=${FRAME_WIDTH}:-1" \
           -y "$OUT" > /dev/null 2>&1

    if [ -s "$OUT" ]; then
        echo "[$(date '+%F %T')] сохранил $OUT"
    else
        echo "[$(date '+%F %T')] не удалось получить кадр"
        rm -f "$OUT"
    fi

    # Чистим старые кадры
    find "$FRAMES_DIR" -name "frame_*.jpg" -mmin +"$MAX_AGE_MIN" -delete

    sleep "$INTERVAL"
done
