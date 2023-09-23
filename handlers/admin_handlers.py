from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON, ADMIN_PANEL, LEXICON_ADMIN, product_ikb, product_params
from config_data.config import load_config
from aiogram.filters import BaseFilter
from database.database import Products, db
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram import F
from keyboard.keyboard import kb_generator, ikb_generator
from dataclasses import dataclass

router: Router = Router()

admin_ids = load_config().tg_bot.admin_ids

product = Products(db)


@dataclass
class Info:
    id:str=None


a = Info()
class FSMFillProduct(StatesGroup):
    fill_product_name = State()
    fill_category = State()
    fill_price = State()
    fill_quantity = State()
    fill_description = State()
    fill_photo = State()
    fill_edit_product_name = State()
    fill_edit_category = State()
    fill_edit_price = State()
    fill_edit_quantity = State()
    fill_edit_description = State()
    fill_edit_photo = State()


class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(F.text == ADMIN_PANEL[3], ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ADMIN['cancel_fsm'])
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(F.text == ADMIN_PANEL[3], StateFilter(default_state))
async def process_cancel_command(message: Message):
    pass


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message(Command(commands='admin'), IsAdmin(admin_ids))
async def send_answer(message: Message):
    await message.answer(LEXICON_ADMIN['admin'], reply_markup=kb_generator(ADMIN_PANEL))


@router.message(F.text == ADMIN_PANEL[0], StateFilter(default_state), IsAdmin(admin_ids))
async def process_fill_product(message: Message, state: FSMContext):
    await message.answer(LEXICON_ADMIN['fsm_product'])
    await state.update_data(product=message.text.strip(' '))
    await state.set_state(FSMFillProduct.fill_product_name)


@router.message(StateFilter(
    FSMFillProduct.fill_product_name))  # Этот хэндлер будет срабатывать, если введено корректное название продукта и переводить в состояние ожидания ввода цены продукта
async def process_product_sent(message: Message, state: FSMContext):
    product_name = message.text
    product_name = f'{product_name.capitalize()} '
    await state.update_data(
        product=product_name)
    await message.answer(text=LEXICON_ADMIN['fsm_category'])
    await state.set_state(FSMFillProduct.fill_category)


@router.message(StateFilter(FSMFillProduct.fill_category))  # Вводим категорию
async def process_category_sent(message: Message, state: FSMContext):
    category_name = message.text.strip().capitalize()
    await state.update_data(category=category_name)
    await message.answer(text=LEXICON_ADMIN['fsm_description'])
    await state.set_state(FSMFillProduct.fill_description)


@router.message(StateFilter(FSMFillProduct.fill_description))  # Вводим описание
async def process_product_sent(message: Message, state: FSMContext):
    text = message.text.capitalize()
    await state.update_data(description=text)  # Присваиваем переменную name в переменную нашей машины состояиния
    await message.answer(text=LEXICON_ADMIN['fsm_price'])
    await state.set_state(FSMFillProduct.fill_price)


@router.message(F.text.isdigit(), StateFilter(FSMFillProduct.fill_price))  # Вводим цену
async def process_fill_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)  # Устанавлиеваем значение price
    await message.answer(text=LEXICON_ADMIN['fsm_quantity'])
    await state.set_state(FSMFillProduct.fill_quantity)  # Переводим в состояние ввода количества товара


@router.message(F.text.isdigit(), StateFilter(FSMFillProduct.fill_quantity))  # Вводим кол-во
async def process_fill_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)  # Устанавлиеваем значение price
    await message.answer(LEXICON_ADMIN['fsm_photo'])
    await state.set_state(FSMFillProduct.fill_photo)


@router.message(F.content_type == 'photo', StateFilter(FSMFillProduct.fill_photo))  # Вводим фото
async def process_fill_photo(message: Message, state: FSMContext):
    URI_INFO = f'https://api.telegram.org/bot{load_config().tg_bot.token}/getFile?file_id='
    URI = f'https://api.telegram.org/file/bot{load_config().tg_bot.token}/'
    for photo in message.photo:
        # Обработка каждой фотографии
        file_id = photo.file_id
        # Остальные операции с фотографией

    await state.update_data(photo=file_id)
    data = await state.get_data()
    product.add_product(product=data['product'], category=data['category'], description=data['description'],
                        price=data['price'],
                        quantity=data['quantity'], media=data['photo'])

    await message.answer(text=LEXICON_ADMIN['successfuly_added'])  # Сообщаем об успешной операции
    await state.clear()





@router.message(F.text == ADMIN_PANEL[1], IsAdmin(admin_ids))
async def get_product(message: Message):
    if db.select_data('product'):
        product_data = db.select_data('product')
        product_data = [i for i in product_data[0:]]
        for i in product_data:
            i = [str(a) for a in i]
            await message.answer_photo(photo=i[-1],
                                       caption=f'<b>{i[1]}</b>\nКатегория: {i[2]}\nХарактеристики: {i[3]}\nЦена: {i[4]}\nКол-во на складе: {i[5]}\nid: {i[0]}',
                                       reply_markup=ikb_generator(1, LEXICON['edit'], LEXICON['delete']))
    else:
        await message.answer(LEXICON_ADMIN['database_is_empty'])


@router.message(F.text == ADMIN_PANEL[2], IsAdmin(admin_ids))
async def delete_all_products(message: Message):
    if db.select_data('product'):
        db.delete_data('product', condition='id > 0')
        await message.answer(LEXICON_ADMIN['successfuly_delete'])

    else:

        await message.answer(LEXICON_ADMIN['database_is_empty'])


@router.callback_query(F.data == LEXICON['edit'])
async def  edit (callback:CallbackQuery):
    await callback.message.answer(LEXICON_ADMIN['edit'], reply_markup=ikb_generator(1,product_params[0],product_params[1],product_params[2],product_params[3],))


@router.callback_query(F.data == product_ikb[1])
async def delete_product(callback:CallbackQuery):
    await callback.message.delete()
    a.id = callback.message.caption.split(' ')[-1]
    db.delete_data(table_name='product',condition=f'id = {a.id}')
    await callback.answer(LEXICON_ADMIN['successfuly_delete'])



