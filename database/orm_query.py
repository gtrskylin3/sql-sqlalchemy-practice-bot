import aiosqlite as sq

async def add_user(telegram_id: int, username: str | None = None):
    """
    Асинхронно добавляет нового пользователя в таблицу users.
    Использует INSERT OR IGNORE, чтобы избежать ошибок, если пользователь уже существует.
    """
    async with sq.connect('shop.db') as db:
        cursor = await db.cursor()
        # Используем INSERT OR IGNORE, чтобы не было ошибки, если пользователь уже есть в базе
        await cursor.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username)
        )
        await db.commit()
        print(f"Пользователь с telegram_id {telegram_id} добавлен или уже существует.")

async def add_product(data: dict):
    """
    Асинхронно добавляет новый товар в таблицу products.
    """
    async with sq.connect('shop.db') as db:
        cursor = await db.cursor()
        await cursor.execute(
            "INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)",
            (data['name'], data['description'], data['price'], data['image'])
        )
        await db.commit()
        print(f"Товар '{data['name']}' добавлен в базу данных.")

async def get_products():
    """
    Асинхронно получает все товары из таблицы products.
    """
    async with sq.connect('shop.db') as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM products")
        return await cursor.fetchall()

async def add_to_cart(user_id: int, product_id: int):
    """
    Асинхронно добавляет товар в корзину пользователя.
    Если товар уже есть, увеличивает его количество.
    """
    async with sq.connect('shop.db') as db:
        cursor = await db.cursor()

        # Сначала получаем id пользователя из таблицы users по его telegram_id
        await cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
        user_db_id_row = await cursor.fetchone()
        if not user_db_id_row:
            print(f"Пользователь с telegram_id {user_id} не найден в базе.")
            return

        user_db_id = user_db_id_row[0]

        # Проверяем, есть ли уже такой товар в корзине у этого пользователя
        await cursor.execute(
            "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?",
            (user_db_id, product_id)
        )
        result = await cursor.fetchone()

        if result:
            # Если товар есть, увеличиваем количество
            new_quantity = result[0] + 1
            await cursor.execute(
                "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                (new_quantity, user_db_id, product_id)
            )
            print(f"Количество товара {product_id} для пользователя {user_db_id} обновлено до {new_quantity}.")
        else:
            # Если товара нет, добавляем новую запись
            await cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)",
                (user_db_id, product_id)
            )
            print(f"Товар {product_id} добавлен в корзину для пользователя {user_db_id}.")

        await db.commit() 