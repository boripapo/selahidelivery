from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text="🆕 Получить список новых заказов")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)