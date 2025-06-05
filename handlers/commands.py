from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from decouple import config

from keyboards.main_kb import main_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Введи /menu чтобы открыть меню бота.")

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("Меню", reply_markup=main_kb(message.from_user.id))

@router.message(F.text == "🤖 О боте")
@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(f"Selahi Delivery Bot v. {config("APP_VERSION")}")
