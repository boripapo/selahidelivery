from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from create_bot import bot, db
from db.enums import OrderStatus
from filters.IsAdminFilter import IsAdminFilter
from keyboards.admin_kb import admin_kb
from keyboards.inline.admin_order_process_kb import admin_order_process_kb
from keyboards.inline.courier_order_process_kb import courier_order_process_kb
from utils.order_formatting import get_formatted_order

router = Router()
router.message.filter(IsAdminFilter())

@router.message(F.text == "⚙️ Админ-панель")
async def text_admin_panel(message: Message):
    await message.answer(text="Админ-панель:",
                         reply_markup=admin_kb())

@router.message(F.text == "❇️ Меню заказов")
async def text_orders_menu(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🆕 Новые заказы")
    builder.button(text="💢 Ожидающие заказы")
    builder.button(text="🛵 Заказы в доставке")
    builder.button(text="⚙️ Админ-панель")
    builder.adjust(2,2)

    await message.answer(text="Меню заказов:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "🆕 Новые заказы")
async def text_new_orders(message: Message):
    orders = await db.get_new_orders()
    if not orders:
        await message.answer("Новых заказов нет.")
        return
    for order in orders:
        await message.answer(get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=admin_order_process_kb(order["id"]))

@router.message(F.text == "💢 Ожидающие заказы")
async def text_pending_orders(message: Message):
    orders = await db.get_orders_by_status(OrderStatus.REJECTED)
    if not orders:
        await message.answer("Ожидающих заказов нет.")
        return
    for order in orders:
        await message.answer(text=get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=admin_order_process_kb(order["id"]))

@router.message(F.text == "🛵 Заказы в доставке")
async def text_in_delivery_orders(message: Message):
    orders = await db.get_orders_by_status(OrderStatus.IN_DELIVERY)
    if not orders:
        await message.answer("Заказов в доставке нет.")
        return
    for order in orders:
        await message.answer(text=get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Закрыть окно",callback_data="close_tab")]]))




@router.message(F.text == "📖 История заказов")
async def text_order_history(message: Message):
    pass

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

