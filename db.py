import asyncpg
import uuid
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import create_async_engine

class Base(DeclarativeBase):
    pass

@declarative_mixin
class BaseModelMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    create_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    update_at = Column(DateTime, nullable=False, default=datetime.utcnow)



DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5433/students_db"

async def create_db():
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


