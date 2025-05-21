from tracemalloc import BaseFilter

from aiogram.types import Message

from create_bot import admins


class IsCourierFilter(BaseFilter):

    async def __call__(self, message: Message):
        if message.from_user.id in admins:
            return True
        await message.answer("❌ Недостаточно прав: Courier only.")