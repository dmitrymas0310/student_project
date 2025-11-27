import asyncio

from db import async_session_maker
from service import StudentService


async def main():
    async with async_session_maker() as session:
        service = StudentService(session)
        await service.load_from_csv("data/students.csv")
        print("Импорт завершён")


if __name__ == "__main__":
    asyncio.run(main())