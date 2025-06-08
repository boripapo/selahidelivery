from datetime import datetime
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


    #orders------------------------------------------------------------------------------------------------
    async def get_order_by_id(self, order_id: int):
        #Возвращает заказы по id
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "SELECT * FROM orders WHERE id = $1",
                order_id
            )
        return result

    async def get_new_orders(self):
        #Возвращает NEW заказы
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE status = $1 ORDER BY id",
                OrderStatus.NEW.value
            )
        return result

    async def get_inactive_orders(self, date_from: datetime | None = None, date_to: datetime | None = None): #inactive -- CANCELLED, DELIVERED, CLOSED
        #Возвращает все неактивные заказы за определенный промежуток.
        #Если промежуток не указан - возвращает только CANCELLED и DELIVERED заказы (заказы за текущую смену)
        async with self.pool.acquire() as connection:
            if date_from is not None and date_to is not None:
                result = await connection.fetch("""
                    SELECT * FROM orders WHERE created_at BETWEEN $1 AND $2
                    AND status IN ($3, $4, $5)""",
                    date_from, date_to, OrderStatus.CANCELLED, OrderStatus.DELIVERED, OrderStatus.CLOSED
                )
            else:
                result = await connection.fetch(
                    "SELECT * FROM orders WHERE status IN ($1, $2)",
                    OrderStatus.CANCELLED, OrderStatus.DELIVERED
                )
        return result

    async def get_all_orders_by_date(self, date_from: datetime = None, date_to: datetime = None):
        #Возвращает все заказы за определенный промежуток
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE created_at BETWEEEN $1 AND $2",
                date_from, date_to
            )
        return result

    async def get_orders_by_status(self, status: OrderStatus):
        #Возвращает заказы по статусу
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE status = $1 ORDER BY id",
                status.value
            )
        return result

    async def get_orders_by_courier_and_status(self, courier_id: int, status: OrderStatus):
        #Возвращает заказы по курьеру и статусу
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE courier_id = $1 AND status = $2",
                courier_id, status
            )
        return result

    async def update_order_status(self, order_id: int, status: OrderStatus, courier_id: int | None = None):
        #Изменяет статус заказа и id курьера, если он указан
        async with self.pool.acquire() as connection:
            if courier_id is not None:
                await connection.execute("""
                UPDATE orders
                SET status = $1,
                    courier_id = $2
                WHERE id = $3
                """,
                status.value, courier_id, order_id
                )
            else:
                await connection.execute("""
                UPDATE orders
                SET status = $1
                WHERE id = $2
                """,
                status.value, order_id
                )

    async def delete_order_by_id(self, order_id: int):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    "DELETE FROM order_items WHERE order_id = $1",
                    order_id
                )
                await connection.execute(
                    "DELETE FROM orders WHERE id = $1",
                    order_id
                )

    async def delete_orders_by_date(self, date_from: datetime | None = None, date_to: datetime = None):
        async with self.pool.acquire() as connection:
            if date_from is not None:
                await connection.execute(
                "DELETE FROM orders WHERE created at BETWEEN $1 AND $2",
                date_from, date_to)
            else:
                await connection.execute(
                "DELETE FROM orders WHERE created_at BETWEEN "
                )



    #order_items-------------------------------------------------------------------------------------------
    async def get_items_by_order_id(self, order_id: int):
        #Возвращает все товары заказа
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM order_items WHERE order_id = $1",
                order_id
            )
        return result



    #couriers----------------------------------------------------------------------------------------------
    async def get_available_couriers(self):
        #Возвращает всех AVAILABLE курьеров
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM couriers WHERE status = $1",
                CourierStatus.AVAILABLE
            )
        return result

    async def get_all_couriers(self):
        #Возвращает всех курьеров
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM couriers"
            )
        return result

    async def update_courier_status(self, courier_id: int, status: CourierStatus):
        #Редактирует статус курьера
        async with self.pool.acquire() as connection:
            await connection.execute("""
            UPDATE couriers
            SET status = $1
            WHERE id = $2
            """, status.value, courier_id
            )