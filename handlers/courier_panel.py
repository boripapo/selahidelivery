from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove

from create_bot import bot
from filters.IsCourierFilter import IsCourierFilter
from keyboards.courier_kb import courier_kb

router = Router()
router.message.filter(IsCourierFilter())

@router.message(F.text == "🛵 Курьер-панель")
async def text_courier_panel(message: Message):
    msg = await bot.send_message(message.chat.id, "Курьер-панель:", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    await message.answer("Курьер-панель:", reply_markup=courier_kb())
