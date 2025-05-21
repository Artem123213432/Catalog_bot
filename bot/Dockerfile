FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование всего проекта для доступа к Django моделям
COPY . /app/

# Установка зависимостей
COPY bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Создание директории для логов
RUN mkdir -p /app/logs

# Запуск бота
CMD ["python", "/app/bot/main.py"] 