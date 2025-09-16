from aiogram import Router, F
from aiogram.types import Message

from roles.kitchen.filters.IsKitchenFilter import IsKitchenFilter
from roles.kitchen.keyboards.kitchen_kb import kitchen_kb

router = Router()
router.message.filter(IsKitchenFilter())

@router.message(F.text == "🍲 Кухня")
async def kitchen_panel(message: Message):
    await message.answer(text = "Кухня:", reply_markup=kitchen_kb())

@router.message(F.text == "♨️ Активные заказы")
async def active_orders(message: Message):
    await message.answer(text = "Активные заказы:")
