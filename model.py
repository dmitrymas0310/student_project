
from db import Base, BaseModelMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint


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

    student = relationship("Student", back_populates="score", lazy="select")
    course = relationship("Course", back_populates="course", lazy="select")












