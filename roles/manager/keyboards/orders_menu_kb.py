from aiogram.utils.keyboard import ReplyKeyboardBuilder


def orders_menu_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text="🆕 Новые заказы")
    builder.button(text="💢 Ожидающие заказы")
    builder.button(text="🛵 Заказы в доставке")
    builder.button(text="📁 История заказов")
    builder.button(text="⬅️ Менеджер-панель")

    builder.adjust(3,2)

    return builder.as_markup(resize_keyboard=True)