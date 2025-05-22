from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import db

def admin_order_process_kb(order_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Подтвердить", callback_data=f"accept_{order_id}")
    builder.button(text="🚫 Отклонить", callback_data=f"reject_{order_id}")
    builder.adjust(2)

    return builder.as_markup()

def admin_courier_assign_kb(order_id: int):
    builder = InlineKeyboardBuilder()
    available_couriers = db.get_available_couriers()
    for courier in available_couriers:
        builder.button(text=f"{courier["name"]}", callback_data=f"assign_{courier["courier_id"]}")