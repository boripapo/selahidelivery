from datetime import datetime
import logging
from typing import Optional

from decouple import config

import asyncpg

from common.db.enums import OrderStatus, CourierStatus
from common.models.OrderItem import OrderItem

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
        #Если промежуток не указан - возвращает только неактивные заказы за текущую смену
        async with self.pool.acquire() as connection:
            if date_from is not None and date_to is not None:
                result = await connection.fetch("""
                    SELECT * FROM orders WHERE created_at BETWEEN $1 AND $2
                    AND status IN ($3, $4, $5)""",
                    date_to, date_from, OrderStatus.CANCELLED, OrderStatus.DELIVERED, OrderStatus.CLOSED
                )
            else:
                result = await connection.fetch(
                    "SELECT * FROM orders WHERE status IN ($1, $2, $3)",
                    OrderStatus.CANCELLED, OrderStatus.DELIVERED, OrderStatus.CLOSED
                )
        return result

    async def get_orders_by_date(self, date: datetime):
        #Возвращает все заказы за определенный промежуток
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE created_at::date = $1",
                date
            )
        return result

    async def get_orders_by_courier(self, courier_id: int):
        #Возвращает заказы по айди курьера
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM orders WHERE courier_id = $1",
                courier_id
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
        #Возвращает заказы по айди курьера и статусу
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

    async def update_order_name(self, order_id: int, name: str):
        async with self.pool.acquire() as connection:
            connection.execute("""
            UPDATE orders
            SET name = $1 
            WHERE id = $2
            """,
            name, order_id
            )

    async def update_order_address(self, order_id: int, address: str):
        async with self.pool.acquire() as connection:
            connection.execute("""
            UPDATE orders
            SET address = $1
            WHERE id = $2
            """,
            address, order_id
            )

    async def set_orders_closed(self, open_shift: datetime, close_shift: datetime):
        # Присваивает всем заказам в текущей смене статус CLOSED
        async with self.pool.acquire() as connection:
            connection.execute("""
            UPDATE orders
            SET status = $1
            WHERE created_at BETWEEN $2 AND $3
            """,
            OrderStatus.CLOSED, open_shift, close_shift
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

    async def delete_orders_by_date(self, date: datetime):
        async with self.pool.acquire() as connection:
            await connection.execute(
            "DELETE FROM orders WHERE created_at::date = $1",
            date
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

    async def get_items_by_multiple_order_id(self, order_id: list[int]):
        async with self.pool.acquire() as connection:
            result = await connection.fetchmany(
                "SELECT price FROM order_items WHERE order_id = $1",
                order_id
            )
        return result

    async def get_items_by_date(self, date: datetime):
        async with self.pool.acquire() as connection:
            result = await connection.fetch("""
            SELECT
                i.id,
                i.order_id,
                i.product_id,
                i.name,
                i.price,
                i.quantity,
                o.created_at
            FROM order_items i
            JOIN orders o
            ON o.id = i.order_id
            WHERE o.created_at::date = $1
            """, date
            )
        return result

    async def update_items_by_order_id(self, order_id: int, items: list[OrderItem]):
        #Обновляет записи в order_items
        async with self.pool.acquire() as connection:
            await connection.executemany("""
                    INSERT INTO order_items (product_id, name, price, quantity, order_id)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (order_id, product_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        quantity = EXCLUDED.quantity
                """, items)


    #couriers----------------------------------------------------------------------------------------------
    async def get_courier_by_id(self, courier_id: int):
        async with self.pool.acquire() as connection:
            result = await connection.fetch(
                "SELECT * FROM couriers WHERE id = $1",
                courier_id
            )
        return result

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



    #Полная очистка БД--------------------------------------------------------------------------------------------------
    async def full_orders_and_order_items_clean(self):
        async with self.pool.acquire() as connection:
            await connection.execute(
                "DELETE FROM orders"
            )
            await connection.execute(
                "DELETE FROM order_items"
            )



    async def fill_db_with_test_data(self):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO orders(id, name, phone, address, payment_method, created_at, status)
VALUES
(30, 'Павел', '+375123123123', 'ул. Московская, 267', 'CASH', '2025-06-12 09:24:00', 'CLOSED'),
(29, 'Павел', '+375123123123', 'ул. Московская, 267', 'CASH', '2025-06-12 13:30:00', 'CLOSED'),
(28, 'Павел', '+375123123123', 'ул. Московская, 267', 'CASH', '2025-06-12 15:30:00', 'CLOSED'),
(27, 'Андрей', '+375111111111', 'ул. Московская, 267', 'CARD', '2025-06-11 09:24:00', 'CLOSED'),
(26, 'Андрей', '+375111111111', 'ул. Московская, 267', 'CARD', '2025-06-11 13:30:00', 'CLOSED'),
(25, 'Андрей', '+375111111111', 'ул. Московская, 267', 'CARD', '2025-06-11 15:30:00', 'CLOSED'),
(24, 'Василий', '+375123456789', 'ул. Московская, 267', 'CASH', '2025-06-10 09:24:00', 'CLOSED'),
(23, 'Василий', '+375123456789', 'ул. Московская, 267', 'CASH', '2025-06-10 13:30:00', 'CLOSED'),
(22, 'Василий', '+375123456789', 'ул. Московская, 267', 'CASH', '2025-06-10 15:30:00', 'CLOSED'),
(21, 'Николай', '+375987654321', 'ул. Московская, 267', 'CARD', '2025-06-09 09:24:00', 'CLOSED'),
(20, 'Николай', '+375987654321', 'ул. Московская, 267', 'CARD', '2025-06-09 13:30:00', 'CLOSED'),
(19, 'Николай', '+375987654321', 'ул. Московская, 267', 'CARD', '2025-06-09 15:30:00', 'CLOSED'),
(18, 'Павел', '+375123123123', 'ул. Московская, 267', 'CASH', '2025-06-08 09:24:00', 'CLOSED'),
(17, 'Павел', '+375123123123', 'ул. Московская, 267', 'CASH', '2025-06-08 13:30:00', 'CLOSED'),
(16, 'Павел', '+375123123123', 'ул. Московская, 267', 'CASH', '2025-06-08 15:30:00', 'CLOSED'),
(15, 'Андрей', '+375111111111', 'ул. Московская, 267', 'CARD', '2025-06-07 09:24:00', 'CLOSED'),
(14, 'Андрей', '+375111111111', 'ул. Московская, 267', 'CARD', '2025-06-07 13:30:00', 'CLOSED'),
(13, 'Андрей', '+375111111111', 'ул. Московская, 267', 'CARD', '2025-06-07 15:30:00', 'CLOSED'),
(12, 'Василий', '+375123456789', 'ул. Московская, 267', 'CASH', '2025-06-06 09:24:00', 'CLOSED'),
(11, 'Василий', '+375123456789', 'ул. Московская, 267', 'CASH', '2025-06-06 13:30:00', 'CLOSED'),
(10, 'Василий', '+375123456789', 'ул. Московская, 267', 'CASH', '2025-06-06 15:30:00', 'CLOSED'),
(9, 'Николай', '+375987654321', 'ул. Московская, 267', 'CARD', '2025-06-05 09:24:00', 'CLOSED'),
(8, 'Николай', '+375987654321', 'ул. Московская, 267', 'CARD', '2025-06-05 13:30:00', 'CLOSED'),
(7, 'Николай', '+375987654321', 'ул. Московская, 267', 'CARD', '2025-06-05 15:30:00', 'CLOSED'),
(6, 'Геннадий', '+375777777777', 'ул. Московская, 267', 'CASH', '2025-06-04 09:24:00', 'CLOSED'),
(5, 'Геннадий', '+375777777777', 'ул. Московская, 267', 'CASH', '2025-06-04 13:30:00', 'CLOSED'),
(4, 'Геннадий', '+375777777777', 'ул. Московская, 267', 'CASH', '2025-06-04 15:30:00', 'CLOSED'),
(3, 'Дмитрий', '+375000000000', 'ул. Московская, 267', 'CARD', '2025-06-03 09:24:00', 'CLOSED'),
(2, 'Дмитрий', '+375000000000', 'ул. Московская, 267', 'CARD', '2025-06-03 13:30:00', 'CLOSED'),
(1, 'Дмитрий', '+375000000000', 'ул. Московская, 267', 'CARD', '2025-06-03 15:30:00', 'CLOSED')
                """
            )
            await connection.execute(
                """
                INSERT INTO order_items(id, product_id, name, price, quantity, order_id)
VALUES
(1, 1, 'Классик Бургер', 12.50, 3, 1),
(2, 6, 'Кола 0.5л', 3.00, 3, 1),
(3, 2, 'Чизбургер', 14.00, 3, 2),
(4, 4, 'Картошка фри', 5.00, 3, 2),
(5, 6, 'Кола 0.5л', 3.00, 3, 2),
(6, 3, 'Бекон Бургер', 15.50, 1, 3),
(7, 7, 'Сок апельсиновый', 3.50, 1, 3),
(8, 1, 'Классик Бургер', 12.50, 1, 4),
(9, 3, 'Бекон Бургер', 15.50, 1, 4),
(10, 5, 'Сырные палочки', 6.50, 2, 4),
(11, 6, 'Кола 0.5л', 3.00, 2, 4),
(12, 1, 'Классик Бургер', 12.50, 3, 5),
(13, 6, 'Кола 0.5л', 3.00, 3, 5),
(14, 2, 'Чизбургер', 14.00, 3, 6),
(15, 4, 'Картошка фри', 5.00, 3, 6),
(16, 6, 'Кола 0.5л', 3.00, 3, 6),
(17, 3, 'Бекон Бургер', 15.50, 1, 7),
(18, 7, 'Сок апельсиновый', 3.50, 1, 7),
(19, 1, 'Классик Бургер', 12.50, 1, 8),
(20, 3, 'Бекон Бургер', 15.50, 1, 8),
(21, 5, 'Сырные палочки', 6.50, 2, 8),
(22, 6, 'Кола 0.5л', 3.00, 2, 8),
(23, 1, 'Классик Бургер', 12.50, 3, 9),
(24, 6, 'Кола 0.5л', 3.00, 3, 9),
(25, 2, 'Чизбургер', 14.00, 3, 10),
(26, 4, 'Картошка фри', 5.00, 3, 10),
(27, 6, 'Кола 0.5л', 3.00, 3, 10),
(28, 3, 'Бекон Бургер', 15.50, 1, 11),
(29, 7, 'Сок апельсиновый', 3.50, 1, 11),
(30, 1, 'Классик Бургер', 12.50, 1, 12),
(31, 3, 'Бекон Бургер', 15.50, 1, 12),
(32, 5, 'Сырные палочки', 6.50, 2, 12),
(33, 6, 'Кола 0.5л', 3.00, 2, 12),
(34, 1, 'Классик Бургер', 12.50, 3, 13),
(35, 6, 'Кола 0.5л', 3.00, 3, 13),
(36, 2, 'Чизбургер', 14.00, 3, 14),
(37, 4, 'Картошка фри', 5.00, 3, 14),
(38, 6, 'Кола 0.5л', 3.00, 3, 14),
(39, 3, 'Бекон Бургер', 15.50, 1, 15),
(40, 7, 'Сок апельсиновый', 3.50, 1, 15),
(41, 1, 'Классик Бургер', 12.50, 1, 16),
(42, 3, 'Бекон Бургер', 15.50, 1, 16),
(43, 5, 'Сырные палочки', 6.50, 2, 16),
(44, 6, 'Кола 0.5л', 3.00, 2, 16),
(45, 1, 'Классик Бургер', 12.50, 3, 17),
(46, 6, 'Кола 0.5л', 3.00, 3, 17),
(47, 2, 'Чизбургер', 14.00, 3, 18),
(48, 4, 'Картошка фри', 5.00, 3, 18),
(49, 6, 'Кола 0.5л', 3.00, 3, 18),
(50, 3, 'Бекон Бургер', 15.50, 1, 19),
(51, 7, 'Сок апельсиновый', 3.50, 1, 19),
(52, 1, 'Классик Бургер', 12.50, 1, 20),
(53, 3, 'Бекон Бургер', 15.50, 1, 20),
(54, 5, 'Сырные палочки', 6.50, 2, 20),
(55, 6, 'Кола 0.5л', 3.00, 2, 20),
(56, 1, 'Классик Бургер', 12.50, 3, 21),
(57, 6, 'Кола 0.5л', 3.00, 3, 21),
(58, 2, 'Чизбургер', 14.00, 3, 22),
(59, 4, 'Картошка фри', 5.00, 3, 22),
(60, 6, 'Кола 0.5л', 3.00, 3, 22),
(61, 3, 'Бекон Бургер', 15.50, 1, 23),
(62, 7, 'Сок апельсиновый', 3.50, 1, 23),
(63, 1, 'Классик Бургер', 12.50, 1, 24),
(64, 3, 'Бекон Бургер', 15.50, 1, 24),
(65, 5, 'Сырные палочки', 6.50, 2, 24),
(66, 6, 'Кола 0.5л', 3.00, 2, 24),
(67, 1, 'Классик Бургер', 12.50, 3, 25),
(68, 6, 'Кола 0.5л', 3.00, 3, 25),
(69, 2, 'Чизбургер', 14.00, 3, 26),
(70, 4, 'Картошка фри', 5.00, 3, 26),
(71, 6, 'Кола 0.5л', 3.00, 3, 26),
(72, 3, 'Бекон Бургер', 15.50, 1, 27),
(73, 7, 'Сок апельсиновый', 3.50, 1, 27),
(74, 1, 'Классик Бургер', 12.50, 1, 28),
(75, 3, 'Бекон Бургер', 15.50, 1, 28),
(76, 5, 'Сырные палочки', 6.50, 2, 28),
(77, 6, 'Кола 0.5л', 3.00, 2, 28),
(78, 1, 'Классик Бургер', 12.50, 3, 29),
(79, 6, 'Кола 0.5л', 3.00, 3, 29),
(80, 2, 'Чизбургер', 14.00, 3, 30),
(81, 4, 'Картошка фри', 5.00, 3, 30),
(82, 6, 'Кола 0.5л', 3.00, 3, 30)
                """
            )