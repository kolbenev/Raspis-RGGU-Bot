from aiogram_dialog import Dialog

from bot.dialogs.user_dialogs.donate import donate_window
from bot.dialogs.user_dialogs.main_menu import (
    main_menu_student,
    main_menu_teacher,
    other_scheduler_window,
)
from bot.dialogs.user_dialogs.notifications import notifications_settings_window
from bot.dialogs.user_dialogs.other_group import (
    other_groups_group_select_window,
    other_groups_course_select_window,
    other_groups_eduform_select_window,
)
from bot.dialogs.user_dialogs.registration import (
    status_select_window,
    student_course_select_window,
    student_eduform_select_window,
    student_direction_select_window,
    teacher_select_window,
)
from bot.dialogs.user_dialogs.rooms_teachers import (
    rooms_list_window,
    teachers_schedule_select_window,
)
from bot.dialogs.user_dialogs.scheduler import (
    schedule_today_window,
    schedule_tomorrow_window,
    schedule_week_window,
)

dialog = Dialog(
    status_select_window,
    teacher_select_window,
    student_course_select_window,
    student_eduform_select_window,
    student_direction_select_window,
    main_menu_student,
    other_scheduler_window,
    schedule_today_window,
    schedule_tomorrow_window,
    schedule_week_window,
    rooms_list_window,
    teachers_schedule_select_window,
    notifications_settings_window,
    other_groups_eduform_select_window,
    other_groups_course_select_window,
    other_groups_group_select_window,
    donate_window,
    main_menu_teacher,
)
