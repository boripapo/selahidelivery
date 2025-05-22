from tracemalloc import BaseFilter

from aiogram.types import Message

from create_bot import couriers


class IsCourierFilter(BaseFilter):

    async def __call__(self, message: Message):
        if message.from_user.id in couriers:
            return True
        await message.answer("❌ Недостаточно прав: Courier only.")