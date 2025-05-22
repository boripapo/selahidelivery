import asyncio
import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import db, admins, bot


async def notify_admin_loop():
    await db.connect()
    logging.info(f"{__name__} initiated.")
    while True:
        logging.info(f"{__name__} is working.")
        new_orders = await db.fetch_new_orders()
        for order in new_orders:
            text = (
                f"<b>Новый заказ</b> {order["id"]}\n"
                f"<b>Имя:</b> {order["name"]}\n"
                f"<b>Телефон:</b> {order["phone"]}\n"
                f"<b>Адрес:</b> {order["address"]}\n"
                f"<b>Тип оплаты:</b> {"Наличные" if order["paymentmethod"] == "CASH" else "Карта курьеру"}\n"
                f"<b>Комментарий:</b> {order["comment"]}\n"
            )
            for admin_id in admins:
                bot.send_message(admin_id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_{order["id"]}")],
                    [InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{order["id"]}")]
                ]))
        await asyncio.sleep(15)
