from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text, BigInteger, Time, MetaData
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from .database import Base

metadata_obj = MetaData()


class Students(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg: Mapped[str] = mapped_column()
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))
    auth: Mapped["Student_Auth"] = relationship(back_populates="student", uselist=False)
    group: Mapped["Groups"] = relationship(back_populates="students")


class Student_Auth(Base):
    __tablename__ = "students_auth"

    id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    password: Mapped[str] = mapped_column()

    student: Mapped["Students"] = relationship(back_populates="auth")


class Subjects(Base):
    __tablename__ = "subjects"

    chat_id: Mapped[int] = mapped_column(BigInteger)

    subject_id: Mapped[int] = mapped_column(primary_key=True)
    subject_name: Mapped[str] = mapped_column()
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))
    regulation_link: Mapped[str | None] = mapped_column()

    teacher: Mapped["Teachers"] = relationship(back_populates="subjects")
    group: Mapped["Groups"] = relationship(back_populates="subjects")


class Groups(Base):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(primary_key=True)
    group_number: Mapped[str] = mapped_column()
    subgroup_number: Mapped[str | None] = mapped_column()

    students: Mapped[list["Students"]] = relationship(back_populates="group")
    subjects: Mapped[list["Subjects"]] = relationship(back_populates="group")
    homeworks: Mapped[list["Homeworks"]] = relationship(back_populates="group")


class Teachers(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(primary_key=True)
    name_teacher: Mapped[str] = mapped_column()
    email_teacher: Mapped[str] = mapped_column()

    subjects: Mapped[list["Subjects"]] = relationship(back_populates="teacher")


class Homeworks(Base):
    __tablename__ = "homeworks"

    chat_id: Mapped[int] = mapped_column(BigInteger)
    homework_id: Mapped[int] = mapped_column(primary_key=True)
    subject_name: Mapped[str] = mapped_column()
    text_homework: Mapped[str] = mapped_column()
    deadline: Mapped[datetime] = mapped_column()
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))

    group: Mapped["Groups"] = relationship(back_populates="homeworks")



