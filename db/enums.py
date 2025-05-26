from enum import Enum

class OrderStatus(str, Enum):
    NEW = 'NEW'
    REJECTED = 'REJECTED'
    ASSIGNED = 'ASSIGNED'
    CANCELLED = 'CANCELLED'
    IN_DELIVERY = 'IN_DELIVERY'
    DELIVERED = 'DELIVERED'
    CLOSED = 'CLOSED'

class CourierStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DELIVERING = "DELIVERING"
    UNAVAILABLE = "UNAVAILABLE"
