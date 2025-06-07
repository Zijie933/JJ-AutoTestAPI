class AppBaseException(Exception):
    """
    自定义异常基类
    """
    def __init__(self, message: str = "服务器处理异常", code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)

class UsernameAlreadyExistsException(AppBaseException):
    """
    用户名已存在
    """
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"用户名 '{username}' 已存在")