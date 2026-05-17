from fastapi import APIRouter

router = APIRouter()


@router.get("/state")
async def get_world_state():
    return {"message": "not implemented"}


@router.get("/snapshots")
async def get_snapshots():
    return {"snapshots": []}
