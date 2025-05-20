FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY admin_panel/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY admin_panel/ .

# Создание директории для логов
RUN mkdir -p /app/logs

# Ожидание готовности базы данных
COPY admin_panel/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Копируем manage.py в /app
COPY ../manage.py /app/manage.py

# Запуск Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 