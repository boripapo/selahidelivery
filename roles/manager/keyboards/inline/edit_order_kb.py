from aiogram.utils.keyboard import InlineKeyboardBuilder


def edit_order_kb(order_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text="👤 Имя", callback_data=f"edit_name:{order_id}")
    builder.button(text="🏠 Адрес", callback_data=f"edit_address:{order_id}")
    builder.button(text="🛒 Товары", callback_data=f"edit_items:{order_id}")
    builder.button(text="⬅️ Назад", callback_data=f"order_back:{order_id}")

    return builder.as_markup()