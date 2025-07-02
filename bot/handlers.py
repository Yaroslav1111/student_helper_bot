# bot/handlers.py
import os
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from .keyboards import main_menu_kb, courses_kb, course_menu_kb
from .states import General
from app import crud
from app.database import AsyncSessionLocal
from rag_system.processor import get_qa_chain, process_document

router = Router()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async for db in get_db_session():
        await crud.get_or_create_user(
            db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
    await state.set_state(General.main_menu)
    await message.answer("👋 Привет! Я твой студенческий помощник.", reply_markup=main_menu_kb())

# --- Обработка главного меню ---
@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(General.main_menu)
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())

# --- Флоу работы с курсами ---
@router.callback_query(F.data == "my_courses")
async def show_my_courses(callback: CallbackQuery, state: FSMContext):
    async for db in get_db_session():
        user = await crud.get_or_create_user(db, callback.from_user.id, None, None)
        courses = await crud.get_user_courses(db, user.id)
    if not courses:
        await callback.answer("У вас пока нет курсов. Давайте добавим первый!", show_alert=True)
        return
    await state.set_state(General.choosing_course)
    await callback.message.edit_text("Выберите курс для работы:", reply_markup=courses_kb(courses))

@router.callback_query(F.data.startswith("select_course_"))
async def select_course(callback: CallbackQuery, state: FSMContext):
    course_id = int(callback.data.split("_")[2])
    await state.update_data(current_course_id=course_id)
    await state.set_state(General.course_menu)
    await callback.message.edit_text(f"Выбран курс. Что делаем дальше?", reply_markup=course_menu_kb(course_id))

# --- Флоу добавления курса ---
@router.callback_query(F.data == "add_course")
async def add_course_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(General.adding_course_name)
    await callback.message.edit_text("Введите название нового курса:")

@router.message(General.adding_course_name)
async def add_course_name(message: Message, state: FSMContext):
    course_name = message.text
    async for db in get_db_session():
        user = await crud.get_or_create_user(db, message.from_user.id, None, None)
        await crud.create_course_for_user(db, user, course_name)
    await message.answer(f"✅ Курс '{course_name}' успешно создан!", reply_markup=main_menu_kb())
    await state.set_state(General.main_menu)

# --- Флоу Задать Вопрос / Загрузить Документ ---
@router.callback_query(F.data.startswith("ask_question_"))
async def ask_question_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(General.asking_question)
    await callback.message.edit_text("Введите ваш вопрос. Я поищу ответ в материалах курса.")

@router.message(General.asking_question)
async def process_question(message: Message, state: FSMContext):
    data = await state.get_data()
    course_id = data.get("current_course_id")
    qa_chain = get_qa_chain(course_id)
    if not qa_chain:
        await message.answer("К сожалению, для этого курса еще нет учебных материалов. Загрузите их.")
        return
    
    await message.answer("⏳ Думаю... Пожалуйста, подождите.")
    # Запускаем в отдельном потоке, чтобы не блокировать бота
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, qa_chain, {"query": message.text})
    await message.answer(result.get("result", "Не удалось найти точный ответ."))

@router.callback_query(F.data.startswith("upload_doc_"))
async def upload_doc_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(General.uploading_document)
    await callback.message.edit_text("Отправьте мне PDF-файл для этого курса.")

@router.message(General.uploading_document, F.document)
async def handle_document(message: Message, state: FSMContext, bot: Bot):
    if not message.document.mime_type == 'application/pdf':
        await message.answer("Пожалуйста, отправьте файл в формате PDF.")
        return
    
    data = await state.get_data()
    course_id = data.get("current_course_id")
    
    await message.answer("✅ Файл получен. Начинаю обработку. Это может занять несколько минут. Я сообщу, когда закончу.")

    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    
    local_file_path = f"data/uploaded_files/{message.document.file_name}"
    await bot.download_file(file_path, destination=local_file_path)
    
    # Асинхронно обрабатываем документ
    await process_document(local_file_path, str(course_id))

    await message.answer(f"✅ Файл '{message.document.file_name}' успешно обработан и добавлен в базу знаний курса!", reply_markup=course_menu_kb(course_id))
    await state.set_state(General.course_menu)