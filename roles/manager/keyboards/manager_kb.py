from aiogram.utils.keyboard import ReplyKeyboardBuilder


def manager_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text = "❇️ Меню заказов")
    #builder.button(text = "⏯️ Смена")
    builder.button(text = "⬅️ На главную")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)