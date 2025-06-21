import asyncio
from database.engine import create_db, async_session
from database.models import User, Product, Cart
from database.orm_query import add_user, add_product, get_products, add_to_cart, get_user_cart


async def test_sqlalchemy():
    """
    Тестируем основные функции SQLAlchemy версии.
    """
    print("🧪 Тестирование SQLAlchemy версии...")
    
    # Создаем таблицы
    await create_db()
    print("✅ Таблицы созданы")
    
    # Тестируем работу с пользователями
    async with async_session() as session:
        # Добавляем пользователя
        user = await add_user(session, 123456789, "test_user")
        print(f"✅ Пользователь добавлен: {user}")
        
        # Добавляем товар
        product_data = {
            'name': 'Тестовый товар',
            'description': 'Описание тестового товара',
            'price': 100.0,
            'image': 'https://example.com/image.jpg'
        }
        product = await add_product(session, product_data)
        print(f"✅ Товар добавлен: {product}")
        
        # Получаем все товары
        products = await get_products(session)
        print(f"✅ Получено товаров: {len(products)}")
        for p in products:
            print(f"   - {p.name}: {p.price} руб.")
        
        # Добавляем товар в корзину
        success = await add_to_cart(session, 123456789, product.id)
        print(f"✅ Товар добавлен в корзину: {success}")
        
        # Получаем корзину пользователя
        cart_items = await get_user_cart(session, 123456789)
        print(f"✅ Товаров в корзине: {len(cart_items)}")
        for item in cart_items:
            print(f"   - {item.product.name}: {item.quantity} шт.")
    
    print("🎉 Все тесты пройдены успешно!")


if __name__ == "__main__":
    asyncio.run(test_sqlalchemy()) 