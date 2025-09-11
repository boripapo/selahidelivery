from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asyncpg import Record

from create_bot import db, bot, managers, couriers
from common.db.enums import OrderStatus, CourierStatus
from roles.courier.filters.IsCourierFilter import IsCourierFilter
from roles.courier.keyboards.courier_kb import courier_kb
from roles.courier.keyboards.inline.courier_order_process_kb import courier_active_order_kb
from common.utils.order_formatting import get_formatted_order

router = Router()
router.message.filter(IsCourierFilter())

#Даты открытия и закрытия текущей смены
open_shift : datetime = None
close_shift : datetime = None

@router.message(F.text == "⬅️ Курьер-панель")
@router.message(F.text == "🛵 Курьер-панель")
async def courier_panel(message: Message):
    await message.answer(text="Курьер-панель:",
                         reply_markup=courier_kb())

@router.message(F.text == "📃 История моих заказов")
async def courier_orders_history(message: Message):
    orders = await db.get_orders_by_courier(message.from_user.id)
    if not orders:
        await message.answer("История заказов пуста.")
        return
    await render_catalog(message, page=1, is_edit=False, items=orders)

async def render_catalog(message, page: int = 1, is_edit: bool = False, items: list[Record] = None):
    # Функция для рендера
    ITEMS_PER_PAGE = 5
    total_pages = (len(items) - 1) // ITEMS_PER_PAGE + 1

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = items[start:end]

    catalog_kb = InlineKeyboardBuilder()
    text = f"История заказов - <b>{page}/{total_pages}</b>"
    for order in page_items:
        order_items = await db.get_items_by_order_id(order["id"])
        total_price = 0
        for order_item in order_items:
            total_price += order_item["price"]
        catalog_kb.button(text=f"{order["id"]} - {order["name"]} - {total_price}р.", callback_data=f"view_order:{order["id"]}")
    catalog_kb.adjust(1)

    buttons_kb = InlineKeyboardBuilder()
    if page > 1:
        buttons_kb.button(text="⬅️ Назад", callback_data=f"page:{page-1}")
    if page < total_pages:
        buttons_kb.button(text="➡️ Вперёд", callback_data=f"page:{page+1}")
    buttons_kb.button(text="Закрыть окно", callback_data="close_tab")
    buttons_kb.adjust(2,1)

    catalog_kb.attach(buttons_kb)

    if is_edit:
        await message.edit_text(text, reply_markup=catalog_kb.as_markup())
    else:
        await message.answer(text, reply_markup=catalog_kb.as_markup())

@router.callback_query(F.data.startswith("page:"))
async def catalog_pagination(call: CallbackQuery):
    #Хендлер пагинации каталога
    page = int(call.data.split(":")[1])
    await call.message.edit_reply_markup()
    await render_catalog(call.message, page=int(page), is_edit=True)
    await call.answer()



