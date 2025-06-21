import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Импортируем все из новой структуры проекта
from database.engine import create_db
from handlers.admin_router import admin_router
from handlers.user_router import user_router
from middlewares.dp import DatabaseMiddleware
from menu_comands import set_menu

# Загружаем переменные окружения из файла .env в текущей папке
load_dotenv()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен и проверяем его наличие
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    print("Ошибка: Токен бота не найден. Убедитесь, что вы создали .env файл в папке sqalchemy_version.")
    exit()

# Инициализируем бота и диспетчер
bot = Bot(token=bot_token)
dp = Dispatcher()

# Подключаем middleware для работы с базой данных
dp.message.middleware(DatabaseMiddleware())
dp.callback_query.middleware(DatabaseMiddleware())

# Подключаем роутеры
dp.include_router(admin_router)
dp.include_router(user_router)


async def main():
    """Основная функция для запуска бота."""
    print("Бот запускается (SQLAlchemy версия)...")
    
    # Вызываем функцию для создания таблиц через SQLAlchemy
    await create_db()
    await bot.set_my_commands(set_menu())
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
