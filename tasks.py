import asyncio

from celery_app import celery_app
from db import async_session_maker
from service import StudentService


@celery_app.task
def import_students_from_csv(file_path: str) -> None:
    """
    Celery-задача: запустить импорт студентов из CSV в фоне.
    """

    async def _run():
        async with async_session_maker() as session:
            service = StudentService(session)
            await service.load_from_csv(file_path)

    asyncio.run(_run())