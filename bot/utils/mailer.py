import asyncio
import logging
import sys
import os
import django
from aiogram import Bot
from asgiref.sync import sync_to_async
from datetime import datetime

logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
logger.info(f"Путь до BASE_DIR: {BASE_DIR}")
logger.info(f"sys.path: {sys.path}")


@sync_to_async
def debug_database():
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            logger.info("Проверка таблицы mailings_mailing...")
            cursor.execute("SELECT COUNT(*) FROM mailings_mailing")
            total_mailings = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mailings_mailing WHERE is_sent = false")
            unsent_mailings = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mailings_client")
            total_clients = cursor.fetchone()[0]
            
            logger.info(f"В базе данных: {total_mailings} рассылок, {unsent_mailings} неотправленных, {total_clients} клиентов")
            
            
            cursor.execute("SELECT id, message_text, is_sent, scheduled_time, sent_at FROM mailings_mailing")
            mailings = cursor.fetchall()
            for mailing in mailings:
                logger.info(f"Рассылка в БД: ID={mailing[0]}, text={mailing[1][:20]}..., is_sent={mailing[2]}, scheduled={mailing[3]}, sent_at={mailing[4]}")
            
            
            cursor.execute("SELECT id, chat_id, is_active FROM mailings_client")
            clients = cursor.fetchall()
            for client in clients:
                logger.info(f"Клиент в БД: ID={client[0]}, chat_id={client[1]}, is_active={client[2]}")
            
            
            try:
                cursor.execute("SELECT COUNT(*) FROM orders_mailing")
                orders_mailings_count = cursor.fetchone()[0]
                logger.info(f"Найдено {orders_mailings_count} рассылок в таблице orders_mailing")
                
                cursor.execute("SELECT COUNT(*) FROM orders_mailing WHERE sent = false")
                unsent_orders_mailings = cursor.fetchone()[0]
                logger.info(f"Найдено {unsent_orders_mailings} неотправленных рассылок в таблице orders_mailing")
                
                cursor.execute("SELECT id, message, sent FROM orders_mailing")
                orders_mailings = cursor.fetchall()
                for m in orders_mailings:
                    logger.info(f"Рассылка в orders_mailing: ID={m[0]}, text={m[1][:20]}..., sent={m[2]}")
            except Exception as e:
                logger.error(f"Ошибка при проверке таблицы orders_mailing: {e}")
                
    except Exception as e:
        logger.error(f"Ошибка при отладке базы данных: {e}", exc_info=True)

@sync_to_async
def get_unsent_mailings():
    try:
        
        from django.db import connection
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT id, message_text, photo_id, scheduled_time FROM mailings_mailing WHERE is_sent = false ORDER BY id")
            rows = cursor.fetchall()
        
        logger.info(f"Найдено {len(rows)} неотправленных рассылок через SQL в mailings_mailing")
        
        
        class MailingObj:
            def __init__(self, id, message_text, photo_id, scheduled_time):
                self.id = id
                self.message_text = message_text
                self.photo_id = photo_id
                self.scheduled_time = scheduled_time
                self.table_name = "mailings_mailing"
                
        mailings = [MailingObj(row[0], row[1], row[2], row[3]) for row in rows]
        for mailing in mailings:
            logger.info(f"Найдена рассылка в mailings_mailing: ID: {mailing.id}, текст: {mailing.message_text[:30]}...")
            
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, message FROM orders_mailing WHERE sent = false ORDER BY id")
                orders_rows = cursor.fetchall()
                
            logger.info(f"Найдено {len(orders_rows)} неотправленных рассылок через SQL в orders_mailing")
            
            class OrdersMailingObj:
                def __init__(self, id, message_text):
                    self.id = id
                    self.message_text = message_text
                    self.photo_id = None  
                    self.scheduled_time = None  
                    self.table_name = "orders_mailing"
                    
            orders_mailings = [OrdersMailingObj(row[0], row[1]) for row in orders_rows]
            for mailing in orders_mailings:
                logger.info(f"Найдена рассылка в orders_mailing: ID: {mailing.id}, текст: {mailing.message_text[:30]}...")
                
            
            return mailings + orders_mailings
        except Exception as e:
            logger.error(f"Ошибка при получении рассылок из orders_mailing: {e}", exc_info=True)
            return mailings
    except Exception as e:
        logger.error(f"Ошибка при получении рассылок через SQL: {e}", exc_info=True)
        return []

