from aiogram.fsm.state import StatesGroup, State


class HomeworkStates(StatesGroup):
    homework_title = State()
    homework_data = State()
    deadline = State()

class SettingsStates(StatesGroup):
    teacher = State()
    teacher_email = State()
    subject = State()
    group_number = State()
    subgroup_number = State()
    regulation_link = State()
    menu = State()