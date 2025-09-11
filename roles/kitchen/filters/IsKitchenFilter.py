from aiogram.filters import BaseFilter
from aiogram.types import Message

from create_bot import kitchen


class IsKitchenFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in kitchen:
            return True
        return False