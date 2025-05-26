from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import bot, db
from db.enums import OrderStatus
from filters.IsCourierFilter import IsCourierFilter
from keyboards.courier_kb import courier_kb
from keyboards.inline.courier_order_process_kb import courier_active_order_kb
from utils.order_formatting import get_formatted_order

router = Router()
router.message.filter(IsCourierFilter())

@router.message(F.text == "🛵 Курьер-панель")
async def text_courier_panel(message: Message):
    msg = await bot.send_message(message.chat.id,
                                 text="Курьер-панель:",
                                 reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    await message.answer(text="Курьер-панель:",
                         reply_markup=courier_kb())

@router.message(F.text == "📃 История моих заказов")
async def text_my_order_history(message: Message):
    pass

@router.message(F.text == "📫 Мои активные заказы")
async def text_ongoing_orders(message: Message):
    ongoing_orders = await db.get_orders_by_courier_and_status(message.from_user.id, OrderStatus.ASSIGNED)

    builder = InlineKeyboardBuilder()
    builder.button(text = "Закрыть окно", callback_data="close_tab")
    for order in ongoing_orders:
        builder.button(text=f"<b>{order["id"]}:</b> {order["address"]}",callback_data=f"viewOrder_{order["id"]}")

    await message.answer(text="Список активных заказов:",reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("viewOrder_"))
async def view_order(call: CallbackQuery):
    _, order_id = call.data.split("_")
    await call.message.answer(text=get_formatted_order(await db.get_order_by_id(order_id), await db.get_items_by_order_id(order_id)),
                              reply_markup=courier_active_order_kb(int(order_id)))



