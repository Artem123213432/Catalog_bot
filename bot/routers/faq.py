from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command
from bot.keyboards.faq import get_faq_keyboard, get_faq_back_keyboard
from bot.data.faq import FAQ_DATA
from uuid import uuid4

router = Router()

# Здесь могут быть обработчики для FAQ 

@router.message(Command("faq"))
async def show_faq(message: Message):
    await message.answer(
        "<b>Часто задаваемые вопросы:</b>",
        reply_markup=get_faq_keyboard()
    )

@router.callback_query(F.data.startswith("faq_"))
async def show_faq_answer(callback: CallbackQuery):
    idx = int(callback.data.split("_")[1])
    question = FAQ_DATA[idx]["question"]
    answer = FAQ_DATA[idx]["answer"]
    await callback.message.edit_text(
        f"<b>{question}</b>\n\n{answer}",
        reply_markup=get_faq_back_keyboard()
    )

@router.callback_query(F.data == "faq_back")
async def faq_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Часто задаваемые вопросы:</b>",
        reply_markup=get_faq_keyboard()
    )

@router.inline_query()
async def inline_faq_query(inline_query: InlineQuery):
    query = inline_query.query.lower()
    results = []
    for i, item in enumerate(FAQ_DATA):
        if query in item["question"].lower() or query in item["answer"].lower():
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=item["question"],
                    description=item["answer"][:50],
                    input_message_content=InputTextMessageContent(
                        message_text=f"<b>{item['question']}</b>\n\n{item['answer']}"
                    )
                )
            )
    if not results and query:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Нет подходящих вопросов",
                input_message_content=InputTextMessageContent(
                    message_text="Не найдено подходящих ответов в FAQ."
                )
            )
        )
    await inline_query.answer(results, cache_time=1, is_personal=True) 