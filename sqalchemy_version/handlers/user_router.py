from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import add_user, get_products, add_to_cart, get_user_cart, remove_from_cart, get_product

user_router = Router()


@user_router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession):
    """
    Обработчик команды /start.
    Добавляет пользователя в базу данных, если он еще не существует.
    
    Обратите внимание: теперь функция принимает session как параметр!
    Это возможно благодаря middleware.
    """
    await add_user(session, message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет, {message.from_user.full_name}! Добро пожаловать в наш магазин.\n"
        "Чтобы посмотреть товары, введите команду /shop\n"
        "Чтобы посмотреть корзину, введите команду /cart"
    )


@user_router.message(Command("shop"))
async def show_shop(message: Message, session: AsyncSession):
    """
    Показывает все товары из базы данных в виде карточек.
    """
    products = await get_products(session)
    if not products:
        await message.answer("Извините, товаров пока нет.")
        return
    
    for product in products:
        # Теперь product - это объект SQLAlchemy, а не кортеж!
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{product.id}")]
            ]
        )
        caption = f"<b>{product.name}</b>\n\n{product.description}\n\n<b>Цена:</b> {product.price} руб."
        await message.answer_photo(
            photo=product.image,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@user_router.callback_query(F.data.startswith("add_to_cart_"))
async def handle_add_to_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Обрабатывает нажатие на кнопку "Добавить в корзину".
    """
    # Получаем ID товара из callback_data
    product_id = int(callback.data.split("_")[-1])
    # Получаем ID пользователя из callback
    user_telegram_id = callback.from_user.id
    
    # Добавляем товар в корзину
    success = await add_to_cart(session, user_telegram_id, product_id)
    
    if success:
        await callback.answer("Товар добавлен в корзину!")
    else:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)


@user_router.message(Command("cart"))
async def show_cart(message: Message, session: AsyncSession):
    """
    Показывает содержимое корзины пользователя.
    """
    cart_items = await get_user_cart(session, message.from_user.id)
    
    if not cart_items:
        await message.answer("Ваша корзина пуста.")
        return
    
    # Формируем сообщение с товарами в корзине
    cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
    total_price = 0
    
    for item in cart_items:
        # item.product - это связанный объект Product благодаря relationship
        product = item.product

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Удалить из корзины", callback_data=f"remove_from_cart_{product.id}")]
            ]
        )



        item_total = product.price * item.quantity
        total_price += item_total
        
        text = f"<b>{product.name}</b>\n\n<b>Цена:</b> {product.price} руб.\n<b>Количество:</b> {item.quantity} шт. \n\n<b>Итого:</b> {item_total} руб."
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    
    await message.answer(f"💰 <b>Общая сумма: {total_price} руб.</b>", parse_mode="HTML") 

@user_router.callback_query(F.data.startswith("remove_from_cart_"))
async def handle_remove_from_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Обрабатывает нажатие на кнопку "Удалить из корзины".
    """
    product_id = int(callback.data.split("_")[-1])
    user_telegram_id = callback.from_user.id
    
    success = await remove_from_cart(session, user_telegram_id, product_id)
    product = await get_product(session, product_id)

    if success:
        await callback.answer(f"Товар {product.name} удален из корзины!")
    else:
        await callback.answer("Ошибка: пользователь не найден", show_alert=True)
