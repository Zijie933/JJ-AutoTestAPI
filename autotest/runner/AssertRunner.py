import json
import re
from operator import index
from typing import Any, Dict, Optional

from loguru import logger

from common.models.api_test import ApiTestResponse
from common.models.assertModel import Assert, AssertCategory, AssertOperator, AssertResult


class AssertRunner:

    @staticmethod
    def run_assert(assertion: Assert, response: ApiTestResponse, response_time: float = None) -> AssertResult:
        """
        根据断言条件和响应体进行断言检查
        """
        try:
            if assertion.category == AssertCategory.BODY_FIELD:
                value = AssertRunner.extract_field(response.get_json_response(), assertion.path)
            elif assertion.category == AssertCategory.BODY_TEXT:
                value = json.dumps(response.body, ensure_ascii=False)
            elif assertion.category == AssertCategory.STATUS_CODE:
                value = response.status_code
            elif assertion.category == AssertCategory.RESPONSE_TIME:
                value = response_time
            elif assertion.category == AssertCategory.HEADER_FIELD:
                value = response.get_header(assertion.path)
            elif assertion.category == AssertCategory.COOKIES_FIELD:
                value = response.get_cookie(assertion.path)
            else:
                return AssertResult(success=False, message=f"不支持的断言类别: {assertion.category}", details=assertion)

            result = AssertRunner.compare_values(value, assertion.operator, assertion.expected, assertion.path)
            result.message = f"[{assertion.category.value}]" + result.message
            result.details = assertion
            return result

        except ValueError as ve:
            # 路径不存在或类型错误，返回断言失败，带详细信息
            return AssertResult(success=False, message=f"断言路径错误: {ve}", details=assertion)
        except Exception as e:
            return AssertResult(success=False, message=f"断言执行异常: {e}", details=assertion)

    @staticmethod
    def compare_values(actual, operator: AssertOperator, expected, path=None) -> AssertResult:
        """
        比较实际值和预期值
        """
        try:
            if operator == AssertOperator.EQ:
                assert actual == expected, f"断言失败: 路径[{path}] 期望值为 {expected}，但实际值为 {actual}"
            elif operator == AssertOperator.NE:
                assert actual != expected, f"断言失败: 路径[{path}] 期望值不为 {expected}，但实际值为 {actual}"
            elif operator == AssertOperator.GT:
                AssertRunner._check_numeric(actual, expected)
                assert actual > expected, f"断言失败: 路径[{path}] 期望值 > {expected}，但实际值为 {actual}"
            elif operator == AssertOperator.GE:
                AssertRunner._check_numeric(actual, expected)
                assert actual >= expected, f"断言失败: 路径[{path}] 期望值 >= {expected}，但实际值为 {actual}"
            elif operator == AssertOperator.LT:
                AssertRunner._check_numeric(actual, expected)
                assert actual < expected, f"断言失败: 路径[{path}] 期望值 < {expected}，但实际值为 {actual}"
            elif operator == AssertOperator.LE:
                AssertRunner._check_numeric(actual, expected)
                assert actual <= expected, f"断言失败: 路径[{path}] 期望值 <= {expected}，但实际值为 {actual}"
            elif operator == AssertOperator.CONTAINS:
                assert isinstance(actual, (str, list, dict)), f"实际值类型 {type(actual)} 不支持包含操作"
                assert expected in actual, f"断言失败: 路径[{path}] 期望包含 '{expected}'，但实际为 '{actual}'"
            elif operator == AssertOperator.NOT_CONTAINS:
                assert isinstance(actual, (str, list, dict)), f"实际值类型 {type(actual)} 不支持不包含操作"
                assert expected not in actual, f"断言失败: 路径[{path}] 期望不包含 '{expected}'，但实际包含"
            elif operator == AssertOperator.EXISTS:
                assert expected is not None, f"断言失败: 路径[{path}] 期望存在，但实际不存在"
            elif operator == AssertOperator.NOT_EXISTS:
                assert expected is None, f"断言失败: 路径[{path}] 期望不存在，但实际存在"
            # TODO 部分断言类型待完善...
            else:
                return AssertResult(success=False, message=f"不支持的操作符: {operator}")

            return AssertResult(success=True, message="断言通过")

        except AssertionError as ae:
            return AssertResult(success=False, message=str(ae))
        except ValueError as ve:
            return AssertResult(success=False, message=f"值错误: {ve}")

    @staticmethod
    def _check_numeric(actual, expected):
        """
        检查 actual 和 expected 是否为数字类型
        """
        if not isinstance(actual, (int, float)):
            raise ValueError(f"实际值 '{actual}' 不是数字类型，无法进行数值比较")
        if not isinstance(expected, (int, float)):
            raise ValueError(f"期望值 '{expected}' 不是数字类型，无法进行数值比较")

    @staticmethod
    def extract_field(json_obj: Any, field_path: str):
        """
        提取嵌套字段的值，支持对象和列表索引访问
        """
        fields = AssertRunner._parse_fields(field_path)
        logger.debug(f"解析后的字段路径: {fields}")
        value = json_obj
        current_path = ""

        for field in fields:
            current_path = AssertRunner._build_current_path(current_path, field)

            if not isinstance(value, (dict, list)):
                raise ValueError(f"路径 '{current_path}' 对应的值不是字典或列表，无法继续提取")

            if isinstance(value, dict):
                if field not in value:
                    raise ValueError(f"路径 '{current_path}' 在响应中不存在")
            elif isinstance(value, list):
                if not isinstance(field, int) or not (0 <= field < len(value)):
                    raise IndexError(f"路径 '{current_path}' 列表索引超出范围，长度为 {len(value)}")

            value = value[field]

        if value is None:
            raise ValueError(f"路径 '{field_path}' 存在，但对应值为 None")

        return value

    @staticmethod
    def _parse_fields(path: str) -> list:
        """将路径拆分为字段列表，并处理数组索引"""
        parts = re.split(r'(?=\[)|(?<=\])', path)
        fields = []
        for part in parts:
            if not part:
                continue
            if part.startswith("[") and part.endswith("]"):
                index_str = part[1:-1]
                if not index_str.isdigit():
                    raise ValueError(f"非法索引: '{index_str}' 不是整数")
                fields.append(int(index_str))
            else:
                sub_parts = part.split(".")
                for sp in sub_parts:
                    if sp:
                        fields.append(sp)
        return fields

    @staticmethod
    def _build_current_path(current: str, field: Any) -> str:
        """构建当前字段路径，用于错误提示"""
        if isinstance(field, int):
            return f"{current}[{field}]" if current else f"[{field}]"
        return f"{current}.{field}" if current else field



