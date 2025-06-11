
from enum import Enum
from typing import Optional, Any, List

from sqlmodel import SQLModel, Field

class AssertCategory(str, Enum):
    """
    断言类别
    """
    STATUS_CODE = "status_code"      # 状态码断言
    RESPONSE_TIME = "response_time"  # 响应时间断言
    BODY_FIELD = "body_field"        # 响应体某字段断言
    BODY_TEXT = "body_text"          # 响应体字符串断言
    HEADER_FIELD = "header_field"    # 响应头字段断言
    COOKIES_FIELD = "cookies_field"  # Cookie字段断言

class AssertOperator(str, Enum):
    """
    操作符
    """
    EQ = "=="            # 等于
    NE = "!="            # 不等于
    GT = ">"             # 大于
    GE = ">="            # 大于等于
    LT = "<"             # 小于
    LE = "<="            # 小于等于
    CONTAINS = "contains"       # 包含（字符串或集合）
    NOT_CONTAINS = "not_contains"  # 不包含
    REGEX_MATCH = "regex_match"    # 正则匹配
    EXISTS = "exists"              # 字段存在
    NOT_EXISTS = "not_exists"      # 字段不存在
    STARTS_WITH = "starts_with"    # 字符串开头
    ENDS_WITH = "ends_with"        # 字符串结尾

class Assert(SQLModel):
    """
    断言模型
    """
    category: AssertCategory       # 断言类别
    operator: AssertOperator       # 操作符
    path: Optional[str] = None     # JSON路径，针对字段类断言
    expected: Optional[Any] = None # 预期值
    # expression: Optional[str] = None # 表达式

class AssertResult(SQLModel):
    """
    断言执行结果模型
    """
    success: bool
    message: Optional[str] = None
    details: Optional[Assert] = None




