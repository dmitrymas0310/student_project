
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
from model import Faculty, Course, User
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
    
    #Course CRUD

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

    

