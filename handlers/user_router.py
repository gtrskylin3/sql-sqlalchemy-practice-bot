from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.orm_query import get_products, add_to_cart, add_user

user_router = Router()


# Переносим обработчик /start сюда
@user_router.message(CommandStart())
async def handle_start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет, {message.from_user.full_name}! Добро пожаловать в наш магазин.\n"
        "Чтобы посмотреть товары, введите команду /shop"
    )


@user_router.message(Command("shop"))
async def show_shop(message: types.Message):
    """
    Показывает все товары из базы данных в виде карточек.
    """
    products = await get_products()
    if not products:
        await message.answer("Извините, товаров пока нет.")
        return

    for product in products:
        # Распаковываем данные о товаре
        product_id, name, price, description, image, _ = product

        # Создаем инлайн-кнопку
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{product_id}")]
        ])

        # Формируем подпись к фото
        caption = f"<b>{name}</b>\n\n{description}\n\n<b>Цена:</b> {price} руб."

        # Отправляем фото с подписью и кнопкой
        await message.answer_photo(
            photo=image,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@user_router.callback_query(F.data.startswith("add_to_cart_"))
async def handle_add_to_cart(callback: types.CallbackQuery):
    """
    Обрабатывает нажатие на кнопку "Добавить в корзину".
    """
    # Получаем ID товара из callback_data
    product_id = int(callback.data.split("_")[-1])

    # Получаем ID пользователя
    user_telegram_id = callback.from_user.id

    # Добавляем товар в корзину
    await add_to_cart(user_telegram_id, product_id)

    # Отвечаем на callback, чтобы убрать "часики" с кнопки
    await callback.answer("Товар добавлен в корзину!")
