from aiogram.filters import BaseFilter
from aiogram.types import Message

from create_bot import admins


class IsAdminFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in admins:
            return True
        await message.answer("❌ Недостаточно прав: Courier only.")
        return False