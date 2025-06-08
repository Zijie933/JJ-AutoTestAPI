from fastapi import FastAPI
from sqlmodel import SQLModel

from app.api.endpoints import user
from common.core.config import settings
from common.db.session import engine
from common.init.middleware import init_middleware

application = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

application.include_router(user.router)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 注册拦截器
init_middleware(application)

if __name__ == "__main__":
    import uvicorn
    create_db_and_tables()
    uvicorn.run(application, host="0.0.0.0", port=9101)
