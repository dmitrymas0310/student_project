from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import csv
from sqlalchemy.ext.asyncio import AsyncSession

from repository import StudentRepository, UserRepository, get_user_repository
from schemas import UserResponse, UserRegistrate
from configs import settings
from schemas import TokenData
from schemas import UserResponse


class StudentService:
    def __init__(self, db: AsyncSession):
        self.repo = StudentRepository(db)

    async def load_from_csv(self, file_path: str) -> None:
        with open(file_path, encoding="utf-8") as f:
            # если файл классический csv ("," или ";" — csv сам разрулит)
            reader = csv.reader(f)
            next(reader, None)  # заголовок

            for row in reader:
                # на всякий случай берём только первые 5 колонок
                last_name, first_name, faculty_name, course_name, score_str = row[:5]

                last_name = last_name.strip()
                first_name = first_name.strip()
                faculty_name = faculty_name.strip()
                course_name = course_name.strip()
                score_value = int(score_str)

                faculty = await self.repo.get_faculty_by_name(faculty_name)
                if faculty is None:
                    faculty = await self.repo.create_faculty(faculty_name)

                student = await self.repo.get_student(
                    lastname=last_name,
                    firstname=first_name,
                    faculty_id=faculty.id,
                )
                if student is None:
                    student = await self.repo.create_student(
                        {
                            "lastname": last_name,
                            "firstname": first_name,
                            "faculty": faculty,
                        }
                    )

                course = await self.repo.get_course_by_name(course_name)
                if course is None:
                    course = await self.repo.create_course(course_name)

                await self.repo.create_score(
                    {
                        "student": student,
                        "course": course,
                        "score": score_value,
                    }
                )



class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.pwd_context = CryptContext(schemes=["sha512_crypt"])
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
    
    async def get_user_by_email(self, email: str) -> UserResponse | None:
        user = await self.repo.get_user_by_email(email)
        return user
    
    async def create_user(self, user_data: UserRegistrate) -> UserResponse:
        """Создать нового пользователя"""
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже существует",
            )

        data_dump = user_data.model_dump()
        data_dump["hashed_password"] = self.get_password_hash(
            data_dump["password"]
        )
        data_dump.pop("password")
        user = await self.repo.create(data_dump)

        return user

async def get_users_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)



security = HTTPBearer()


class AuthService:

    def __init__(
        self, repo: UserRepository, credentials: HTTPAuthorizationCredentials | None = None
    ):
        self.repo = repo
        self.pwd_context = CryptContext(schemes=["sha512_crypt"])
        self.credentials = credentials

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str):
        user = await self.repo.get_user_by_email(email)

        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = None):

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        data.update({"exp": expire})

        encoded_jwt = jwt.encode(
            data,
            settings.auth.sekret_key,
            algorithm=settings.auth.algorithm,
        )
        return encoded_jwt

    async def get_current_user(
        self,
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                self.credentials.credentials,
                settings.auth.sekret_key,
                algorithms=[settings.auth.algorithm],
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception

        user = await self.repo.get_user_by_email(email)
        if user.status is False:
            raise HTTPException(status_code=400, detail="Inactive user")
        if user is None:
            raise credentials_exception
        return user


async def get_req_service(
    repo: UserResponse = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


async def get_auth_service(
    repo: UserResponse = Depends(get_user_repository),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthService:
    return AuthService(repo, credentials)