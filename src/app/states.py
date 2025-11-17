from aiogram.fsm.state import StatesGroup, State


class HomeworkStates(StatesGroup):
    homework_data = State()
    deadline = State()

class SettingsStates(StatesGroup):
    teacher = State()
    subject = State()
    group_list = State()