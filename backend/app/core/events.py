from app.core.database import connect_db, close_db
from app.core.logging import setup_logging


async def startup() -> None:
    setup_logging()
    await connect_db()


async def shutdown() -> None:
    await close_db()
