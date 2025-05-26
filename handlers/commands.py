from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from keyboards.main_kb import main_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Введи /menu чтобы открыть меню бота.")

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("Меню", reply_markup=main_kb(message.from_user.id))
