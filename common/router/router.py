from fastapi import APIRouter

from autotest.api.endpoints import api_test
from system.api.endpoints import user

allRouter = APIRouter()

allRouter.include_router(router=user.router, prefix="/user", tags=["user"])
allRouter.include_router(router=api_test.router, prefix="/autotest", tags=["autotest"])