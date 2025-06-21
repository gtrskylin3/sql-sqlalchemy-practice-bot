# Магазин Telegram Bot - SQLAlchemy версия

Это версия бота магазина, переписанная с чистого SQL на SQLAlchemy ORM.

## Основные различия с SQL версией

### 1. Подключение к базе данных

**SQL версия:**
```python
import aiosqlite as sq

async with sq.connect('shop.db') as db:
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM products")
```

**SQLAlchemy версия:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import async_session

async with async_session() as session:
    stmt = select(Product)
    result = await session.execute(stmt)
```

### 2. Модели данных

**SQL версия:** Ручное создание таблиц через SQL
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
```

**SQLAlchemy версия:** Python классы
```python
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
```

### 3. Работа с данными

**SQL версия:** Работа с кортежами
```python
products = await cursor.fetchall()
for product in products:
    product_id, name, price, description, image, _ = product
    print(f"{name}: {price}")
```

**SQLAlchemy версия:** Работа с объектами
```python
products = await get_products(session)
for product in products:
    print(f"{product.name}: {product.price}")
```

### 4. Middleware

**SQL версия:** Нет middleware, прямое подключение в каждой функции

**SQLAlchemy версия:** Middleware для передачи сессий
```python
class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with async_session() as session:
            data['session'] = session
            return await handler(event, data)
```

### 5. Обработчики

**SQL версия:**
```python
async def start_command(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
```

**SQLAlchemy версия:**
```python
async def start_command(message: Message, session: AsyncSession):
    await add_user(session, message.from_user.id, message.from_user.username)
```

## Преимущества SQLAlchemy

1. **Типобезопасность** - работа с объектами вместо кортежей
2. **Автоматические связи** - relationship между таблицами
3. **Миграции** - возможность изменять структуру БД
4. **Защита от SQL-инъекций** - автоматическое экранирование
5. **Кроссплатформенность** - легко переключиться на другую БД

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` с токеном бота и ID админа:
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
```

3. Запустите бота:
```bash
python bot.py
```

## Команды бота

- `/start` - начало работы с ботом
- `/shop` - показать все товары
- `/cart` - показать корзину
- `/add_product` - добавить товар (только для админа)