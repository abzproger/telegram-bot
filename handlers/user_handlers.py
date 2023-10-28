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


