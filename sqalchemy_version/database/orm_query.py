from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from .models import User, Product, Cart


async def add_user(session: AsyncSession, telegram_id: int, username: str = None) -> User:
    """
    Добавляет нового пользователя или возвращает существующего.
    Сначала проверяет, существует ли пользователь, затем добавляет или обновляет.
    """
    # Сначала проверяем, существует ли пользователь
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if username and existing_user.username != username:
            existing_user.username = username
            await session.commit()
            print(f"Пользователь с telegram_id {telegram_id} обновлен.")
        else:
            print(f"Пользователь с telegram_id {telegram_id} уже существует.")
        return existing_user
    else:
        new_user = User(telegram_id=telegram_id, username=username)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        print(f"Пользователь с telegram_id {telegram_id} добавлен.")
        return new_user



async def add_product(session: AsyncSession, data: dict) -> Product:
    """
    Добавляет новый товар в базу данных.
    """
    # Создаем объект товара
    product = Product(
        name=data['name'],
        description=data.get('description', ''),  # Используем get() для безопасного получения
        price=data['price'],
        image=data.get('image', '')
    )
    
    # Добавляем в сессию и сохраняем
    session.add(product)
    await session.commit()
    await session.refresh(product)  # Обновляем объект с данными из БД
    
    print(f"Товар {data['name']} добавлен в базу данных")
    return product


async def get_products(session: AsyncSession) -> list[Product]:
    """
    Получает все товары из базы данных.
    """
    # Создаем запрос для получения всех товаров
    stmt = select(Product)
    result = await session.execute(stmt)
    
    # Возвращаем список товаров
    return result.scalars().all()

async def get_product(session: AsyncSession, product_id: int) -> Product:
    """
    Получает товар из базы данных.
    """
    # Создаем запрос для получения всех товаров
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    
    # Возвращаем список товаров
    return product

async def remove_product(session: AsyncSession, product_id: int) -> User:
    """
    Удаляет товар из базы данных.
    """
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    await session.delete(product)
    await session.commit()

async def add_to_cart(session: AsyncSession, user_telegram_id: int, product_id: int) -> bool:
    """
    Добавляет товар в корзину пользователя.
    Если товар уже есть, увеличивает его количество.
    Возвращает True если успешно, False если пользователь не найден.
    """
    # Сначала получаем пользователя по telegram_id
    stmt = select(User).where(User.telegram_id == user_telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        print(f"Пользователь с telegram_id {user_telegram_id} не найден в базе данных")
        return False
    
    # Проверяем, есть ли уже такой товар в корзине
    stmt = select(Cart).where(
        Cart.user_id == user.id,
        Cart.product_id == product_id
    )
    result = await session.execute(stmt)
    cart_item = result.scalar_one_or_none()
    
    if cart_item:
        # Если товар есть, увеличиваем количество
        cart_item.quantity += 1
        print(f"Количество товара {product_id} для пользователя {user.id} обновлено до {cart_item.quantity}.")
    else:
        # Если товара нет, создаем новую запись
        cart_item = Cart(
            user_id=user.id,
            product_id=product_id,
            quantity=1
        )
        session.add(cart_item)
        print(f"Товар {product_id} добавлен в корзину для пользователя {user.id}.")
    
    await session.commit()
    return True


async def get_user_cart(session: AsyncSession, user_telegram_id: int) -> list[Cart]:
    """
    Получает содержимое корзины пользователя с информацией о товарах.
    """
    # Получаем пользователя
    stmt = select(User).where(User.telegram_id == user_telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return []
    
    # Получаем корзину с загруженными товарами
    stmt = select(Cart).options(
        selectinload(Cart.product)  # Загружаем связанный товар
    ).where(Cart.user_id == user.id)
    
    result = await session.execute(stmt)
    return result.scalars().all()


async def remove_from_cart(session: AsyncSession, user_telegram_id: int, product_id: int) -> bool:
    """
    Удаляет товар из корзины пользователя.
    """
    # Получаем пользователя
    stmt = select(User).where(User.telegram_id == user_telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    
    # Удаляем товар из корзины
    stmt = select(Cart).where(
        Cart.user_id == user.id,
        Cart.product_id == product_id
    )
    result = await session.execute(stmt)
    cart_item = result.scalar_one_or_none()
    
    if cart_item and cart_item.quantity > 1:
        cart_item.quantity -= 1
        await session.commit()
        print(f"Количество товара {product_id} для пользователя {user.id} обновлено до {cart_item.quantity}.")
        return True
    elif cart_item and cart_item.quantity == 1:
        await session.delete(cart_item)
        print(f"Товар {product_id} удален из корзины пользователя {user.id}")
        await session.commit()
        return True
    else:
        print(f"Товар {product_id} не найден в корзине пользователя {user.id}")
    return False


