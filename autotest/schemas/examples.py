from common.models.api_test import ApiTestCase
from common.models.assertModel import AssertCategory, Assert, AssertOperator
from common.models.example import Example

apiTestCaseRunParamsExample = {
    "id": [None],
    "case": [
        ApiTestCase(
            method="GET",
            name="快捷测试用例",
            url="https://www.bilibili.com",
        )
    ],
    "examples": [[
        Example(
            headers='{"Content-Type": "application/json"}',
            params='{"xx参数": 933}',
            body='{"xx请求体": 933}',
            cookies='{"xxCookies": "1234567890"}',
            timeout=10,
            asserts=[
                Assert(
                    category=AssertCategory.STATUS_CODE,
                    operator=AssertOperator.EQ,
                    expected=200
                ),
                Assert(
                    category=AssertCategory.HEADER_FIELD,
                    operator=AssertOperator.EQ,
                    path="content-type",
                    expected="application/json",
                ),
                Assert(
                    category=AssertCategory.BODY_FIELD,
                    operator=AssertOperator.EQ,
                    path="data.id",
                    expected=1,
                ),
                Assert(
                    category=AssertCategory.BODY_FIELD,
                    operator=AssertOperator.EQ,
                    path="data[3].data_list[1]",
                    expected=1,
                ),
            ]
        ),
        Example(
            headers='{"Content-Type": "application/json"}',
            asserts=[
                Assert(
                    category=AssertCategory.STATUS_CODE,
                    operator=AssertOperator.GT,
                    expected=400
                ),
                Assert(
                    category=AssertCategory.COOKIES_FIELD,
                    operator=AssertOperator.NOT_EXISTS,
                    path="BAIDUID",
                ),
                Assert(
                    category=AssertCategory.HEADER_FIELD,
                    operator=AssertOperator.CONTAINS,
                    path="x-ua-compatible",
                    expected="Edge",
                ),
            ]
        ),
    ]]
}

api_test_steps_run_example = {
    "case": {
        "name": "Step运行完 获得env变量 的最终接口测试",
        "url": "http://127.0.0.1:9101/user/",
        "method": "GET",
        "headers": "{\"Authorization\":\"${token}\"}"
    },
    "steps": [
        {
            "name": "步骤1-获取token",
            "case": {
                "name": "获取token",
                "url": "http://127.0.0.1:9101/user/login",
                "method": "POST",
                "body": "{\"username\":\"JJack\",\"password\":\"1234567\"}"
            },
            "asserts": [
                {
                    "category": "body_field",
                    "operator": "==",
                    "path": "code",
                    "expected": "0"
                }
            ],
            "extract": "{\"token\":\"body.data\"}"
        },
        {
            "name": "步骤2-获取该用户信息",
            "case": {
                "name": "获取用户信息",
                "url": "http://127.0.0.1:9101/user/",
                "method": "GET",
                "headers": "{\"Authorization\":\"${token}\"}"
            },
            "asserts": [
                {
                    "category": "body_field",
                    "operator": "==",
                    "path": "code",
                    "expected": "0"
                }
            ]
        }
    ]
}
