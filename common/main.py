from fastapi import FastAPI
from sqlmodel import SQLModel

from common.init.db_tables import init_db_and_tables
from system.crud.user_crud import create_jjack
from common.init.exception_handler import init_exception_handler
from common.init.routers import init_router
from common.core.config import settings
from common.db.session import engine, get_db
from common.init.middleware import init_middleware

application = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# 注册路由
init_router(application)

# 注册中间件
init_middleware(application)

# 注册异常处理
init_exception_handler(application)

if __name__ == "__main__":
    import uvicorn
    init_db_and_tables()
    uvicorn.run(application, host="0.0.0.0", port=9101)
