from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from database.orm_query import add_user

user_router = Router()

@user_router.message(CommandStart())
async def start_command(message: Message):
    """
    Обработчик команды /start.
    Добавляет пользователя в базу данных, если он еще не существует.
    """
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Добро пожаловать в наш магазин!")


