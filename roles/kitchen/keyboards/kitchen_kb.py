from aiogram.utils.keyboard import ReplyKeyboardBuilder


def kitchen_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text = "❇️ Меню кухни")
    builder.button(text = "")
    builder.button(text = "⬅️ На главную")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)