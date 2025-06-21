from aiogram import Router, F
from filters.admin_filter import MyFilter
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter, and_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.orm_query import add_product

admin_router = Router()
admin_router.message.filter(MyFilter())

class AddProduct(StatesGroup):
    name = State()
    discription = State()
    price = State()
    image = State()


@admin_router.message(Command("add_product"))
async def add_product_cmd(message: Message, state: FSMContext):
    await message.answer("Введите название продукта")
    await state.set_state(AddProduct.name)

@admin_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено")

@admin_router.message(AddProduct.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание продукта")
    await state.set_state(AddProduct.discription)


@admin_router.message(AddProduct.discription)
async def process_discription(message: Message, state: FSMContext):
    await state.update_data(discription=message.text)
    await message.answer("Введите цену продукта")
    await state.set_state(AddProduct.price)

@admin_router.message(AddProduct.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            await message.answer("Цена должна быть больше 0")
            return
        await state.update_data(price=price)
        await message.answer("Введите ссылку на изображение продукта")
        await state.set_state(AddProduct.image)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену")

@admin_router.message(AddProduct.image, F.photo)
async def process_image(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data(image=photo)
    data = await state.get_data()
    await add_product(data)
    await message.answer("Продукт успешно добавлен")
    await state.clear()

@admin_router.message(AddProduct.image)
async def process_image_url(message: Message, state: FSMContext):
    if message.text and message.text.startswith("http"):
        await state.update_data(image=message.text)
        data = await state.get_data()
        await add_product(data)
        await message.answer("Продукт успешно добавлен")
        await state.clear()
    else:
        await message.answer("Пожалуйста, введите корректный URL изображения")