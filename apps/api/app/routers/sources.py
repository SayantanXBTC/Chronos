from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.sources_service import SourcesService

router = APIRouter()


@router.get("")
async def get_sources(db: AsyncSession = Depends(get_db)):
    svc = SourcesService(db=db)
    return await svc.get_sources()
