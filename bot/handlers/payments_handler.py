import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram import Router, F

from bot.states import UserStates
from config.logger import logger
from database.confdb import session
from database.models import User
from database.utils import get_user_by_user_id


router = Router()


async def donate_handler(
    callback: CallbackQuery, button: Button, dialog: DialogManager
):
    """
    Обработать выбор суммы доната
    и отправить пользователю счет на оплату.
    """
    amount = button.widget_id.split("_")[1]
    user = callback.from_user
    logger.info(f"{user.username}:{user.id} выбрал донат на {amount}⭐️")
    await dialog.done()

    try:
        await callback.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Поддержка бота",
            description=f"Спасибо за вашу поддержку! Вы выбрали {amount} ⭐️",
            payload=f"donate_{amount}",
            provider_token="STARS",
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount} Stars", amount=int(amount))],
        )
    except Exception as error:
        logger.exception(
            f"{user.username}:{user.id} ошибка отправки доната {amount}⭐️: {error!r}"
        )
        await callback.message.answer(
            "⚠️ Не удалось отправить запрос на оплату. Попробуйте позже 🙏"
        )


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """
    Обработать pre_checkout запрос
    перед оплатой и подтвердить его.
    """
    logger.debug("Обработка pre_checkout запроса: %s", pre_checkout_query.id)
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment.invoice_payload.startswith("donate_"))
async def process_successful_payment(
    message: Message, state: FSMContext, dialog_manager: DialogManager
):
    """
    Обработать успешную оплату
    доната и вернуть пользователя в меню.
    """
    logger.info(
        "Успешная оплата от пользователя %s: payload=%s",
        message.from_user.id,
        message.successful_payment.invoice_payload,
    )
    user: User = await get_user_by_user_id(
        user_id=message.from_user.id,
        session=session,
    )
    target_state = (
        UserStates.status
        if not user
        else (
            UserStates.main_menu_student
            if user.status == "student"
            else UserStates.main_menu_teacher
        )
    )

    send_message = await message.answer(
        "✅ Платеж успешно прошел, спасибо вам за поддержку! Сейчас я переведу вас в основное меню..."
    )
    await asyncio.sleep(5)
    try:
        await send_message.delete()
    except Exception:
        pass

    await dialog_manager.start(
        state=target_state,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
