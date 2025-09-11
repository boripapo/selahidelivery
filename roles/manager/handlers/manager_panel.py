from datetime import datetime
from typing import Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asyncpg import Record

from create_bot import bot, db, admins
from common.db.enums import OrderStatus
from roles.manager.filters.IsManagerFilter import IsManagerFilter
from roles.manager.keyboards.manager_kb import manager_kb
from roles.manager.keyboards.inline.manager_order_process_kb import manager_order_process_kb
from roles.courier.keyboards.inline.courier_order_process_kb import courier_order_process_kb
from roles.manager.services.ManagerBroadcaster import ManagerBroadcaster
from common.utils.order_formatting import get_formatted_order

router = Router()
router.message.filter(IsManagerFilter())

manager_broadcaster = ManagerBroadcaster()

#Даты открытия и закрытия текущей смены
open_shift : datetime = None
close_shift : datetime = None

@router.message(F.text == "⬅️ Менеджер-панель")
@router.message(F.text == "📖 Менеджер-панель")
async def manager_panel(message: Message):
    await message.answer(text="Менеджер-панель:",
                         reply_markup=manager_kb())



#Смена------------------------------------------------------------------------------------------------------------------
@router.message(F.text == "⏯️ Смена")
async def shift(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="▶️ Открыть смену")
    builder.button(text="⏹️ Закрыть смену")
    builder.button(text="⬅️ Менеджер-панель")
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
        f"Менеджер: {message.from_user.first_name} @{message.from_user.username}"
    )
    for admin_id in admins:
        await bot.send_message(chat_id=admin_id, text=f"<b>{open_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
                                                      f"Менеджер {message.from_user.id} открыл смену.")

@router.message(F.text == "⏹️ Закрыть смену")
async def close_shift(message: Message):
    global open_shift, close_shift
    if close_shift is not None:
        await message.answer("Смена уже закрыта!")
        return
    close_shift = datetime.now()

    #Присваивает всем заказам в текущей смене статус CLOSED
    await db.set_orders_closed(open_shift=open_shift, close_shift = close_shift)

    open_shift = None

    await message.answer(
        f"Смена закрыта.\n\n"
        f"<b>{close_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
        f"Менеджер: {message.from_user.first_name} @{message.from_user.username}"
    )
    for admin_id in admins:
        await bot.send_message(chat_id=admin_id, text=f"<b>{close_shift.strftime("%d.%m.%Y - %H:%M")}</b>\n\n"
                                                      f"Менеджер {message.from_user.id} закрыл смену.")



#Меню заказов-----------------------------------------------------------------------------------------------------------
@router.message(F.text == "❇️ Меню заказов")
async def orders_menu(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🆕 Новые заказы")
    builder.button(text="💢 Ожидающие заказы")
    builder.button(text="🛵 Заказы в доставке")
    builder.button(text="📁 История заказов")
    builder.button(text="⬅️ Менеджер-панель")
    builder.adjust(3,2)

    await message.answer(text="Меню заказов:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "🆕 Новые заказы")
@router.callback_query(F.data == "show_new_orders")
async def new_orders(message: Union[Message, CallbackQuery]):
    if isinstance(message, CallbackQuery):
        await message.answer()
        chat_message = message.message
    else:
        chat_message = message

    orders = await db.get_new_orders()
    if not orders:
        await chat_message.answer("Новых заказов нет.")
        return
    for order in orders:
        await chat_message.answer(get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=manager_order_process_kb(order["id"]))

@router.message(F.text == "💢 Ожидающие заказы")
async def pending_orders(message: Message):
    orders = await db.get_orders_by_status(OrderStatus.REJECTED)
    if not orders:
        await message.answer("Ожидающих заказов нет.")
        return
    for order in orders:
        await message.answer(text=get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=manager_order_process_kb(order["id"]))

@router.message(F.text == "🛵 Заказы в доставке")
async def in_delivery_orders(message: Message):
    orders = await db.get_orders_by_status(OrderStatus.IN_DELIVERY)
    if not orders:
        await message.answer("Заказов в доставке нет.")
        return
    for order in orders:
        await message.answer(text=get_formatted_order(order, await db.get_items_by_order_id(order["id"])),
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Закрыть окно",callback_data="close_tab")]]))

@router.message(F.text == "📁 История заказов")
async def orders_history(message: Message):
    orders = await db.get_inactive_orders()
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

@router.callback_query(F.data.startswith("view_order:"))
async def view_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])

    order = await db.get_order_by_id(order_id)
    items = await db.get_items_by_order_id(order_id)
    if order is None:
        await call.message.answer("Ошибка: заказ не найден.")
        await call.answer()
        return

    builder = InlineKeyboardBuilder()

    if order["status"] == 'NEW':
        builder.button(text="✅ Подтвердить", callback_data=f"approve:{order_id}")
        builder.button(text="🚫 Отклонить", callback_data=f"decline:{order_id}")
        builder.button(text="✏️ Редактировать", callback_data=f"edit_order:{order_id}")
        builder.button(text="⭕️ Удалить", callback_data=f"delete_order:{order_id}")
        builder.button(text="Закрыть окно", callback_data="close_tab")
        builder.adjust(2, 1, 1)
    else:
        builder.button(text="🗑 Удалить", callback_data=f"delete_order:{order_id}")
        builder.button(text="Закрыть окно", callback_data="close_tab")

    await call.message.answer(get_formatted_order(order,items), reply_markup=builder.as_markup())
    await call.answer()

@router.callback_query(F.data.startswith("delete_order:"))
async def delete_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm_delete_order:{order_id}")
    builder.button(text="❌ Нет", callback_data="close_tab")
    builder.adjust(2)

    await call.message.answer(text=f"Вы действительно хотите удалить заказ № <b>{order_id}</b>?", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("confirm_delete_order:"))
async def confirm_delete_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])

    await db.delete_order_by_id(order_id)
    await call.answer(f"Заказ {order_id} удален.")
    await call.message.delete()