#Смена------------------------------------------------------------------------------------------------------------------
@router.message(F.text == "⏯️ Смена")
async def shift(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="▶️ Открыть смену")
    builder.button(text="⏹️ Закрыть смену")
    builder.button(text="⬅️ Курьер-панель")
    builder.adjust(2,2)

    await message.answer(text="Смена:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "▶️ Открыть смену")
async def open_shift(message: Message):
    global open_shift, close_shift
    if open_shift is not None:
        await message.answer("Смена уже открыта!")
        return
    open_shift = datetime.now()
    close_shift = None

    await message.answer(
        f"Смена открыта.\n\n"
        f"<b>{open_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
        f"Курьер: {message.from_user.first_name} @{message.from_user.username}"
    )

@router.message(F.text == "⏹️ Закрыть смену")
async def close_shift(message: Message):
    global open_shift, close_shift
    if close_shift is not None:
        await message.answer("Смена уже закрыта!")
        return
    close_shift = datetime.now()
    open_shift = None

    await message.answer(
        f"Смена закрыта.\n\n"
        f"<b>{close_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
        f"Курьер: {message.from_user.first_name} @{message.from_user.username}"
    )



#Установить статус------------------------------------------------------------------------------------------------------
@router.message(F.text == "⚪️ Установить статус")
async def set_status(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🟢 Доступен")
    builder.button(text="🔴 Недоступен")
    builder.button(text="⬅️ Курьер-панель")
    builder.adjust(2,1)
    await message.answer(text="Установить статус:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "🟢 Доступен")
async def set_available(message: Message):
    courier = await db.get_courier_by_id(message.from_user.id)
    if courier["status"] == CourierStatus.DELIVERING:
        await message.answer("Сначала завершите доставку!")
    elif courier["status"] == CourierStatus.AVAILABLE:
        await message.answer("Ваш статус уже установлен как 🟢 Доступен.")
    else:
        await db.update_courier_status(message.from_user.id, CourierStatus.AVAILABLE)
        await message.answer("Ваш статус изменен на 🟢 Доступен.")

@router.message(F.text == "🔴 Недоступен")
async def set_unavailable(message: Message):
    courier = await db.get_courier_by_id(message.from_user.id)
    if courier["status"] == CourierStatus.DELIVERING:
        await message.answer("Сначала завершите доставку!")
    elif courier["status"] == CourierStatus.UNAVAILABLE:
        await message.answer("Ваш статус уже установлен как 🔴 Недоступен.")
    else:
        await db.update_courier_status(message.from_user.id, CourierStatus.UNAVAILABLE)
        await message.answer("Ваш статус изменен на 🔴 Недоступен.")



#Активные заказы--------------------------------------------------------------------------------------------------------
@router.message(F.text == "📫 Активные заказы")
async def ongoing_orders(message: Message):
    in_delivery_orders = await db.get_orders_by_courier_and_status(message.from_user.id, OrderStatus.IN_DELIVERY)
    if not in_delivery_orders:
        await message.answer("Активных заказов нет.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text = "Закрыть окно", callback_data="close_tab")
    for order in in_delivery_orders:
        builder.row(InlineKeyboardButton(text=f"{order["id"]}: {order["address"]}",callback_data=f"order:{order["id"]}"))
    builder.adjust(1)
    await message.answer(text="Активные заказы:",reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("order:"))
async def view_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await call.message.answer(text=get_formatted_order(await db.get_order_by_id(order_id), await db.get_items_by_order_id(order_id)),
                              reply_markup=courier_active_order_kb(order_id))
    await call.answer()

@router.callback_query(F.data.startswith("accept:"))
async def accept_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.IN_DELIVERY)
    await db.update_courier_status(courier_id=call.from_user.id, status=CourierStatus.DELIVERING)
    await call.answer(text=f"Заказ {order_id} принят на доставку.")
    await call.message.delete()

@router.callback_query(F.data.startswith("reject:"))
async def reject_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.REJECTED)
    for manager_id in managers:
        await bot.send_message(chat_id=manager_id, text=f"Курьер {couriers[call.from_user.id]} отказался от доставки заказа {order_id}. Назначьте курьера на заказ.")
    await call.answer("Вы отказались от доставки этого заказа.")
    await call.message.delete()

@router.callback_query(F.data.startswith("delivered:"))
async def delivered_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.DELIVERED)
    await db.update_courier_status(courier_id=call.from_user.id, status=CourierStatus.AVAILABLE)
    await call.answer("Заказ успешно доставлен.")
    await call.message.delete()

@router.callback_query(F.data.startswith("cancel:"))
async def cancel_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.CANCELLED)
    await db.update_courier_status(courier_id=call.from_user.id, status=CourierStatus.AVAILABLE)
    for manager_id in managers:
        await bot.send_message(chat_id=manager_id, text=f"Курьер {couriers[call.from_user.id]} отменил доставку заказа {order_id}")
    await call.answer("Заказ был отменен.")
    await call.message.delete()