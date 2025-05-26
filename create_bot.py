import asyncio

import asyncpg
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config

from db.database import Database

admins = [int(admin_id) for admin_id in config("ADMINS").split(",")]
couriers = list()

db = Database()

async def get_couriers():
    global couriers
    conn = await asyncpg.connect(host=config("DB_HOST"),
            port=int(config("DB_PORT")),
            database=config("DB_NAME"),
            user=config("DB_USER"),
            password=config("DB_PASS"))

    records = await conn.fetch(
        "SELECT * FROM couriers"
    )
    couriers = [int(record["id"]) for record in records]
    await conn.close()

asyncio.run(get_couriers())

scheduler = AsyncIOScheduler(timezone = "Europe/Moscow")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token = config("TOKEN"), default = DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

