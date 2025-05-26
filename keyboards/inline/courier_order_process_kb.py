from aiogram.utils.keyboard import InlineKeyboardBuilder

def courier_order_process_kb(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"accept_{order_id}")
    builder.button(text="🚫 Отклонить", callback_data=f"reject_{order_id}")
    builder.adjust(2)
    return builder.as_markup()

def courier_active_order_kb(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Закрыть заказ", callback_data=f"delivered_{order_id}")
    builder.button(text="❌ Отменить заказ", callback_data=f"rejected_{order_id}")
    builder.button(text="Закрыть окно", callback_data="close_tab")
    builder.adjust(2,1)
    return builder.as_markup()
