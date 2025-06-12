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
