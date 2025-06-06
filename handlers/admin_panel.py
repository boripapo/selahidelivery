from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from filters.IsAdminFilter import IsAdminFilter
from keyboards.admin_kb import admin_kb

router = Router()
router.message.filter(IsAdminFilter())

@router.message(F.text == "⬅️ Админ-панель")
@router.message(F.text == "⚙️ Админ-панель")
async def text_admin_panel(message: Message):
    await message.answer(text="Админ-панель:",
                         reply_markup=admin_kb())

#История заказов------------------------------------------------------------------------------------------------

@router.message(F.text == "🔎 История заказов")
async def text_orders_history(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text = "📅 Текущая смена")
    builder.button(text = "📒 Прошлые смены")
    builder.button(text = "⬅️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="История заказов:",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "📅 Текущая смена")
async def text_current_shift(message: Message):
    await message.answer(text="blank")

@router.message(F.text == "📒 Прошлые смены")
async def text_past_shifts(message: Message):
    await message.answer(text="blank")

#Статистика------------------------------------------------------------------------------------------------

@router.message(F.text == "📊 Статистика")
async def text_statistics(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text = "💵 Выручка")
    builder.button(text = "📋 Заказы")
    builder.button(text = "⬅️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="Статистика:",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "💵 Выручка")
async def text_revenue_statistics(message: Message):
    await message.answer(text="blank")

@router.message(F.text == "📋 Заказы")
async def text_orders_statistics(message: Message):
    await message.answer(text="blank")

#Очистка базы данных------------------------------------------------------------------------------------------------

@router.message(F.text == "♻️ Очистка базы данных")
async def text_db_cleaning(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text = "🧹 Очистить текущую смену")
    builder.button(text = "🌀 Полная очистка базы заказов")
    builder.button(text = "⬅️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="Очистка базы данных:",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "🧹 Очистить текущую смену")
async def text_db_cleaning_current_shift(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="yes_clean_current_shift")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(1)

    await message.answer(text="Очистить текущую смену?",
                         reply_markup=builder.as_markup())

@router.callback_query(F.data == "yes_clean_current_shift")
async def call_clean_current_shift(call: CallbackQuery):
    await call.answer(text="Текущая смена успешно очищена")
    await call.message.delete()

@router.message(F.text == "🌀 Полная очистка базы заказов")
async def text_full_cleaning_orders(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="yes_full_clean_orders")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(1)

    await message.answer(text="Вы уверены, что хотите полностью очистить базу заказов?",
                         reply_markup=builder.as_markup())

@router.callback_query(F.data == "yes_full_clean_orders")
async def call_full_clean_warning(call: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Очистить базу заказов", callback_data="start_full_clean_orders")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(1)

    await call.message.answer(text="Это действие НЕЛЬЗЯ ОТМЕНИТЬ!",
                         reply_markup=builder.as_markup())
    await call.message.delete()

@router.callback_query(F.data == "start_full_clean_orders")
async def call_full_orders_clean(call: CallbackQuery):
    await call.answer(text="База заказов успешно очищена.", show_alert=True)
    await call.message.delete()