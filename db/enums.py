from enum import Enum

class OrderStatus(str, Enum):
    NEW = 'NEW'
    REJECTED = 'REJECTED'
    ASSIGNED = 'ASSIGNED'
    CANCELLED = 'CANCELLED'
    DELIVERED = 'DELIVERED'
    CLOSED = 'CLOSED'

class CourierStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    ON_DELIVERY = "ON_DELIVERY"
    UNAVAILABLE = "UNAVAILABLE"
