
#Опишите модель данных, используя SQLAlchemy.

#Разработайте класс для выполнения операций INSERT и SELECT для полученной модели данных.

#Напишите метод для заполнения модели данными из файла students.csv.

#Напишите методы для:
  #получения списка студентов по названию факультета;
  #получения списка уникальных курсов;
  #получения среднего балла по факультету;
  #получения списка студентов по выбранному курсу с оценкой ниже 30 баллов.

from fastapi import Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from model import Faculty, Course, User, Student, Score
from db import get_session


class StudentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Faculty
    async def get_faculty_by_name(self, name: str) -> Optional[Faculty]:
       result = await self.db.execute(
           select(Faculty).where(Faculty.name == name)
       )
       return result.scalar_one_or_none()
    
    async def create_faculty(self, name: str) -> Faculty:
        faculty = Faculty(name=name)
        self.db.add(faculty)
        await self.db.commit()
        await self.db.refresh(faculty)

        return faculty
    
    #Course

    async def get_course_by_name(self, name: str) -> Optional[Course]:
        result = await self.db.execute(
            select(Course).where(Course.name == name)
        )
        return result.scalar_one_or_none()

    async def create_course(self, name: str) -> Course:
        course = Course(name=name)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course
    
    #Student

    async def get_student(
            self,
            lastname: Optional[str],
            firstname: Optional[str],
            faculty_id
    ) -> Optional[Student]:
        if not lastname or not firstname or faculty_id is None:
            return None
        
        student = select(Student).where(
            Student.lastname == lastname,
            Student.firstname == firstname,
            Student.faculty_id == faculty_id
        )
        
        result = await self.db.execute(student)
        return result.scalar_one_or_none()
    
    async def create_student(self, student_date: dict) -> Student:
        """
        Ожидается словарь (student_date):
        {
            "lastname": str,
            "firstname": str,
            "faculty": Faculty  # объект факультета
        }
        """

        student = Student(**student_date)
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    #Score

    async def create_score(self, score_data: dict) -> Score:
        """
        Ожидается словарь(score_datr):
        {
            "student": Student,
            "course": Course,
            "score": int
        }
        """
        score = Score(**score_data)
        self.db.add(score)
        await self.db.commit()
        await self.db.refresh(score)
        return score

    #Pagination

    async def get_students(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Student]:
        if skip < 0:
            skip = 0
        if limit <= 0:
            limit = 100

        stmt = (
            select(Student)
            .order_by(Student.lastname, Student.firstname)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    #Задачи (hw) ---------- МЕТОДЫ ПО ЗАДАНИЮ ----------

    async def get_students_by_faculty(self, faculty_name: Optional[str]) -> list[Student]:
        """
        получение списка студентов по названию факультета
        """
        if not faculty_name:
            return []

        stmt = (
            select(Student)
            .join(Faculty, Student.faculty_id == Faculty.id)
            .where(Faculty.name == faculty_name)
            .order_by(Student.lastname, Student.firstname)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_unique_courses(self) -> list[str]:
        """
        получение списка уникальных курсов
        """
        stmt = select(Course.name).distinct().order_by(Course.name)
        result = await self.db.execute(stmt)
        rows = result.all()  # [(name,), (name2,), ...]
        return [row[0] for row in rows]

    async def get_avg_score_by_faculty(self, faculty_name: Optional[str]) -> Optional[float]:
        """
        получение среднего балла по факультету
        """
        if not faculty_name:
            return None

        stmt = (
            select(func.avg(Score.score))
            .join(Student, Score.student_id == Student.id)
            .join(Faculty, Student.faculty_id == Faculty.id)
            .where(Faculty.name == faculty_name)
        )
        result = await self.db.execute(stmt)
        value = result.scalar()
        return float(value) if value is not None else None

    async def get_students_by_course_with_score_below(
        self,
        course_name: Optional[str],
        threshold: int = 30,
    ) -> list[Student]:
        """
        получение списка студентов по выбранному курсу с оценкой ниже threshold (по умолчанию 30)
        """
        if not course_name:
            return []

        stmt = (
            select(Student)
            .join(Score, Score.student_id == Student.id)
            .join(Course, Score.course_id == Course.id)
            .where(
                Course.name == course_name,
                Score.score < threshold,
            )
            .order_by(Student.lastname, Student.firstname)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()


    
    #User 

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_date: dict) -> User:
        user = User(**user_date)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
        
    async def get_user_by_email(self, email:str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
        
async def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)

    

