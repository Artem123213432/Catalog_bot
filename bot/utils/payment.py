from yookassa import Configuration, Payment
import uuid
import logging

logger = logging.getLogger(__name__)

SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

async def create_payment(amount: float, description: str) -> dict:
    try:
        logger.info(f"Создание платежа на сумму {amount} руб.: {description}")
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/Test_tessssttt_bot"
            },
            "capture": True,
            "description": description,
            "metadata": {
                "order_id": str(uuid.uuid4())
            }
        })
        
        return {
            "id": payment.id,
            "payment_url": payment.confirmation.confirmation_url
        }
    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {e}")
        return None

async def check_payment(payment_id: str) -> dict:
    try:
        logger.info(f"Проверка статуса платежа: {payment_id}")
        payment = Payment.find_one(payment_id)
        return {"paid": payment.status == "succeeded"}
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса платежа: {e}")
        return {"paid": False} 
