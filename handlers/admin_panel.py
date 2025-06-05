from aiogram import Router, F
from aiogram.types import Message
from filters.IsAdminFilter import IsAdminFilter
from keyboards.admin_kb import admin_kb

router = Router()
router.message.filter(IsAdminFilter())

@router.message(F.text == "⚙️ Админ-панель")
async def text_manager_panel(message: Message):
    await message.answer(text="Админ-панель:",
                         reply_markup=admin_kb())