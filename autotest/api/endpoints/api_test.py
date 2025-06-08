from fastapi import APIRouter

from app.api.deps import SessionDep
from common.schemas.response import Response

router = APIRouter()

# 上传测试接口
# @router.post("/", response_model=Response, description="上传测试接口")
# async def save_or_update(*, db: SessionDep, test_in: ApiTestCreate):