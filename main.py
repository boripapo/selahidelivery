import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, admins, dp
from handlers import commands, admin_panel, courier_panel
from services.notify_admin_loop import notify_admin_loop


async def set_commands():
    commands = [BotCommand(command="start", description="Старт"),
                BotCommand(command="menu", description="Меню")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

async def start_bot():
    await set_commands()
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, "Бот запущен.")
    except:
        pass

async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, "Бот остановлен.")
    except:
        pass

async def main():
    dp.include_router(commands.router)
    dp.include_router(admin_panel.router)
    dp.include_router(courier_panel.router)

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        #task = asyncio.create_task(notify_admin_loop())
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

asyncio.run(main())
