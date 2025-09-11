from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text = "🔎 История заказов")
    builder.button(text = "📊 Статистика")
    builder.button(text = "♻️ Очистка базы данных")
    #builder.button(text = "⏫ Заполнить БД")
    builder.button(text = "⬅️ На главную")

    builder.adjust(3,2)

    return builder.as_markup(resize_keyboard=True)