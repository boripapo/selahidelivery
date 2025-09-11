import asyncio
import logging

from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import db, bot, managers

class ManagerBroadcaster:
    resume_event = asyncio.Event()

    async def pause(self): #Приостановить работу
        self.resume_event.clear()
        logging.warn(f"{self.__class__.__name__} paused")

    async def resume(self): #Возобновить работу
        self.resume_event.set()
        logging.warn(f"{self.__class__.__name__} resumed")

    async def start(self):

        builder = InlineKeyboardBuilder()
        builder.button(text="Показать заказы", callback_data="show_new_orders")
        builder.button(text="Закрыть окно", callback_data="close_tab")

        logging.info(f"{self.__class__.__name__} initiated")
        while True:
            if not self.resume_event.is_set():
                await self.resume_event.wait()
            logging.info(f"{self.__class__.__name__} is working")

            new_orders = await db.get_new_orders()

            for order in new_orders:
                for manager_id in managers:
                    await bot.send_message(chat_id=manager_id, text="❗️ <b>Пришли новые заказы!</b>", reply_markup=builder.as_markup())
            await asyncio.sleep(20) #интервал проверок