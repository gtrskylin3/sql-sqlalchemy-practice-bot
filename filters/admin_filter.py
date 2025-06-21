import os
from aiogram.filters import Filter
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

class MyFilter(Filter):
    """
    Это фильтр, который проверяет, является ли пользователь,
    отправивший сообщение, администратором бота.
    ID администратора берется из переменных окружения.
    """
    def __init__(self) -> None:
        self.admin_id = os.getenv("ADMIN_ID")

    async def __call__(self, message: Message) -> bool:
        return str(message.from_user.id) == self.admin_id