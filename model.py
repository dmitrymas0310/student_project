
from typing import Any
from db import Base, BaseModelMixin, DATABASE_URL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.ext.asyncio import create_async_engine


class Faculty(Base, BaseModelMixin):
    __tablename__="faculty"

    name = Column(String, unique=True, nullable=False)

    students = relationship("Student", back_populates="faculty", lazy="select")


class Student(Base, BaseModelMixin):
    __tablename__="student"

    lastname = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False)

    faculty = relationship("Faculty", back_populates="students", lazy="select")
    scores = relationship("Score", back_populates="student", lazy="select")

class Course(Base, BaseModelMixin):
    __tablename__="course"

    name = Column(String, unique=True, nullable=False)

    scores = relationship("Score", back_populates="course", lazy="select")

class Score(Base, BaseModelMixin):
    __tablename__="score"
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id", ondelete="CASCADE"),nullable=False)
    score = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="scores", lazy="select")
    course = relationship("Course", back_populates="scores", lazy="select")


class User(Base, BaseModelMixin):
    __tablename__="users"

    username = Column(String)
    full_name = Column(String)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return (
            f"uuid - {self.uuid}, username - {self.username}"
            f"full_name - {self.full_name}, email - {self.email}"
            f"status - {self.status}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid":self.uuid,
            "username":self.username,
            "full_name":self.full_name,
            "email":self.email,
            "status":self.status
        }


async def create_db():
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)












