from aiogram import Router
import requests
from aiogram import F
from aiogram.filters import Command, CommandStart, Filter,BaseFilter
from aiogram.types import Message
from database.database import Products, db, user, Cart
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from keyboard.keyboard import kb_generator, ikb_generator
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from dataclasses import dataclass
from lexicon.lexicon_ru import LEXICON, FSM_LEXICON, pagination

router: Router = Router()


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


@router.message(F.text == LEXICON['registration'], StateFilter(default_state))
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


@router.message(StateFilter(FSMFillForm.fill_email))
async def process_email_command(message: Message, state: FSMContext):
    try:
        response = requests.get(
            f'https://perfect-inc.com/tools/email-checker/api/?email={message.text}').json()  # Проверка на существование email
        if response['exists'] == True:
            await state.update_data(email=message.text)
            await message.answer(text=FSM_LEXICON['fsm_phone_number'])
            await state.set_state(FSMFillForm.fill_phone)
    except:
        await message.answer(FSM_LEXICON['error_email'])



@router.message(StateFilter(FSMFillForm.fill_phone), ~F.text.isalpha())
async def process_phone_sent(message: Message, state: FSMContext):
    data = await state.get_data()
    if len(message.text) != 11:
        await message.answer(FSM_LEXICON['error_value'])
        return
    await state.update_data(phone=message.text)
    user.add_user(username=data['name'], email=data['email'], phone_number=message.text,
                  telegram_id=message.from_user.id,)
    await message.answer(text=FSM_LEXICON['successfuly_registration'],
                         reply_markup=kb_generator([LEXICON['start_buy'], LEXICON['cart'], LEXICON['cancel']]))
    await state.clear()
