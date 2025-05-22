from enum import Enum
from decouple import config

import asyncpg

DSN = f"postgresql://{config("DB_USER")}:{config("DB_PASS")}@{config("DB_HOST")}:{config("DB_PORT")}/{config("DB_NAME")}"

class OrderStatus(str, Enum):
    NEW = 'NEW'
    REJECTED = 'REJECTED'
    ASSIGNED = 'ASSIGNED'
    CANCELLED = 'CANCELLED'
    DELIVERED = 'DELIVERED'
    CLOSED = 'CLOSED'

class Database:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self.pool: asyncpg.pool | None = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self._dsn)

    async def fetch_new_orders(self) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT * FROM orders WHERE status = $1 ORDER BY id",
                OrderStatus.NEW.value
            )

    async def update_order_status(self, order_id: int, status: OrderStatus, courier_id: int | None = None):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE orders
                SET status = $1,
                    courier_id = COALESCE($2, courier_id)
                WHERE id = $3
                """,
                status.value, courier_id, order_id
            )