# bot/states.py
from aiogram.fsm.state import State, StatesGroup

class General(StatesGroup):
    main_menu = State()
    choosing_course = State()
    course_menu = State()
    asking_question = State()
    adding_course_name = State()
    uploading_document = State()
class ExamState(StatesGroup):
    waiting_for_task = State()