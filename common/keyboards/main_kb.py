from aiogram.utils.keyboard import ReplyKeyboardBuilder

from create_bot import managers, couriers, admins, kitchen


def main_kb(user_telegram_id: int):
    builder = ReplyKeyboardBuilder()

    if user_telegram_id in managers:
        builder.button(text = "📖 Менеджер-панель")
    if user_telegram_id in [int(courier["id"]) for courier in couriers]:
        builder.button(text = "🛵 Курьер-панель")
    if user_telegram_id in admins:
        builder.button(text = "⚙️ Админ-панель")
    if user_telegram_id in kitchen:
        builder.button(text = "🍲 Кухня")

    builder.adjust(2,2)

    return builder.as_markup(resize_keyboard=True)