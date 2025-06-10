import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Fastapi Demo"
    APP_DESCRIPTION: str = "this is a simple demo~"
    APP_VERSION: str = "0.0.1"
    BASE_URL: str = "http://127.0.0.1:8100"
    API_PREFIX: str = ""

    WHITE_LIST: list[str] = [
        "/user/login",
        "/user/register",
        "/docs",
        "/openapi.json"
    ]

    SECRET_KEY: str = os.getenv("SECRET_KEY", "jack_default_key_1")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    MYSQL_USER: str = Field("root", env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field("123456", env="MYSQL_PASSWORD")
    MYSQL_HOST: str = Field("127.0.0.1", env="MYSQL_HOST")
    MYSQL_PORT: int = Field(3306, env="MYSQL_PORT")

    @property
    def MYSQL_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:"
            f"{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:"
            f"{self.MYSQL_PORT}/fastapi_demo_jack"
        )


    class Config:
        env_file = ".env"

settings = Settings()

if __name__ == '__main__':
    import pydantic

    print(pydantic.__version__)