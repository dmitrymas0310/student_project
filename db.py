import asyncpg
import uuid
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, declarative_mixin, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5433/students_db"

class Base(DeclarativeBase):
    pass

@declarative_mixin
class BaseModelMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    create_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    update_at = Column(DateTime, nullable=False, default=datetime.utcnow)


engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
          yield session
        finally:
          await session.close()







