import asyncio
import logging

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp, db, admins
from handlers import main_panel, manager_panel, courier_panel, util_handlers, admin_panel
from handlers.manager_panel import manager_broadcaster


async def set_commands():
    commands = [BotCommand(command="start", description="Старт"),
                BotCommand(command="menu", description="Меню"),
                BotCommand(command="about", description="О боте")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

@dp.startup.register
async def on_startup():
    await set_commands()
    await manager_broadcaster.resume()
    asyncio.create_task(manager_broadcaster.start())
    await manager_broadcaster.resume()
    for admin in admins:
        await bot.send_message(chat_id=admin, text="Бот запущен.")

@dp.shutdown.register
async def on_shutdown():
    for admin in admins:
        await bot.send_message(chat_id=admin, text="Бот остановлен.")

async def main():
    dp.include_router(util_handlers.util_router)
    dp.include_router(main_panel.main_router)
    dp.include_router(admin_panel.admin_router)
    dp.include_router(manager_panel.manager_router)
    dp.include_router(courier_panel.courier_router)
    try:
        await db.create_pool()

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logging.exception(f"{e}")
    finally:
        await db.close_pool()

        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())