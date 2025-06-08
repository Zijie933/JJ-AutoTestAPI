from contextvars import ContextVar
from typing import Any, Dict, Optional

from jwt import ExpiredSignatureError, InvalidTokenError
from loguru import logger

from common.core.constants import ErrorMessages
from common.core.exceptions import TokenInvalidException
from common.core.security import parse_jwt_token


class PayloadLocal:
    """
    线程隔离存储 payload（字典）
    """
    _payload_var: ContextVar[Dict[str, Any]] = ContextVar("payload_local", default={})

    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        data = self._payload_var.get()
        return data if data else None

    @payload.setter
    def payload(self, value: Dict[str, Any]) -> None:
        self._payload_var.set(value)

    def save_by_token(self, value: str) -> None:
        try:
            payload = parse_jwt_token(value)
            logger.info(f"暂存payload为：{payload}")
        except ExpiredSignatureError:
            raise TokenInvalidException(ErrorMessages.TOKEN_EXPIRED)
        except InvalidTokenError:
            raise TokenInvalidException(ErrorMessages.TOKEN_INVALID)
        except KeyError:
            raise TokenInvalidException(ErrorMessages.MISSING_FIELD_MSG)
        self._payload_var.set(payload)

    def get(self, key: str, default: Any = None) -> Any:
        return self._payload_var.get().get(key, default)

    def clear(self) -> None:
        self._payload_var.set({})

payloadLocal = PayloadLocal()