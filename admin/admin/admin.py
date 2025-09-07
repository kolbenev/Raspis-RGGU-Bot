from sqladmin import ModelView

from database.models import User


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [
        User.id,
        User.username,
        User.created_at,
        User.status,
        User.chat_id,
        User.user_id,
        User.is_admin,
        User.group_id,
        User.eduform,
        User.teacher_id,
        User.notify_time,
        User.notify_enabled,
    ]
    column_searchable_list = [User.user_id, User.username, User.chat_id]
    column_sortable_list = [User.id, User.created_at]
    can_delete = True
    can_edit = True
    can_create = True
