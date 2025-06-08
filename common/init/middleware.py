from datetime import datetime, timezone
from fastapi import FastAPI, Request
from loguru import logger

from common.core.PayloadLocal import payloadLocal
from common.core.config import settings
from common.core.constants import ErrorMessages
from common.core.exceptions import TokenInvalidException

def init_middleware(app: FastAPI):

    """
    中间件，用于处理Token
    """

    whitelist = settings.WHITE_LIST
    @app.middleware("http")
    async def intercept(request: Request, call_next):
        try:
            path = request.url.path
            logger.info(f"请求路径：{path}")

            # 如果请求路径在白名单，跳过token校验
            if path in whitelist:
                logger.info(f"{path}在白名单，跳过Token校验")
                return await call_next(request)

            payload = payloadLocal.payload
            logger.info(f"中间件开始，当前payload：{payload}")

            if payload:
                exp = payload.get("exp")
                logger.info(f"Token过期时间戳：{exp}")
                if exp is None or exp < int(datetime.now(timezone.utc).timestamp()):
                    logger.info("Token已过期或无过期时间，清理payload缓存")
                    payloadLocal.clear()
                    payload = None

            if not payload:
                token = request.headers.get("Authorization")
                logger.info(f"请求头中的Authorization字段：{token}")
                if not token:
                    logger.error("请求头中缺少Authorization，抛出Token无效异常")
                    raise TokenInvalidException(ErrorMessages.TOKEN_INVALID)
                try:
                    payloadLocal.save_by_token(token)
                    logger.info("成功保存Token到payload缓存")
                except TokenInvalidException as e:
                    logger.error(f"Token无效异常，异常信息：{e}")
                    raise e

            response = await call_next(request)
            logger.info("中间件处理完成，继续执行后续请求")
            return response

        except Exception as e:
            logger.exception("中间件执行出现异常")
            raise e
