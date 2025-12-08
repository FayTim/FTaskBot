from src.db.database import async_session_factory
from src.db.models import Homeworks, Subjects, Groups
from sqlalchemy import select

async def send_homework(chat_id, text, deadline):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Subjects, Groups)
            .join(Groups, Subjects.group_id == Groups.group_id)
            .where(Subjects.chat_id == chat_id)
        )
        row = result.first()
        if row is None:
            return

        subject, group = row
        subject_name = subject.subject_name
        group_id = group.group_id

        new_homework = Homeworks(
            chat_id=chat_id,
            subject_name=subject_name,
            text_homework=text,
            group_id=group_id,
            deadline=deadline
        )

        session.add(new_homework)
        await session.commit()
