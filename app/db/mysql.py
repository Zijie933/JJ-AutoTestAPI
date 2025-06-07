import os

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine


class Name(BaseModel):
    uid: str
    name: str
    jj: str

async def init_db():
    url = URL.create(
        drivername="mysql+asyncmy",
        username="root",
        password=os.getenv("MYSQL_PASSWORD"),
        host="127.0.0.1",
        port=3306,
        database="test",
    )

    engine = create_async_engine(url.render_as_string(hide_password=False), echo=True)

    async with engine.connect() as connect:
        try:
            result = await connect.execute(text("SELECT *, name as jj FROM name"))
            for row in result:
                o = Name(**row._mapping)
                print(o.dict())
        except Exception as e:
            print("数据库查询错误:", e)
