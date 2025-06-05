from aiogram.filters import BaseFilter
from aiogram.types import Message

from create_bot import managers


class IsManagerFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in managers:
            return True
        await message.answer("❌ Недостаточно прав: Manager only.")
        return False