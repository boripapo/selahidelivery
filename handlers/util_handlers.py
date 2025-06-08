from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from keyboards.main_kb import main_kb

router = Router()

@router.callback_query(F.data == "close_tab")
async def close_tab(call: CallbackQuery):
    await call.message.delete()

@router.message(F.text == "⬅️ На главную")
async def text_back_to_main(message: Message):
    await message.answer(text="Меню:",
                         reply_markup=main_kb(message.from_user.id))