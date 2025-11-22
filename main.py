import asyncio
import model
from db import create_db

async def main():
    await create_db()

if __name__ == "__main__":

    asyncio.run(main())