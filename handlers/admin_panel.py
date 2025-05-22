from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from create_bot import bot
from filters.IsAdminFilter import IsAdminFilter
from keyboards.admin_kb import admin_kb

router = Router()
router.message.filter(IsAdminFilter())

@router.message(F.text == "⚙️ Админ-панель")
async def text_admin_panel(message: Message):
    msg = await bot.send_message(message.chat.id, "Админ-панель:", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    await message.answer("Админ-панель:", reply_markup=admin_kb())

@router.message(F.text == "📃 Получить список пользователей")
async def text_get_all_users(message: Message):
    pass

@router.callback_query(F.data.startswith("accept_"))
async def order_accept(call: CallbackQuery):
    pass