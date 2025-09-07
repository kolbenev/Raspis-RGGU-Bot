from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    status = State()
    teacher_select = State()
    student_course = State()
    student_form = State()
    student_direction = State()

    main_menu_student = State()
    main_menu_teacher = State()

    other_scheduler = State()
    other_groups_course = State()
    other_groups_list = State()
    other_groups_form = State()

    rooms_list = State()
    prepod_list = State()

    schedule_today = State()
    schedule_tomorrow = State()
    schedule_week = State()

    donate = State()
    notifications_settings = State()


class AdminStates(StatesGroup):
    main_menu = State()
    sender = State()
