"""
Модуль регистрации.
"""

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.other.keyboards import group_kb, student_kb
from bot.utils.other.text_for_messages import stage_grupp_name, stage_formob, stage_kyrs, welcome_messages
from bot.utils.utils import lazy_get_group_by_name, create_new_group
from bot.handlers.states import RegistrationState
from database.confdb import session
from database.models import User
from parser.parser_main import parsing_schedule
from config.cafs import caf_id


router = Router(name=__name__)


async def start_registration(message: Message, state: FSMContext) -> None:
    await message.answer(text=welcome_messages)
    await message.answer(text=stage_kyrs)
    await state.set_state(RegistrationState.kyrs)


async def register_user(
    message: Message,
    session: AsyncSession,
    formob: str,
    kyrs: int,
    grupp_id: int,
) -> User:
    chat_id = message.chat.id
    new_user = User(
        chat_id=chat_id,
        formob=formob,
        kyrs=kyrs,
        gruppa=grupp_id,
    )
    session.add(new_user)
    await session.commit()
    return new_user


@router.message(RegistrationState.kyrs)
async def process_kyrs(message: Message, state: FSMContext) -> None:
    if message.text.isdigit() and 1 <= int(message.text) <= 6:
        await state.update_data(kyrs=int(message.text))
        await state.set_state(RegistrationState.formob)
        await message.answer(text=stage_formob)
    else:
        await message.answer(text="Вы неверно ввели курс, попробуйте еще раз!")


@router.message(RegistrationState.formob)
async def process_formob(message: Message, state: FSMContext) -> None:
    formob_list = ["Д", "В", "З", "2", "М", "У"]
    user_answer = message.text.upper()
    if user_answer in formob_list:
        await state.update_data(formob=user_answer)
        await state.set_state(RegistrationState.grupp)
        data = await state.get_data()
        await message.answer(text=stage_grupp_name, reply_markup=group_kb(formob=data["formob"], kyrs=data["kyrs"]))
    else:
        await message.answer(text="Неверный ввод формы обучения, попробуйте еще раз!")


@router.message(RegistrationState.grupp)
async def process_grupp(message: Message, state: FSMContext) -> None:
    user_answer = message.text
    data = await state.get_data()
    formob = data["formob"]
    kyrs = data["kyrs"]
    group = 0

    try:
        caf = caf_id[formob][kyrs][user_answer]
        try:
            new_group = await lazy_get_group_by_name(
                session=session, group_name=user_answer
            )
            group = new_group.id
            await session.commit()

        except ValueError:
            new_group = await create_new_group(
                session=session,
                caf=caf,
                name=user_answer,
                kyrs=kyrs,
                formob=formob,
            )
            group = new_group.id
            await session.commit()
            await parsing_schedule(formob=formob, kyrs=kyrs, caf=caf)

        finally:
            await register_user(
                message=message,
                session=session,
                formob=formob,
                kyrs=kyrs,
                grupp_id=group,
            )
            await state.clear()
            await message.answer(text="Вы успешно зарегистрировались!", reply_markup=student_kb())

    except KeyError:
        await message.answer(
            text="Такой группы нет или вы неверно ввели ее название, попробуйте еще раз."
        )
