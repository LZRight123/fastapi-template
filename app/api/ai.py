

from fastapi import APIRouter

from app.models.response import RespModel


router = APIRouter()

@router.get("/")
async def ai():
    return RespModel(
        data={
            "message": "Hello AI"
        }
    )
