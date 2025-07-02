# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models

async def get_or_create_user(db: AsyncSession, telegram_id: int, username: str, full_name: str) -> models.User:
    result = await db.execute(select(models.User).filter(models.User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        user = models.User(telegram_id=telegram_id, username=username, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def create_course_for_user(db: AsyncSession, user: models.User, course_name: str) -> models.Course:
    course = models.Course(name=course_name, owner=user)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course

async def get_user_courses(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Course).where(models.Course.owner_id == user_id))
    return result.scalars().all()