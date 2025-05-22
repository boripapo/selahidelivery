from aiogram.utils.keyboard import ReplyKeyboardBuilder

from create_bot import admins, couriers


def main_kb(user_telegram_id: int):
    builder = ReplyKeyboardBuilder()

    builder.button(text="Проверить заказ")
    if user_telegram_id in admins:
        builder.button(text="⚙️ Админ-панель")
    if user_telegram_id in couriers:
        builder.button(text="🛵 Курьер-панель")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)
