FROM python:3.12-slim

# Рабочая директория
WORKDIR /app

# Сначала копируем requirements и ставим зависимости —
# так Docker кэширует этот слой.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY app/ /app/

# Открываем порт
EXPOSE 8000

# Запускаем uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
