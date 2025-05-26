from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text = "❇️ Меню заказов")
    #builder.button(text = "📖 История заказов")
    builder.button(text = "⬅️ На главную")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)