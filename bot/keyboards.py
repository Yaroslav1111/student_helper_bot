# bot/keyboards.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.models import Course

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Мои курсы", callback_data="my_courses")
    builder.button(text="➕ Добавить новый курс", callback_data="add_course")
    builder.adjust(1)
    return builder.as_markup()

def courses_kb(courses: list[Course]):
    builder = InlineKeyboardBuilder()
    for course in courses:
        builder.button(text=f"Курс: {course.name}", callback_data=f"select_course_{course.id}")
    builder.button(text="⬅️ Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def course_menu_kb(course_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Задать вопрос по курсу", callback_data=f"ask_question_{course_id}")
    builder.button(text="📄 Добавить материал (PDF)", callback_data=f"upload_doc_{course_id}")
    builder.button(text="⬅️ К списку курсов", callback_data="my_courses")
    builder.adjust(1)
    return builder.as_markup()