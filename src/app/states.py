from aiogram.fsm.state import StatesGroup, State


class HomeworkStates(StatesGroup):
    homework_data = State()
    deadline = State()

class SettingsStates(StatesGroup):
    teacher = State()
    teacher_email = State()
    subject = State()
    group_number = State()
    subgroup_number = State()
    menu = State()