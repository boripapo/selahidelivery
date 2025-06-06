from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asyncpg import Record

from create_bot import bot, db
from db.enums import OrderStatus
from filters.IsManagerFilter import IsManagerFilter
from keyboards.manager_kb import manager_kb
from keyboards.inline.manager_order_process_kb import manager_order_process_kb
from keyboards.inline.courier_order_process_kb import courier_order_process_kb
from utils.order_formatting import get_formatted_order

router = Router()
router.message.filter(IsManagerFilter())

#Даты открытия и закрытия текущей смены
open_shift : datetime = None
close_shift : datetime = None

@router.message(F.text == "⬅️ Менеджер-панель")
@router.message(F.text == "📖 Менеджер-панель")
async def text_manager_panel(message: Message):
    await message.answer(text="Менеджер-панель:",
                         reply_markup=manager_kb())

#Смена------------------------------------------------------------------------------------------------------------------

@router.message(F.text == "⏯️ Смена")
async def text_shift(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="▶️ Открыть смену")
    builder.button(text="⏹️ Закрыть смену")
    builder.button(text="⬅️ Менеджер-панель")
    builder.adjust(2,2)

    await message.answer(text="Смена:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "▶️ Открыть смену")
async def text_open_shift(message: Message):
    global open_shift, close_shift
    if open_shift is not None:
        await message.answer("Смена уже открыта!")
        return
    open_shift = datetime.now()
    close_shift = None

    await message.answer(
        f"Смена открыта.\n\n"
        f"<b>{open_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
        f"Менеджер: {message.from_user.first_name} @{message.from_user.username}"
    )

@router.message(F.text == "⏹️ Закрыть смену")
async def text_close_shift(message: Message):
    global open_shift, close_shift
    if close_shift is not None:
        await message.answer("Смена уже закрыта!")
        return
    close_shift = datetime.now()
    open_shift = None

    await message.answer(
        f"Смена закрыта.\n\n"
        f"<b>{close_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
        f"Менеджер: {message.from_user.first_name} @{message.from_user.username}"
    )

#Меню заказов-----------------------------------------------------------------------------------------------------------

@router.message(F.text == "❇️ Меню заказов")
async def text_orders_menu(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🆕 Новые заказы")
    builder.button(text="💢 Ожидающие заказы")
    builder.button(text="🛵 Заказы в доставке")
    builder.button(text="📁 История заказов")
    builder.button(text="⬅️ Менеджер-панель")
    builder.adjust(3,2)

    await message.answer(text="Меню заказов:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "🆕 Новые заказы")
async def text_new_orders(message: Message):
    orders = await db.get_new_orders()
    if not orders:
        await message.answer("Новых заказов нет.")
        return
    for order in orders:
        await message.answer(get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=manager_order_process_kb(order["id"]))

@router.message(F.text == "💢 Ожидающие заказы")
async def text_pending_orders(message: Message):
    orders = await db.get_orders_by_status(OrderStatus.REJECTED)
    if not orders:
        await message.answer("Ожидающих заказов нет.")
        return
    for order in orders:
        await message.answer(text=get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=manager_order_process_kb(order["id"]))

@router.message(F.text == "🛵 Заказы в доставке")
async def text_in_delivery_orders(message: Message):
    orders = await db.get_orders_by_status(OrderStatus.IN_DELIVERY)
    if not orders:
        await message.answer("Заказов в доставке нет.")
        return
    for order in orders:
        await message.answer(text=get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Закрыть окно",callback_data="close_tab")]]))

@router.message(F.text == "📁 История заказов")
async def text_orders_history(message: Message): #Хендлер для вызова каталога
    orders = await db.get_inactive_orders()
    if not orders:
        await message.answer("История заказов пуста.")
        return
    await render_catalog(message, page=1, is_edit=False, items=orders)

async def render_catalog(message, page: int = 1, is_edit: bool = False, items: list[Record] = None): #Функция для рендера
    ITEMS_PER_PAGE = 10
    total_pages = (len(items) - 1) // ITEMS_PER_PAGE + 1

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = items[start:end]

    text = f"История заказов - <b>{page}/{total_pages}</b>\n\n"
    for order in page_items:
        order_items = await db.get_items_by_order_id(order["id"])
        total_price = 0
        for order_item in order_items:
            total_price += order_item["price"]
        text += f"{order["id"]} : {order["name"]} : Сумма = {total_price}\n"

    kb = InlineKeyboardBuilder()

    if page > 1:
        kb.button(text="⬅️ Назад", callback_data=f"page:{page-1}")
    if page < total_pages:
        kb.button(text="➡️ Вперёд", callback_data=f"page:{page+1}")
    kb.button(text="❌ Закрыть", callback_data=f"page:close")
    kb.adjust(2,1)

    if is_edit:
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        await message.answer(text, reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("page:"))
async def catalog_pagination(call: CallbackQuery): #Хендлер пагинации каталога
    _, page = call.data.split(":")
    if page == "close":
        await call.message.delete()
    await call.message.edit_reply_markup()
    await render_catalog(call.message, page=int(page), is_edit=True)
    await call.answer()

#Инлайн оформление заказа-----------------------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("approve_"))
async def order_approve(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])

    available_couriers = await db.get_available_couriers()

    builder = InlineKeyboardBuilder()
    for courier in available_couriers:
        builder.button(text=f"{courier["name"]}", callback_data=f"assign_{order_id}_{courier["id"]}")
    await call.message.edit_reply_markup(reply_markup=builder.as_markup())
    await call.answer()

@router.callback_query(F.data.startswith("assign_"))
async def order_assign(call: CallbackQuery):
    order_id, courier_id = list(map(int, call.data.split("_")[1:]))
    await db.update_order_status(order_id=order_id, status=OrderStatus.ASSIGNED, courier_id=courier_id)
    await bot.send_message(chat_id=courier_id,
                           text=get_formatted_order(await db.get_order_by_id(order_id),
                                                    await db.get_items_by_order_id(order_id)),
                           reply_markup=courier_order_process_kb(order_id))
    await call.message.answer(f"Заказ {order_id} был назначен курьеру {courier_id}")
    await call.message.delete()

