from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from matplotlib import pyplot
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

from create_bot import bot, db
from filters.IsAdminFilter import IsAdminFilter
from keyboards.admin_kb import admin_kb

admin_router = Router()
admin_router.message.filter(IsAdminFilter())

@admin_router.message(F.text == "⬅️ Админ-панель")
@admin_router.message(F.text == "⚙️ Админ-панель")
async def text_admin_panel(message: Message):
    await message.answer(text="Админ-панель:",
                         reply_markup=admin_kb())

#История заказов--------------------------------------------------------------------------------------------------------

@admin_router.message(F.text == "🔎 История заказов")
async def text_orders_history(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text = "📅 Текущая смена")
    builder.button(text = "📒 Прошлые смены")
    builder.button(text = "⬅️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="История заказов:",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@admin_router.message(F.text == "📅 Текущая смена")
async def text_current_shift(message: Message):
    await message.answer(text="blank")
    #await message.from_user.

@admin_router.message(F.text == "📒 Прошлые смены")
async def text_past_shifts(message: Message):
    await message.answer(text="blank")

#Тестовые данные--------------------------------------------------------------------------------------------------------

@admin_router.message(F.text == "⏫ Заполнить БД")
async def text_fill_db(message: Message):
    await db.fill_db_with_test_data()
    await message.answer(text = "БД заполнена тестовыми данными.")

#Статистика-------------------------------------------------------------------------------------------------------------

@admin_router.message(F.text == "📊 Статистика")
async def text_statistics(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text = "💵 Выручка")
    builder.button(text = "📋 Заказы")
    builder.button(text = "⬅️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="Статистика:",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@admin_router.message(F.text == "💵 Выручка")
async def text_revenue_statistics(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text = "За сегодня", callback_data = "revenue_chart:1")
    builder.button(text = "За 7 дней", callback_data = "revenue_chart:7")
    builder.button(text = "За 30 дней", callback_data = "revenue_chart:30")
    builder.button(text = "Закрыть окно", callback_data="close_tab")
    builder.adjust(3, 1)

    await message.answer(text = "Выберите период:", reply_markup=builder.as_markup())

@admin_router.message(F.text == "📋 Заказы")
async def text_orders_statistics(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="За сегодня", callback_data="orders_chart:1")
    builder.button(text="За 7 дней", callback_data="orders_chart:7")
    builder.button(text="За 30 дней", callback_data="orders_chart:30")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(3, 1)

    await message.answer(text="Выберите период:", reply_markup=builder.as_markup())

@admin_router.callback_query(F.data.startswith("orders_chart:"))
async def call_orders_chart(call: CallbackQuery):
    period = int(call.data.split(":")[1])
    today = datetime.now()
    orders_by_date = list()
    dates = list()
    for i in range(0, period):
        orders = await db.get_orders_by_date(today - timedelta(i))
        dates.append(today - timedelta(i))
        orders_by_date.append(len(orders))
    dates.reverse()
    orders_by_date.reverse()

    fig, ax = pyplot.subplots()
    ax.plot(dates, orders_by_date, marker="o", linestyle="-")
    fig.autofmt_xdate(rotation=45)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Заказы по дням")
    ax.set_ylabel("Заказы за день")
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    if period == 1:
        await bot.send_photo(chat_id=call.from_user.id, photo=BufferedInputFile(buf.read(), filename="orders_chart.png"),
                             caption=f"Заказы за сегодня.")
    else:
        await bot.send_photo(chat_id=call.from_user.id, photo=BufferedInputFile(buf.read(), filename="orders_chart.png"),
                             caption=f"Заказы за {period} дней, с {(today - timedelta(period)).strftime("%d.%m.%Y")} по {today.strftime("%d.%m.%Y")}")
    await call.message.delete()

@admin_router.callback_query(F.data.startswith("revenue_chart:"))
async def call_revenue_chart(call: CallbackQuery):
    period = int(call.data.split(":")[1])
    today = datetime.now()
    revenue_by_date = list()
    dates = list()
    for i in range(0, period):
        revenue_for_today = Decimal('0')
        orders = await db.get_orders_by_date(today - timedelta(i))
        dates.append((today - timedelta(i)))
        for order in orders:
            items = await db.get_items_by_order_id(order["id"])
            revenue_for_today += sum(item["price"] for item in items)
        revenue_by_date.append(revenue_for_today)
    dates.reverse()
    revenue_by_date.reverse()

    fig, ax = pyplot.subplots()
    ax.plot(dates, revenue_by_date, marker = "o", linestyle = "-")
    fig.autofmt_xdate(rotation=45)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.set_title("Выручка")
    ax.set_ylabel("Выручка за день")
    ax.grid(True)

    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    if period == 1:
        await bot.send_photo(chat_id=call.from_user.id, photo=BufferedInputFile(buf.read(), filename="revenue_chart.png"),
                             caption=f"Выручка за сегодня.")
    else:
        await bot.send_photo(chat_id=call.from_user.id, photo=BufferedInputFile(buf.read(), filename="revenue_chart.png"),
                             caption=f"Выручка за {period} дней, с {(today - timedelta(period)).strftime("%d.%m.%Y")} по {today.strftime("%d.%m.%Y")}")
    await call.message.delete()



#Очистка базы данных------------------------------------------------------------------------------------------------

@admin_router.message(F.text == "♻️ Очистка базы данных")
async def text_db_cleaning(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text = "🧹 Очистить текущую смену")
    builder.button(text = "🌀 Полная очистка базы заказов")
    builder.button(text = "⬅️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="Очистка базы данных:",
                         reply_markup=builder.as_markup(resize_keyboard=True))

@admin_router.message(F.text == "🧹 Очистить текущую смену")
async def text_db_cleaning_current_shift(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="yes_clean_current_shift")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(1)

    await message.answer(text="Очистить текущую смену?",
                         reply_markup=builder.as_markup())

@admin_router.callback_query(F.data == "yes_clean_current_shift")
async def call_clean_current_shift(call: CallbackQuery):
    await call.answer(text="Текущая смена успешно очищена")
    await call.message.delete()

@admin_router.message(F.text == "🌀 Полная очистка базы заказов")
async def text_full_cleaning_orders(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="yes_full_clean_orders")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(1)

    await message.answer(text="Вы уверены, что хотите полностью очистить базу заказов?",
                         reply_markup=builder.as_markup())

@admin_router.callback_query(F.data == "yes_full_clean_orders")
async def call_full_clean_warning(call: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Очистить базу заказов", callback_data="start_full_clean_orders")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(1)

    await call.message.answer(text="Это действие НЕЛЬЗЯ ОТМЕНИТЬ!",
                         reply_markup=builder.as_markup())
    await call.message.delete()

@admin_router.callback_query(F.data == "start_full_clean_orders")
async def call_full_orders_clean(call: CallbackQuery):
    await db.full_orders_and_order_items_clean()
    await call.answer(text="База заказов успешно очищена.", show_alert=True)
    await call.message.delete()