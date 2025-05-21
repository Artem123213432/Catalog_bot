FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY admin_panel/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для логов
RUN mkdir -p /app/logs

# Копирование кода проекта
COPY admin_panel/ /app/admin_panel/

# Устанавливаем рабочий каталог для запуска Django
WORKDIR /app/admin_panel

# Запуск Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 