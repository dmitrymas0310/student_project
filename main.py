import uvicorn
from fastapi import FastAPI

from configs import settings
from v1_api import router as auth_router


import asyncio
from model import create_db

async def main():
    await create_db()

app = FastAPI(
    title=settings.app.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

if __name__ == "__main__":

    #asyncio.run(main())

    uvicorn.run(
        "main:app",
        host=settings.app.app_host,
        port=settings.app.app_port,
        reload=True,
    )