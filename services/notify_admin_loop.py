import asyncio
import logging

from create_bot import db, admins, bot
from keyboards.inline.admin_order_process_kb import admin_order_process_kb
from utils.order_formatting import get_formatted_new_order


async def notify_admin_loop():
    await db.connect()
    logging.info(f"{__name__} initiated.")
    while True:
        logging.info(f"{__name__} is working.")
        new_orders = await db.get_new_orders()
        for order in new_orders:
            for admin_id in admins:
                bot.send_message(admin_id, get_formatted_new_order(order), reply_markup=admin_order_process_kb(order["id"]))
        await asyncio.sleep(15)
