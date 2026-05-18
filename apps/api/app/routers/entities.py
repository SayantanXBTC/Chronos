from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.entity_service import EntityService

router = APIRouter()


@router.get("/{slug}")
async def get_entity(slug: str, db: AsyncSession = Depends(get_db)):
    svc = EntityService(db=db)
    result = await svc.get_entity_detail(slug)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Entity '{slug}' not found")
    return result
