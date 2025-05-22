FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY admin_panel/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/logs

COPY admin_panel/ /app/admin_panel/

ENV PYTHONPATH=/app

WORKDIR /app/admin_panel

CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000 