@sync_to_async
def get_active_clients():
    try:
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, chat_id FROM mailings_client WHERE is_active = true ORDER BY id")
            rows = cursor.fetchall()
        
        
        class ClientObj:
            def __init__(self, id, chat_id):
                self.id = id
                self.chat_id = chat_id
        
        logger.info(f"Найдено {len(rows)} активных клиентов через SQL в mailings_client")
        clients = [ClientObj(row[0], row[1]) for row in rows]
        
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM orders_client")
                count = cursor.fetchone()[0]
                logger.info(f"Найдено {count} клиентов в таблице orders_client")
                
                cursor.execute("SELECT id, telegram_id FROM orders_client ORDER BY id")
                orders_rows = cursor.fetchall()
                
            logger.info(f"Добавляю {len(orders_rows)} клиентов из orders_client")
            for row in orders_rows:
                clients.append(ClientObj(row[0], row[1]))
                
        except Exception as e:
            logger.error(f"Ошибка при получении клиентов из orders_client: {e}", exc_info=True)
            
        return clients
    except Exception as e:
        logger.error(f"Ошибка при получении клиентов через SQL: {e}", exc_info=True)
        return []

@sync_to_async
def mark_mailing_as_sent(mailing_id, table_name="mailings_mailing"):
    try:
        
        from django.db import connection
        with connection.cursor() as cursor:
            if table_name == "mailings_mailing":
                
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "UPDATE mailings_mailing SET is_sent = true, sent_at = %s WHERE id = %s",
                    [now, mailing_id]
                )
                logger.info(f"Рассылка ID: {mailing_id} помечена как отправленная в mailings_mailing")
            elif table_name == "orders_mailing":
                
                cursor.execute(
                    "UPDATE orders_mailing SET sent = true WHERE id = %s",
                    [mailing_id]
                )
                logger.info(f"Рассылка ID: {mailing_id} помечена как отправленная в orders_mailing")
    except Exception as e:
        logger.error(f"Ошибка при сохранении статуса рассылки в {table_name}: {e}", exc_info=True)

async def check_and_send_mailings(bot: Bot):
    logger.info("Запущена фоновая задача check_and_send_mailings")
    
    
    await debug_database()
    
    while True:
        try:
            mailings = await get_unsent_mailings()
            if mailings:
                logger.info(f"Начинаем обработку {len(mailings)} рассылок")
                for mailing in mailings:
                    logger.info(f"Обработка рассылки ID: {mailing.id} из таблицы {mailing.table_name}, текст: {mailing.message_text[:30]}...")
                    clients = await get_active_clients()
                    if not clients:
                        logger.warning("Нет активных клиентов для отправки рассылки")
                        await mark_mailing_as_sent(mailing.id, mailing.table_name)  
                        continue
                        
                    sent_count = 0
                    error_count = 0
                    
                    for client in clients:
                        try:
                            chat_id = client.chat_id
                            logger.info(f"Отправка сообщения клиенту с chat_id={chat_id}")
                            if mailing.photo_id:
                                logger.info(f"Отправка фото с ID {mailing.photo_id} клиенту {chat_id}")
                                await bot.send_photo(
                                    chat_id=chat_id, 
                                    photo=mailing.photo_id, 
                                    caption=mailing.message_text, 
                                    parse_mode='HTML'
                                )
                            else:
                                logger.info(f"Отправка текстового сообщения клиенту {chat_id}")
                                await bot.send_message(
                                    chat_id=chat_id, 
                                    text=mailing.message_text, 
                                    parse_mode='HTML'
                                )
                            sent_count += 1
                            
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            error_count += 1
                            logger.error(f"Ошибка при отправке сообщения клиенту {client.chat_id}: {e}")
                            
                    
                    await mark_mailing_as_sent(mailing.id, mailing.table_name)
                    logger.info(f"Рассылка ID: {mailing.id} из таблицы {mailing.table_name} завершена. Успешно: {sent_count}, ошибок: {error_count}")
            else:
                logger.info("Нет неотправленных рассылок")
                
        except Exception as e:
            logger.error(f"Ошибка в check_and_send_mailings: {e}", exc_info=True)
            
        
        logger.info("Ожидание 10 секунд до следующей проверки рассылок")
        await asyncio.sleep(10)