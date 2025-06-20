from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from filters.admin_filter import IsAdmin
from database.orm_query import add_product

admin_router = Router()
admin_router.message.filter(IsAdmin())


class AddProduct(StatesGroup):
    # Шаги для добавления товара
    name = State()
    description = State()
    price = State()
    image = State()


# Команда для начала добавления товара
@admin_router.message(Command("add_product"))
async def add_product_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название товара. Для отмены введите 'отмена'.")
    await state.set_state(AddProduct.name)


# Обработчик отмены
@admin_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.")


# Шаг 1: Получаем название
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Теперь введите описание товара.")
    await state.set_state(AddProduct.description)


# Шаг 2: Получаем описание
@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Теперь введите цену товара (только цифры).")
    await state.set_state(AddProduct.price)


# Шаг 3: Получаем цену
@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    try:
        # Проверяем, что цена - это число
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Отлично. Теперь отправьте фото товара.")
        await state.set_state(AddProduct.image)
    except ValueError:
        await message.answer("Цена должна быть числом. Попробуйте еще раз.")


# Шаг 4: Получаем фото и сохраняем товар
@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext):
    # Получаем ID файла фото самого лучшего качества
    image_id = message.photo[-1].file_id
    await state.update_data(image=image_id)

    # Получаем все данные из FSM
    data = await state.get_data()

    # Добавляем товар в базу данных
    await add_product(data)

    # Отправляем подтверждение
    await message.answer("Товар успешно добавлен!")

    # Очищаем состояние
    await state.clear()

@admin_router.message(AddProduct.image)
async def process_image_url(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith('http'):
        await state.update_data(image=message.text)
        data = await state.get_data()
        await add_product(data)
        await message.answer("Товар успешно добавлен (используя URL)!")
        await state.clear()
    else:
        await message.answer("Пожалуйста, отправьте фото или URL, начинающийся с http.")
