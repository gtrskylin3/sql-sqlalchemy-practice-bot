from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware для передачи асинхронной сессии SQLAlchemy в обработчики.
    
    Этот middleware автоматически создает сессию для каждого запроса
    и передает ее в обработчик через data['session'].
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обрабатывает каждый запрос, создавая сессию базы данных.
        """
        # Создаем асинхронную сессию
        async with async_session() as session:
            # Добавляем сессию в data, чтобы она была доступна в обработчиках
            data['session'] = session
            
            # Вызываем следующий обработчик в цепочке
            return await handler(event, data)

