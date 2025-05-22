import logging
from typing import Optional

from decouple import config

import asyncpg

from db.enums import OrderStatus, CourierStatus


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=config("DB_HOST"),
            port=int(config("DB_PORT")),
            database=config("DB_NAME"),
            user=config("DB_USER"),
            password=config("DB_PASS"),
            max_size=20
        )
        logging.info("PostgreSQL connection acquired.")

    async def close_pool(self):
        if self.pool:
            await self.pool.close()
            logging.warn("PostgreSQL connection closed.")

    async def check_connection(self) -> bool:
        if not self.pool:
            return False

        try:
            async with self.pool.acquire() as connection:
                await connection.fetchval('1')
            return True
        except Exception as e:
            logging.exception(f"{e}")
            return False

    async def get_new_orders(self):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE status = $1 ORDER BY id",
                OrderStatus.NEW.value
            )
            return result

    async def update_order_status(self, order_id: int, status: OrderStatus, courier_id: int | None = None):
        async with self.pool.acquire() as connection:
            await connection.execute("""
            UPDATE orders
            SET status = $1,
                courier_id = $2
            WHERE id = $3
            """,
            status.value, courier_id, order_id
            )
    async def get_available_couriers(self):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM couriers WHERE status = $1",
                CourierStatus.AVAILABLE
            )
        return result