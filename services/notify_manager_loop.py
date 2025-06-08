import asyncio
import logging

from create_bot import db, bot, managers
from keyboards.inline.manager_order_process_kb import manager_order_process_kb
from utils.order_formatting import get_formatted_order


async def notify_manager_loop():
    await db.connect()
    logging.info(f"{__name__} initiated.")
    while True:
        logging.info(f"{__name__} is working.")
        new_orders = await db.get_new_orders()
        for order in new_orders:
            for manager_id in managers:
                bot.send_message(manager_id, get_formatted_order(order), reply_markup=manager_order_process_kb(order))
        await asyncio.sleep(15)