from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text, BigInteger, Time, MetaData
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from .database import Base

metadata_obj = MetaData()


class Students(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg: Mapped[str] = mapped_column()
    # tg_id = Column(Text, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))
    # group_id = Column(ForeignKey("groups.group_id"))
    auth: Mapped["Student_Auth"] = relationship(back_populates="student", uselist=False)
    group: Mapped["Groups"] = relationship(back_populates="students")


class Student_Auth(Base):
    __tablename__ = "students_auth"

    id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    # tg_id = Column(ForeignKey("students.tg_id"), primary_key=True)
    password: Mapped[str] = mapped_column()
    # password = Column(Text, nullable=False)

    student: Mapped["Students"] = relationship(back_populates="auth")


class Subjects(Base):
    __tablename__ = "subjects"

    chat_id: Mapped[int] = mapped_column()

    subject_id: Mapped[int] = mapped_column(primary_key=True)
    # subject_id = Column(BigInteger, primary_key=True)
    subject_name: Mapped[str] = mapped_column()
    # subject_name = Column(Text, nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"))
    # teacher_id = Column(ForeignKey())
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))
    # group_id = Column(ForeignKey("groups.group_id"))
    link_report: Mapped[str | None] = mapped_column()
    # link_report = Column(Text, nullable=True)
    regulation: Mapped[str | None] = mapped_column()
    # regulation = Column(Text, nullable=True)

    teacher: Mapped["Teachers"] = relationship(back_populates="subjects")
    group: Mapped["Groups"] = relationship(back_populates="subjects")
    # homeworks: Mapped[list["Homeworks"]] = relationship(back_populates="subject")


class Groups(Base):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(primary_key=True)
    # group_id = Column(BigInteger, primary_key=True)
    group_number: Mapped[str] = mapped_column()
    # group_number = Column(Text, nullable=False)
    subgroup_number: Mapped[str | None] = mapped_column()
    # subgroup_number = Column(Text, nullable=True)

    students: Mapped[list["Students"]] = relationship(back_populates="group")
    subjects: Mapped[list["Subjects"]] = relationship(back_populates="group")
    homeworks: Mapped[list["Homeworks"]] = relationship(back_populates="group")


class Teachers(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(primary_key=True)
    # teacher_id = Column(BigInteger, primary_key=True)
    name_teacher: Mapped[str] = mapped_column()
    # name_teacher = Column(Text, nullable=False)
    email_teacher: Mapped[str] = mapped_column()
    # email_teacher = Column(Text, nullable=False)

    subjects: Mapped[list["Subjects"]] = relationship(back_populates="teacher")


class Homeworks(Base):
    __tablename__ = "homeworks"

    chat_id: Mapped[int] = mapped_column()
    # homework_id = Column(BigInteger, primary_key=True)
    homework_id: Mapped[int] = mapped_column(primary_key=True)
    subject_name: Mapped[str] = mapped_column()
    # subject_id = Column(ForeignKey("subjects.subject_id"))
    text_homework: Mapped[str] = mapped_column()
    # text_homework = Column(Text, nullable=False)
    deadline: Mapped[datetime] = mapped_column()
    # deadline = Column(Time, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.group_id"))
    # group_id = Column(ForeignKey("groups.group_id"))

    # subject: Mapped["Subjects"] = relationship(back_populates="homeworks")
    group: Mapped["Groups"] = relationship(back_populates="homeworks")



