# import sqlite3

# # Подключаемся к базе данных (если файла нет — он создастся)
# conn = sqlite3.connect('database.db')

# # Создаём объект-курсор для выполнения SQL-запросов
# cursor = conn.cursor()

# cursor.execute(
#     """
#     CREATE TABLE IF NOT EXISTS products (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         price REAL NOT NULL,
#         description TEXT,
#         image TEXT
#     )
#     """
# )

# conn.commit()
# conn.close()

import aiosqlite as sq

async def create_tables():
    """
    Асинхронно создает таблицы в базе данных shop.db, если они еще не существуют.
    - users: для хранения информации о пользователях
    - products: для хранения информации о товарах
    - cart: для хранения содержимого корзин пользователей (связывает users и products)
    """
    async with sq.connect('shop.db') as db:
          # Устанавливаем TEXT_FACTORY на str для корректной работы с текстом
        db.text_factory = str
        cursor = await db.cursor()
        
        # Включаем поддержку внешних ключей для базы данных
        await cursor.execute("PRAGMA foreign_keys = ON")

        # Создаём таблицу users
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Таблица 'users' создана или уже существует.")

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Таблица 'products' создана или уже существует.")

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER MOT NULL DEFOULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        """)
        print("Таблица 'cart' создана или уже существует.")

        await db.commit()

        # users: с уникальным telegram_id.
        # products: для товаров.
        # cart: связующая таблица с FOREIGN KEY (внешними ключами) 
        # на users.id и products.id. ON DELETE CASCADE означает, 
        # что если пользователь или товар будет удален, 
        # все связанные с ним записи в корзине также удалятся автоматически.

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())


