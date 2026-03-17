from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/ping")
async def ping_database(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1 AS ok"))
    row = result.mappings().first()

    return {
        "status": "ok",
        "database": row["ok"],
    }