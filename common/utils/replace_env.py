import json
import re
from typing import Dict, Any

from common.models.api_test import ApiTestCase


def replace_vars_in_case(case: ApiTestCase, env: Dict[str, Any]) -> ApiTestCase:
    """
    替换 ApiTestCase 中的所有 ${xxx} 变量
    :param case: 原始用例对象
    :param env: 环境变量字典
    :return: 替换后的用例对象
    """

    def replace_string(s: str) -> str:
        return re.sub(r'\$\{(\w+)\}', lambda m: str(env.get(m.group(1), m.group(0))), s)

    if not case:
        return case

    new_body = None
    if case.body:
        try:
            body_dict = json.loads(case.body)
            replaced = json.dumps(body_dict, default=lambda o: str(o))
            new_body = re.sub(r'\$\{(\w+)\}', lambda m: str(env.get(m.group(1), '')), replaced)
        except json.JSONDecodeError:
            new_body = replace_string(case.body)

    new_headers = None
    if case.headers:
        try:
            headers_dict = json.loads(case.headers)
            new_headers = {k: replace_string(v) for k, v in headers_dict.items()}
            new_headers = json.dumps(new_headers)
        except json.JSONDecodeError:
            new_headers = replace_string(case.headers)

    new_cookies = None
    if case.cookies:
        try:
            cookies_dict = json.loads(case.cookies)
            new_cookies = {k: replace_string(v) for k, v in cookies_dict.items()}
            new_cookies = json.dumps(new_cookies)
        except json.JSONDecodeError:
            new_cookies = replace_string(case.cookies)

    new_params = None
    if case.params:
        try:
            params_dict = json.loads(case.params)
            new_params = {k: replace_string(v) for k, v in params_dict.items()}
            new_params = json.dumps(new_params)
        except json.JSONDecodeError:
            new_params = replace_string(case.params)

    new_url = replace_string(case.url) if case.url else None

    # 使用 model_copy 创建新的 ApiTestCase 实例
    return case.model_copy(update={
        "body": new_body,
        "headers": new_headers,
        "url": new_url,
        "cookies": new_cookies,
        "params": new_params
    })