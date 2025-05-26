from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import db, bot, admins, couriers
from db.enums import OrderStatus, CourierStatus
from filters.IsCourierFilter import IsCourierFilter
from keyboards.courier_kb import courier_kb
from keyboards.inline.courier_order_process_kb import courier_active_order_kb
from utils.order_formatting import get_formatted_order

router = Router()
router.message.filter(IsCourierFilter())

@router.message(F.text == "🛵 Курьер-панель")
async def text_courier_panel(message: Message):
    await message.answer(text="Курьер-панель:",
                         reply_markup=courier_kb())

@router.message(F.text == "📃 История моих заказов")
async def text_my_order_history(message: Message):
    pass

@router.message(F.text == "📫 Активные заказы")
async def text_ongoing_orders(message: Message):
    on_delivery_orders = await db.get_orders_by_courier_and_status(message.from_user.id, OrderStatus.IN_DELIVERY)
    if not on_delivery_orders:
        await message.answer("Активных заказов нет.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text = "Закрыть окно", callback_data="close_tab")
    for order in on_delivery_orders:
        builder.row(InlineKeyboardButton(text=f"{order["id"]}: {order["address"]}",callback_data=f"order_{order["id"]}"))
    builder.adjust(1)
    await message.answer(text="Активные заказы:",reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("order_"))
async def view_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    await call.message.answer(text=get_formatted_order(await db.get_order_by_id(order_id), await db.get_items_by_order_id(order_id)),
                              reply_markup=courier_active_order_kb(order_id))
    await call.answer()

@router.callback_query(F.data.startswith("accept_"))
async def accept_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.IN_DELIVERY)
    await db.update_courier_status(courier_id=call.from_user.id, status=CourierStatus.DELIVERING)
    await call.answer(text=f"Заказ {order_id} принят на доставку.")
    await call.message.delete()

@router.callback_query(F.data.startswith("reject_"))
async def reject_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.REJECTED)
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"Курьер {couriers[call.from_user.id]} отказался от доставки заказа {order_id}. Назначьте курьера на заказ.")
    await call.answer("Вы отказались от доставки этого заказа.")
    await call.message.delete()

@router.callback_query(F.data.startswith("delivered_"))
async def delivered_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.DELIVERED)
    await call.answer("Заказ успешно доставлен.")
    await call.message.delete()

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])
    await db.update_order_status(order_id=order_id, status=OrderStatus.CANCELLED)
    for admin in admins:
        await bot.send_message(chat_id=admin, text=f"Курьер {couriers[call.from_user.id]} отменил доставку заказа {order_id}")
    await call.answer("Заказ был отменен.")
    await call.message.delete()




