from fastapi import APIRouter

from app.api.endpoints import user

allRouter = APIRouter()

allRouter.include_router(router=user.router, prefix="/user", tags=["user"])