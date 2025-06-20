import os
from aiogram.filters import Filter
from aiogram.types import Message


class IsAdmin(Filter):
    """
    Это фильтр, который проверяет, является ли пользователь,
    отправивший сообщение, администратором бота.
    ID администратора берется из переменных окружения.
    """
    def __init__(self) -> None:
        # Получаем ID админа из переменных окружения .env
        # Важно: ADMIN_ID должен быть строкой, как и message.from_user.id
        self.admin_id = os.getenv("ADMIN_ID")

    async def __call__(self, message: Message) -> bool:
        # Сравниваем ID пользователя с ID админа
        return str(message.from_user.id) == self.admin_id 