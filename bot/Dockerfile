FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY bot/ .

# Создание директории для логов
RUN mkdir -p /app/logs

# Запуск бота
CMD ["python", "main.py"] 