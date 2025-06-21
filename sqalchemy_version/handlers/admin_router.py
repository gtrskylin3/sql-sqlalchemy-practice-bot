from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from filters.admin_filter import IsAdmin
from database.orm_query import add_product, get_products, remove_product, get_product

admin_router = Router()
admin_router.message.filter(IsAdmin())


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()
    # edit_product = False
    # edit_product_id = None

@admin_router.message(Command("admin"))
async def admin_cmd(message: Message):
    await message.answer("Вы вошли в админ-панель вам доступны следующие команды: \n/add_product - добавить продукт \n/remove_product - удалить продукт \n/edit_product - редактировать продукт")

@admin_router.message(Command("add_product"))
async def add_product_cmd(message: Message, state: FSMContext):
    await message.answer("Введите название продукта")
    await state.set_state(AddProduct.name)

@admin_router.message(Command("remove_product"))
async def remove_product_cmd(message: Message, state: FSMContext, session: AsyncSession):
    products = await get_products(session)
    if not products:
        await message.answer("Товаров нет")
        return
    
    for product in products:
        caption = f"<b>{product.name}</b>\n\n<b>Цена:</b> {product.price} руб.\n<b>Описание:</b> {product.description}"
        await message.answer_photo(
            caption=caption,
            photo=product.image,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Удалить", callback_data=f"remove_product_{product.id}")],
                    [InlineKeyboardButton(text="Редактировать", callback_data=f"edit_product_{product.id}")]
                ]
            )
        )
    
@admin_router.callback_query(F.data.startswith("remove_product_"))
async def remove_product_callback(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[-1])
    await remove_product(session, product_id)
    await callback.answer("Продукт успешно удален")

# @admin_router.callback_query(F.data.startswith("edit_product_"))
# async def edit_product_callback(state: FSMContext, callback: CallbackQuery, session: AsyncSession):
#     product_id = int(callback.data.split("_")[-1])
#     await state.set_state(AddProduct.edit_product)
#     await state.update_data(edit_product=True)
#     await state.update_data(edit_product_id=product_id)
#     await callback.message.answer("Введите новое название продукта")
#     await state.set_state(AddProduct.name)


@admin_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено")


@admin_router.message(AddProduct.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание продукта")
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
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
async def process_image(message: Message, state: FSMContext, session: AsyncSession):
    photo = message.photo[-1].file_id
    await state.update_data(image=photo)
    data = await state.get_data()
    
    await add_product(session, data)
    await message.answer("Продукт успешно добавлен")
    await state.clear()


@admin_router.message(AddProduct.image)
async def process_image_url(message: Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text.startswith("http"):
        await state.update_data(image=message.text)
        data = await state.get_data()
        
        await add_product(session, data)
        await message.answer("Продукт успешно добавлен")
        await state.clear()
    else:
        await message.answer("Пожалуйста, введите корректный URL изображения") 