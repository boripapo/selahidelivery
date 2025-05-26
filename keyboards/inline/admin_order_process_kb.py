from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_order_process_kb(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"accept_{order_id}")
    builder.button(text="🚫 Отклонить", callback_data=f"reject_{order_id}")
    builder.adjust(2)
    return builder.as_markup()