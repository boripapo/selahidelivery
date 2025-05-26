from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import bot, db
from db.enums import OrderStatus
from filters.IsAdminFilter import IsAdminFilter
from keyboards.admin_kb import admin_kb
from keyboards.inline.admin_order_process_kb import admin_order_process_kb
from keyboards.inline.courier_order_process_kb import courier_order_process_kb
from utils.order_formatting import get_formatted_new_order

router = Router()
router.message.filter(IsAdminFilter())

@router.message(F.text == "⚙️ Админ-панель")
async def text_admin_panel(message: Message):
    msg = await bot.send_message(message.chat.id,
                                 text="Админ-панель:",
                                 reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    await message.answer(text="Админ-панель:",
                         reply_markup=admin_kb())

@router.message(F.text == "🆕 Получить новые заказы")
async def text_get_new_orders(message: Message):
    orders = await db.get_new_orders()
    for order in orders:
        await message.answer(get_formatted_new_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=admin_order_process_kb(order["id"]))

@router.message(F.text == "📖 История заказов")
async def text_order_history(message: Message):
    pass

@router.callback_query(F.data.startswith("accept_"))
async def order_accept(call: CallbackQuery):
    order_id = int(call.data.split("_")[1])

    available_couriers = await db.get_available_couriers()
    builder = InlineKeyboardBuilder()
    for courier in available_couriers:
        builder.button(text=f"{courier["name"]}",
                       callback_data=f"assign_{courier["id"]}_{order_id}")
    await call.message.edit_reply_markup(reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("assign_"))
async def order_assign(call: CallbackQuery):
    _, courier_id, order_id = call.data.split("_")

    await bot.send_message(call.from_user.id, f"<b>Заказ <code>{order_id}</code> был назначен курьеру {courier_id}</b>")
    await db.update_order_status(int(order_id), OrderStatus.ASSIGNED, int(courier_id))
    await bot.send_message(int(courier_id),
                           get_formatted_new_order(await db.get_order_by_id(order_id), await db.get_items_by_order_id(order_id)),
                           reply_markup=courier_order_process_kb(int(order_id)))
    await call.message.delete()



