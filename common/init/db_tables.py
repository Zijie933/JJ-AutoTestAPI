from loguru import logger
from sqlmodel import SQLModel

from common.db.session import engine, get_db
from common.models.user import User
from system.crud.user_crud import create_jjack


def init_db_and_tables():
    """
    初始化数据表与管理员
    :return:
    """
    SQLModel.metadata.create_all(engine)

    db_gen = get_db()
    try:
        db = next(db_gen)
        existing_user = db.query(User).filter(User.username == "jjack").first()
        if not existing_user:
            create_jjack(db=db)
        else:
            logger.info("管理员用户 jjack 已存在，跳过初始化")
    finally:
        next(db_gen, None)


def create_database_if_not_exists():
    from sqlalchemy import create_engine
    from sqlalchemy.exc import ProgrammingError

    db_url = str(engine.url).split("/")
    base_url = "/".join(db_url[:-1]) + "/"

    temp_engine = create_engine(base_url)
    db_name = db_url[-1]

    with temp_engine.connect() as conn:
        try:
            conn.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"数据库 `{db_name}` 已创建或已存在")
        except ProgrammingError as e:
            print(f"创建数据库失败: {e}")