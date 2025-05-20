from yookassa import Configuration, Payment
import uuid

# Укажите ваши тестовые учетные данные
SHOP_ID = '1091374'
SECRET_KEY = 'test_yOgWlf-8N7ppnjyDNPpvCvxiYJWob1dX_zd4FuQPsIk'

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

async def create_payment(amount: float, description: str) -> dict:
    try:
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://example.com/return_url" # Здесь можно указать URL, куда пользователь вернется после оплаты
            },
            "capture": True, # Автоматическое подтверждение платежа
            "description": description,
            "metadata": {
                "order_id": str(uuid.uuid4()) # Пример метаданных: ID заказа
            }
        })
        return {
            "id": payment.id,
            "payment_url": payment.confirmation.confirmation_url
        }
    except Exception as e:
        print(f"Ошибка при создании платежа: {e}")
        return None

async def check_payment(payment_id: str) -> dict:
    try:
        payment = Payment.find_one(payment_id)
        return {"paid": payment.status == 'succeeded'}
    except Exception as e:
        print(f"Ошибка при проверке статуса платежа: {e}")
        return {"paid": False} 