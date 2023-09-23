from aiogram import Router
from aiogram import F
from aiogram.filters import Command, CommandStart,Filter
from aiogram.types import Message
from lexicon.lexicon_ru import LEXICON, FSM_LEXICON, pagination
from database.database import Products, db, user, Cart
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from keyboard.keyboard import kb_generator, ikb_generator
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from dataclasses import dataclass

router: Router = Router()

product = Products(db)
cart = Cart(db)


@dataclass
class Pagination:
    count_pages: int = 0
    quantity: int = 1
    current_page :int =None
    product_data : list =None

class Cats_Filter(Filter):
    def __init__(self, categories:list) -> None:
        self.my_cats = categories

    async def __call__(self, message: Message) -> bool:
        return message.text in self.my_cats


categories = list(set([x[0] for x in product.get_categories()]))

class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_email = State()
    fill_phone = State()


@router.message(CommandStart(), StateFilter(default_state))
async def start(message: Message, state: FSMContext):
    if not user.user_exists(message.from_user.id):
        await message.answer(LEXICON['new_user'],
                             reply_markup=kb_generator([LEXICON['registration'], LEXICON['cancel']]))
    else:
        await message.answer(text=f"{LEXICON['old_user']}",
                             reply_markup=kb_generator([LEXICON['start_buy'], LEXICON['cart'], LEXICON['cancel']]),
                             one_time_keyboard=True)


@router.message(F.text==LEXICON['registration'], StateFilter(default_state))
async def process_fill_form_command(message: Message, state: FSMContext):
    await message.answer(text=FSM_LEXICON['fsm_name'])
    await state.update_data(name=message.text)
    await state.set_state(FSMFillForm.fill_name)


@router.message(StateFilter(FSMFillForm.fill_name))
async def process_name_sent(message: Message, state: FSMContext):
    name = message.text.strip().split(' ')
    if len(name) < 2:
        await message.answer(text=FSM_LEXICON['fsm_name_fail'])
        return
    await state.update_data(name=f'{name[0].capitalize()} {name[1].capitalize()}')
    await message.answer(text=FSM_LEXICON['fsm_email'])
    await state.set_state(FSMFillForm.fill_email)


@router.message(StateFilter(FSMFillForm.fill_email), F.text.contains('@'))
async def process_email_command(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(text=FSM_LEXICON['fsm_phone_number'])
    await state.set_state(FSMFillForm.fill_phone)


@router.message(StateFilter(FSMFillForm.fill_phone), ~F.text.isalpha())
async def process_phone_sent(message: Message, state: FSMContext):
    data = await state.get_data()
    if len(message.text) != 11:
        await message.answer(FSM_LEXICON['error_value'])
        return
    await state.update_data(phone=message.text)
    user.add_user(username=data['name'], email=data['email'], phone_number=message.text,
                  telegram_id=message.from_user.id)
    await message.answer(text=FSM_LEXICON['successfuly_registration'],
                         reply_markup=kb_generator([LEXICON['start_buy'], LEXICON['cart'], LEXICON['cancel']]))
    await state.clear()

@router.message(Command('location'))
async def get_location(message: Message):
    await message.answer(LEXICON['location'])
    await message.answer_location(latitude=42.736093725784436, longitude=47.13569643312872)

@router.message(F.text == (LEXICON['start_buy']))
async def start_buy(message:Message):
    await message.answer(text=LEXICON['select_cats'],reply_markup=kb_generator(categories))
    print(message.from_user.id)

#Тут исправить
@router.message(Cats_Filter(categories=categories))
async def get_products_in_categories(message:Message):
    data: list = [x for x in product.get_products(category=message.text)[Pagination.count_pages]]
    Pagination.product_data = data
    await message.answer_photo(photo=data[-1],caption=f"<strong>{data[1]}</strong>\n<b>Характеристики:</b>\n{data[3]}\n<b>Категория:</b> {data[2]}\n<b>Стоимость:</b> {data[4]} руб.\n<i>ID:</i> {data[0]}",reply_markup=ikb_generator(2,pagination[0],pagination[1]))

@router.callback_query(F.data == pagination[1])
async def pag_next(callback:CallbackQuery):
    Pagination.count_pages += 1
    data = Pagination.product_data
    try:
        if Pagination.count_pages < len(product.get_products()) - 1:
            await callback.message.answer_photo(photo=data[-1],caption=f"<strong>{data[1]}</strong>\n<b>Характеристики:</b>\n{data[3]}\n<b>Категория:</b> {data[2]}\n<b>Стоимость:</b> {data[4]} руб.\n<i>ID:</i> {data[0]}",reply_markup=ikb_generator(2,pagination[0],pagination[1]))
        else:
            await callback.answer(text=LEXICON['error'])
    except TelegramBadRequest:
        await callback.answer()


