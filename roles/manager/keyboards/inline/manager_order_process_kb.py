from aiogram.utils.keyboard import InlineKeyboardBuilder

def manager_order_process_kb(order):
    builder = InlineKeyboardBuilder()

    if order["status"] == "NEW":
        builder.button(text="✅ Подтвердить", callback_data=f"approve_order:{order["id"]}")
        builder.button(text="🚫 Отклонить", callback_data=f"decline_order:{order["id"]}")
    builder.button(text="✏️ Редактировать", callback_data=f"edit_order:{order["id"]}")
    builder.button(text="⭕️ Удалить", callback_data=f"delete_order:{order["id"]}")
    builder.button(text="Закрыть окно", callback_data="close_tab")

    builder.adjust(2,1,1)

    return builder.as_markup()