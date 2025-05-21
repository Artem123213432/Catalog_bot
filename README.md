# Тестовый Бот-каталог

Тестовый телеграм-бот для просмотра товаров и оформления заказов с интеграцией платежей и функцией рассылок.

## Функциональные возможности

- Просмотр каталога товаров
- Оформление заказов
- Интеграция оплаты через YooKassa
- Система рассылок пользователям
- Раздел FAQ с часто задаваемыми вопросами
- Административная панель на Django для управления контентом

## Технологии

- Python
- Aiogram (для Telegram Bot API)
- Django (для админ-панели)
- Docker и Docker Compose (для развертывания)
- PostgreSQL (база данных)
- Redis (для кэширования)

## Установка и запуск

1. Клонировать репозиторий:
```
git clone https://github.com/Artem123213432/Bot_catalog.git
```

2. Создать файл .env с необходимыми переменными окружения:
```
# Пример содержимого .env файла
BOT_TOKEN=your_bot_token
POSTGRES_PASSWORD=your_password
YOOKASSA_ACCOUNT_ID=your_yookassa_account
YOOKASSA_SECRET_KEY=your_yookassa_secret_key
YOOKASSA_RETURN_URL=https://your-return-url.com
```

3. Запустить контейнеры с помощью Docker Compose:
```
docker compose up -d
```

## Структура проекта

- `/bot` - Код телеграм-бота
- `/admin_panel` - Код административной панели Django
- `/docker-compose.yml` - Конфигурация Docker Compose для развертывания