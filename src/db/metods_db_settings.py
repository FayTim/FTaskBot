from sqlalchemy import select, update
from src.db.database import async_session_factory
from src.db.models import Teachers, Groups, Subjects

async def save_chat_settings(chat_id, data):
    teacher_name = data["teacher"]
    teacher_email = data["teacher_email"]
    subject_name = data["subject"]
    group_number = data["group_number"]
    subgroup_number = data["subgroup_number"]
    regulation_link = data["regulation"]

    async with async_session_factory() as session:
        result = await session.execute(
            select(Teachers).where(
                Teachers.name_teacher == teacher_name,
                Teachers.email_teacher == teacher_email
            )
        )
        teacher = result.scalar_one_or_none()
        if teacher is None:
            teacher = Teachers(
                name_teacher=teacher_name,
                email_teacher=teacher_email
            )
            session.add(teacher)
            await session.flush()

        result = await session.execute(
            select(Groups).where(
                Groups.group_number == group_number,
                Groups.subgroup_number == subgroup_number
            )
        )
        group = result.scalar_one_or_none()
        if group is None:
            group = Groups(
                group_number=group_number,
                subgroup_number=subgroup_number
            )
            session.add(group)
            await session.flush()

        subject = Subjects(
            chat_id=chat_id,
            subject_name=subject_name,
            teacher_id=teacher.teacher_id,
            group_id=group.group_id,
            regulation_link=regulation_link,
        )
        session.add(subject)

        await session.commit()

async def get_settings_chat(chat_id):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Subjects).where(Subjects.chat_id == chat_id)
        )
        check_chat_id = result.scalar_one_or_none()
        return check_chat_id

async def update_teacher_in_db(chat_id, new_teacher_name):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Teachers)
            .join(Subjects, Subjects.teacher_id == Teachers.teacher_id)
            .where(Subjects.chat_id == chat_id)
        )
        teacher = result.scalar_one_or_none()
        teacher.name_teacher = new_teacher_name
        await session.commit()

async def update_teacher_email_in_db(chat_id, new_teacher_email):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Teachers)
            .join(Subjects, Subjects.teacher_id == Teachers.teacher_id)
            .where(Subjects.chat_id == chat_id)
        )
        teacher = result.scalar_one_or_none()
        teacher.email_teacher = new_teacher_email
        await session.commit()

async def update_subject_in_db(chat_id, new_subject):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Subjects).where(Subjects.chat_id == chat_id)
        )
        subject = result.scalar_one_or_none()
        subject.subject_name = new_subject
        await session.commit()

async def update_group_number_in_db(chat_id, new_group_number):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Groups)
            .join(Subjects, Subjects.teacher_id == Groups.group_id)
            .where(Subjects.chat_id == chat_id)
        )
        group = result.scalar_one_or_none()
        group.group_number = new_group_number
        await session.commit()

async def update_subgroup_number_in_db(chat_id, new_subgroup_number):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Groups)
            .join(Subjects, Subjects.teacher_id == Groups.group_id)
            .where(Subjects.chat_id == chat_id)
        )
        subgroup = result.scalar_one_or_none()
        subgroup.subgroup_number = new_subgroup_number
        await session.commit()

async def update_regulation_db(chat_id, new_regulation_link):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Subjects).where(Subjects.chat_id == chat_id)
        )
        regulation = result.scalar_one_or_none()
        regulation.regulation_link = new_regulation_link
        await session.commit()