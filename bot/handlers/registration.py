"""
Модуль регистрации.
"""

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from config.cafs import caf_id
from database.models import User
from database.confdb import session
from bot.middlewares.logger import logger
from parser.parser_main import parsing_schedule
from bot.handlers.states import RegistrationState
from bot.utils.other.keyboards import group_kb, student_kb, formob_kb, kyrs_kb
from bot.utils.utils import (
    lazy_get_group_by_name,
    create_new_group,
    lazy_get_user_by_chat_id,
)
from bot.utils.other.text_for_messages import (
    stage_grupp_name,
    stage_formob,
    stage_kyrs,
)


router = Router(name=__name__)


async def start_registration(message: Message, state: FSMContext) -> None:
    logger.info(f"{message.chat.username}:{message.chat.id} начал процесс регистрации.")
    await message.answer(text=stage_kyrs, reply_markup=kyrs_kb())
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
    logger.info(
        f"Зарегестрированн новый пользователь: {message.chat.username}:{message.chat.id} "
        f"Data: {kyrs}, {formob}, {grupp_id}"
    )
    return new_user


@router.message(RegistrationState.kyrs)
async def process_kyrs(message: Message, state: FSMContext) -> None:
    if message.text.isdigit() and 1 <= int(message.text) <= 5:
        await state.update_data(kyrs=int(message.text))
        await state.set_state(RegistrationState.formob)
        await message.answer(text=stage_formob, reply_markup=formob_kb())

    else:
        logger.info(
            f"{message.chat.username}:{message.chat.id} ввел неверный курс."
        )
        await message.answer(text="Вы неверно ввели курс, попробуйте еще раз!")


@router.message(RegistrationState.formob)
async def process_formob(message: Message, state: FSMContext) -> None:

    formob_dict = {
        "дневная": "Д",
        "вечерняя": "В",
        "заочная": "З",
        "второе высшее": "2",
        "магистратура": "М",
        "дистанционная": "У",
    }

    if message.text.lower() in formob_dict.keys():
        user_answer = formob_dict[message.text.lower()]
        await state.update_data(formob=user_answer)
        await state.set_state(RegistrationState.grupp)
        data = await state.get_data()
        await message.answer(
            text=stage_grupp_name,
            reply_markup=group_kb(formob=data["formob"], kyrs=data["kyrs"]),
        )
    else:
        logger.info(
            f"{message.chat.username}:{message.chat.id} ввел неверный formob."
        )
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
            try:
                user = await lazy_get_user_by_chat_id(
                    chat_id=message.chat.id, session=session
                )
                user.formob = formob
                user.kyrs = kyrs
                user.gruppa = group
                await session.commit()
                await state.clear()
                await message.answer(
                    text="Вы успешно изменили свои данные!", reply_markup=student_kb()
                )

            except ValueError:
                await register_user(
                    message=message,
                    session=session,
                    formob=formob,
                    kyrs=kyrs,
                    grupp_id=group,
                )
                await state.clear()
                await message.answer(
                    text="Вы успешно зарегистрировались!", reply_markup=student_kb()
                )

    except KeyError:
        logger.info(
            f"{message.chat.username}:{message.chat.id} ввел неверную группу."
        )
        await message.answer(
            text="Такой группы нет или вы неверно ввели ее название, попробуйте еще раз."
        )
