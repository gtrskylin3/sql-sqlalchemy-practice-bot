import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from database.database import create_tables
from handlers.admin_router import admin_router
from handlers.user_router import user_router

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настраиваем логирование для получения информации о работе бота
logging.basicConfig(level=logging.INFO)

# Получаем токен бота из переменных окружения
bot_token = os.getenv("BOT_TOKEN")

# Инициализируем бота и диспетчер
bot = Bot(token=bot_token)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(admin_router)
dp.include_router(user_router)


async def main():
    """
    Основная функция для запуска бота.
    """
    print("Бот запускается...")
    # Убеждаемся, что таблицы в базе данных созданы перед запуском бота
    await create_tables()
    print("База данных готова.")

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
