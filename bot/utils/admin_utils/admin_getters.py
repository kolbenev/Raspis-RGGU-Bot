from sqlalchemy import select, func

from database.confdb import session
from database.models import User


async def get_admin_stats(dialog_manager, **kwargs):
    total_users = await session.scalar(select(func.count()).select_from(User))
    students = await session.scalar(
        select(func.count()).where(User.status == "student")
    )
    teachers = await session.scalar(
        select(func.count()).where(User.status == "teacher")
    )
    admins = await session.scalar(select(func.count()).where(User.is_admin == True))
    notifications_enabled = await session.scalar(
        select(func.count()).where(User.notify_enabled == True)
    )

    text = (
        f"📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"🎓 Студентов: {students}\n"
        f"👩‍🏫 Преподавателей: {teachers}\n"
        f"🛠 Админов: {admins}\n"
        f"🔔 Уведомления включены: {notifications_enabled}"
    )

    return {"text": text}
