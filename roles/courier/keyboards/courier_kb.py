from aiogram.utils.keyboard import ReplyKeyboardBuilder


def courier_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text = "📫 Активные заказы")
    builder.button(text = "📃 История моих заказов")
    builder.button(text = "⏯️ Смена")
    builder.button(text = "⬅️ На главную")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)