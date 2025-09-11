import asyncio
import logging

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp, db, admins
from common.handlers import main_panel, util_handlers
from roles.manager.handlers import manager_panel
from roles.courier.handlers import courier_panel
from roles.admin.handlers import admin_panel
from roles.manager.handlers.manager_panel import manager_broadcaster


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
    dp.include_router(util_handlers.router)
    dp.include_router(main_panel.router)
    dp.include_router(admin_panel.router)
    dp.include_router(manager_panel.router)
    dp.include_router(courier_panel.router)
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