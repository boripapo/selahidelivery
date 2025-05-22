from aiogram.utils.keyboard import ReplyKeyboardBuilder


def courier_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text = "Активный заказ")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)