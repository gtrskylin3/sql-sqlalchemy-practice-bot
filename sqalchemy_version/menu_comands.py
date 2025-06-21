from aiogram.types import BotCommand

def set_menu():
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="shop", description="Посмотреть товары"),
        BotCommand(command="cart", description="Посмотреть корзину"),
        BotCommand(command="admin", description="Админ-панель"),
    ]
    return commands



