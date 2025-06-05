from aiogram.utils.keyboard import InlineKeyboardBuilder

def manager_order_process_kb(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"approve_{order_id}")
    builder.button(text="🚫 Отклонить", callback_data=f"decline_{order_id}")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(2,1)
    return builder.as_markup()