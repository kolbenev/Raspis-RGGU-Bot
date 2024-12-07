from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.utils import lazy_get_group_by_name, create_new_group
from database.models import User
from bot.utils.text_for_messages import stage_formob, stage_grupp_name
from telebot.async_telebot import AsyncTeleBot
from config.cafs import caf_id

from telebot.types import Message


async def register_user(message: Message, session:AsyncSession) -> User:
    new_user = User(
        chat_id=message.chat.id,
    )
    session.add(new_user)
    await session.commit()
    return new_user



async def registered_stage_kyrs(message: Message, user: User, bot: AsyncTeleBot, session:AsyncSession):
        if message.text.isdigit() and 1 <= int(message.text) <= 6:
            user.kyrs = int(message.text)
            user.user_status = "registered_stage_formob"
            await session.commit()
            await bot.send_message(message.chat.id, text=stage_formob)
        else:
            await bot.send_message(message.chat.id, text='Неверный ввод курса, попробуй еще раз.')



async def registered_stage_formob(message: Message, user: User, bot: AsyncTeleBot, session: AsyncSession):
    formob_list = ['Д', 'В', 'З', '2', 'М', 'У']
    user_answer = message.text.upper()
    if user_answer in formob_list:
        await bot.send_message(message.chat.id, text=stage_grupp_name)
        user.formob = message.text
        user.user_status = "registered_stage_group"
        await session.commit()
    else:
        await bot.send_message(chat_id=message.chat.id, text='Неверный ввод формы обучения, попробуйте еще раз!')


async def registered_stage_group(user: User, message: Message, bot: AsyncTeleBot, session: AsyncSession):
    kaf = caf_id[user.formob][user.kyrs][message.text]
    if kaf:
        try:
            group = await lazy_get_group_by_name(session=session, group_name=message.text)
            user.gruppa = group.id
            await session.commit()
        except ValueError:
            group = await create_new_group(session=session, kaf=kaf, name=message.text)
            user.gruppa = group.id
            await session.commit()
        finally:
            await bot.send_message(message.chat.id, text='Успешно зарегистрирован!')
            user.user_status = "student"
            await session.commit()

