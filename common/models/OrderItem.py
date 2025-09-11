from decimal import Decimal


class OrderItem:
    productId: int
    name: str
    price: Decimal
    quantity: int
    order_id: int