#Инлайн оформление заказа-----------------------------------------------------------------------------------------------
@router.callback_query(F.data.startswith("approve:"))
async def order_approve(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])

    available_couriers = await db.get_available_couriers()

    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=f"order_back:{order_id}")
    for courier in available_couriers:
        builder.button(text=f"{courier["name"]}", callback_data=f"assign:{order_id}:{courier["id"]}")
    await call.message.edit_reply_markup(reply_markup=builder.as_markup())
    await call.answer()

@router.callback_query(F.data.startswith("decline:"))
async def order_decline(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])

    await db.update_order_status(order_id=order_id, status=OrderStatus.CANCELLED)
    await call.answer(f"Заказ {order_id} был отклонён.")
    await call.message.delete()

#Редактирование заказа----------------------------------------------------------
class OrderEdit(StatesGroup):
    edit_name = State()
    edit_address = State()
    edit_items = State()

@router.callback_query(F.data.startswith("edit_order:"))
async def edit_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])

    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Имя", callback_data=f"edit_name:{order_id}")
    builder.button(text="🏠 Адрес", callback_data=f"edit_address:{order_id}")
    builder.button(text="🛒 Товары", callback_data=f"edit_items:{order_id}")
    builder.button(text="⬅️ Назад", callback_data=f"order_back:{order_id}")

    await call.message.edit_reply_markup(reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("edit_"))
async def order_edit(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split(":")[1])
    edit_type = call.data.split("_")[1].split(":")
    match edit_type:
        case "name":
            await call.message.answer(text="Введите новое имя:")
            await state.set_state(OrderEdit.edit_name)
        case "address":
            await call.message.answer(text="Введите новый адрес:")
            await state.set_state(OrderEdit.edit_address)
        case "items":
            await call.message.answer(text="Измените товары в заказе:")
            await state.set_state(OrderEdit.edit_items)
        case _:
            pass
    await state.update_data(order_id=order_id)
    await call.answer()

@router.message(F.text, OrderEdit.edit_name)
async def order_edit_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await db.update_order_name(order_id=data.get("order_id"), name=data.get("name"))
    await message.answer(f"Имя в заказе {data.get("order_id")} было изменено на {data.get("name")}")
    await state.clear()

@router.message(F.text, OrderEdit.edit_address)
async def order_edit_address(message: Message, state: FSMContext):
    await state.update_data(address = message.text)
    data = await state.get_data()
    await db.update_order_address(order_id=data.get("order_id"), name=data.get("address"))
    await message.answer(f"Адрес в заказе {data.get("order_id")} был изменен на {data.get("address")}")
    await state.clear()

@router.message(F.text, OrderEdit.edit_items)
async def order_edit_items(message: Message, state: FSMContext):
    await message.answer(text="Редактирование товаров в заказе пока недоступно.")
    await state.clear()
#-------------------------------------------------------------------------------


@router.callback_query(F.data.startswith("assign:"))
async def order_assign(call: CallbackQuery):
    order_id, courier_id = list(map(int, call.data.split(":")[1:]))
    await db.update_order_status(order_id=order_id, status=OrderStatus.ASSIGNED, courier_id=courier_id)
    await bot.send_message(chat_id=courier_id,
                           text=get_formatted_order(await db.get_order_by_id(order_id),
                                                    await db.get_items_by_order_id(order_id)),
                           reply_markup=courier_order_process_kb(order_id))
    await call.answer(f"Заказ {order_id} был назначен курьеру {courier_id}")
    await call.message.delete()

@router.callback_query(F.data.startswith("order_back:"))
async def order_back(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await call.message.edit_reply_markup(reply_markup=manager_order_process_kb(order_id))
    await call.answer()