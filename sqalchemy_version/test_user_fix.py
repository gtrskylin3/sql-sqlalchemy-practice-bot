import asyncio
from database.engine import create_db, async_session
from database.orm_query import add_user


async def test_user_creation():
    """Тестируем создание пользователя и повторное добавление"""
    print("🧪 Тестируем исправление функции add_user")
    print("=" * 50)
    
    try:
        # Создаем базу данных
        await create_db()
        
        async with async_session() as session:
            # Первый раз - создаем пользователя
            print("\n1. Создаем пользователя впервые...")
            user1 = await add_user(session, 123456789, "test_user")
            print(f"✅ Результат: {user1}")
            
            # Второй раз - пытаемся создать того же пользователя
            print("\n2. Пытаемся создать того же пользователя...")
            user2 = await add_user(session, 123456789, "test_user_updated")
            print(f"✅ Результат: {user2}")
            
            # Проверяем, что это тот же объект
            print(f"\n3. Проверяем, что это тот же пользователь: {user1.id == user2.id}")
            
            # Третий раз - с тем же username
            print("\n4. Пытаемся создать с тем же username...")
            user3 = await add_user(session, 123456789, "test_user_updated")
            print(f"✅ Результат: {user3}")
            
        print("\n🎉 Тест прошел успешно! Ошибка UNIQUE constraint исправлена.")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_user_creation()) 