import aiosqlite as sq

async def add_user(telegram_id:int, username:str|None=None):
    """
    Асинхронно добавляет нового пользователя в таблицу users.
    Использует INSERT OR IGNORE, чтобы избежать ошибок, если пользователь уже существует.
    """
    async with sq.connect('shop.db') as db:
        cursor = await db.cursor()
        # Используем INSERT OR IGNORE, чтобы не было ошибки, 
        # если пользователь уже есть в базе
        await cursor.execute(
        "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username)
        )
        await db.commit()
        print(f"Пользователь с telegram_id {telegram_id} добавлен или уже существует.") 

# INSERT OR IGNORE INTO ...: Это ключевая часть SQL-запроса.
# INSERT INTO users ...: Пытается вставить новую запись.
# OR IGNORE: Если во время вставки возникает конфликт 
# (а он возникнет, потому что у нас стоит UNIQUE на поле telegram_id), 
# то эта команда просто проигнорирует ошибку и ничего не будет делать. 
# Это идеальный способ добавить 
# пользователя, не проверяя заранее, есть ли он уже в базе.





