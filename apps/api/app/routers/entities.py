from fastapi import APIRouter

router = APIRouter()


@router.get("/{slug}")
async def get_entity(slug: str):
    return {"slug": slug}
