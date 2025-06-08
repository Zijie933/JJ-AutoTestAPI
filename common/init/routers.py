from fastapi import FastAPI

from common.router.router import allRouter
from common.core.config import settings

def init_router(app: FastAPI):
    """ 注册路由 """
    app.include_router(allRouter, prefix=settings.API_PREFIX)