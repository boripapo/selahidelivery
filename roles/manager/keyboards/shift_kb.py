from aiogram.utils.keyboard import ReplyKeyboardBuilder


def shift_kb():
    builder = ReplyKeyboardBuilder()

    builder.button(text="▶️ Открыть смену")
    builder.button(text="⏹️ Закрыть смену")
    builder.button(text="⬅️ Менеджер-панель")

    builder.adjust(2, 2)

    return builder.as_markup(resize_keyboard=True)