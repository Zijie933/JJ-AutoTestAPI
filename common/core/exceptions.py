from common.core.constants import ErrorMessages


class AppBaseException(Exception):
    """
    自定义异常基类
    """
    def __init__(self, message: str = "服务器处理异常", code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)

class MissingFieldException(AppBaseException):
    """
    缺少字段异常
    """
    def __init__(self, message: str = ErrorMessages.MISSING_FIELD_MSG):
        super().__init__(message)

class DatabaseException(AppBaseException):
    """
    数据库操作异常
    """
    def __init__(self, message: str = ErrorMessages.DATABASE_ERROR):
        super().__init__(message)

class UsernameAlreadyExistsException(AppBaseException):
    """
    用户名已存在
    """
    def __init__(self, message: str = ErrorMessages.USER_ALREADY_EXIST):
        super().__init__(message)

class UsernameNotExistsException(AppBaseException):
    """
    用户名不存在
    """
    def __init__(self, message: str = ErrorMessages.USER_ALREADY_EXIST):
        super().__init__(message)

class PasswordIncorrectException(AppBaseException):
    """
    密码错误
    """
    def __init__(self, message: str = ErrorMessages.PASSWORD_INCORRECT):
        super().__init__(message)

class TokenInvalidException(AppBaseException):
    """
    token 无效
    """
    def __init__(self, message: str = ErrorMessages.TOKEN_INVALID):
        super().__init__(message)


