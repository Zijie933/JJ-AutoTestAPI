# JJ-AutoTestAPI

本后端项目集成了一套自动化测试框架，位于 `autotest` 目录下。以下将详细说明其测试流程。

## 自动化测试流程

自动化测试主要围绕API接口进行，支持单个API测试和多步骤的场景测试。核心流程如下：

### 1. 测试用例定义 (Test Case Definition)

*   **API测试用例 (`ApiTestCase`)**: 定义单个API请求的详细信息，包括：
    *   `name`: 用例名称
    *   `url`: 请求URL
    *   `method`: 请求方法 (GET, POST, PUT, DELETE等)
    *   `headers`: 请求头 (JSON字符串)
    *   `params`: URL查询参数 (JSON字符串)
    *   `body`: 请求体 (根据`Content-Type`，可以是JSON字符串、表单数据等)
    *   `cookies`: 请求Cookie (JSON字符串)
    *   这些用例可以通过CRUD操作进行管理（参考 <mcsymbol name="save_api_test" filename="api_test_crud.py" path="autotest/crud/api_test_crud.py" startline="5" type="function"></mcsymbol>, <mcsymbol name="update_api_test" filename="api_test_crud.py" path="autotest/crud/api_test_crud.py" startline="22" type="function"></mcsymbol>）。

*   **测试数据/示例 (`Example`)**: 为一个API测试用例提供多组不同的输入数据和预期断言。每个`Example`包含：
    *   `headers`, `params`, `body`, `cookies`: 覆盖或补充`ApiTestCase`中的对应字段。
    *   `timeout`: 单个请求的超时时间。
    *   `asserts`: 一个断言列表，用于验证响应的正确性。

*   **步骤 (`StepInput` / `Step`)**: 用于定义多步骤的场景测试。每个步骤包含：
    *   `name`: 步骤名称。
    *   `case`: 一个完整的`ApiTestCase`定义，作为此步骤要执行的API请求。
    *   `asserts`: 针对此步骤响应的断言列表。
    *   `extract`: (JSON字符串) 定义如何从当前步骤的响应中提取数据，并将其存入环境变量，供后续步骤使用。例如：`{"token": "body.data.access_token"}`。

### 2. 测试执行 (Test Execution)

测试执行分为两种主要模式：单个API测试和步骤化场景测试。

#### a. 单个API测试执行

1.  **初始化**: 通过 <mcsymbol name="ApiTestService.init" filename="ApiTestService.py" path="autotest/service/ApiTestService.py" startline="17" type="function"></mcsymbol> (针对 <mcsymbol name="ApiTestCaseRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="25" type="class"></mcsymbol>)，加载测试用例 (`ApiTestCase`) 和对应的测试数据 (`examples`)，组装成 <mcsymbol name="ApiTestCaseRunModel" filename="api_test.py" path="common/models/api_test.py" startline="30" type="class"></mcsymbol>。
2.  **运行**: <mcsymbol name="ApiTestRunner" filename="ApiTestRunner.py" path="autotest/runner/ApiTestRunner.py" startline="13" type="class"></mcsymbol> 负责执行。
    *   如果提供了多个`Example`，<mcsymbol name="ApiTestRunner.run_concurrent_tests" filename="ApiTestRunner.py" path="autotest/runner/ApiTestRunner.py" startline="22" type="function"></mcsymbol> 会并发执行这些`Example`（最大并发数可配置）。
    *   对于每个`Example`，<mcsymbol name="ApiTestRunner.run_single_test" filename="ApiTestRunner.py" path="autotest/runner/ApiTestRunner.py" startline="40" type="function"></mcsymbol> 会：
        *   使用`httpx.AsyncClient`构建并发送HTTP请求。
        *   接收响应，并将其封装为 <mcsymbol name="ApiTestResponse" filename="api_test.py" path="common/models/api_test.py" startline="15" type="class"></mcsymbol>。
3.  **断言处理**: <mcsymbol name="AssertRunner" filename="AssertRunner.py" path="autotest/runner/AssertRunner.py" startline="11" type="class"></mcsymbol> 负责处理断言。
    *   <mcsymbol name="AssertRunner.run_assert" filename="AssertRunner.py" path="autotest/runner/AssertRunner.py" startline="13" type="function"></mcsymbol> 遍历`Example`中定义的每个`Assert`。
    *   根据断言类别 (`AssertCategory`: STATUS_CODE, HEADER_FIELD, BODY_FIELD, COOKIES_FIELD, ENV等)，从响应或环境变量中提取实际值 (<mcsymbol name="AssertRunner.extract_field" filename="AssertRunner.py" path="autotest/runner/AssertRunner.py" startline="100" type="function"></mcsymbol> 支持JSON路径提取，如 `data.items[0].name`)。
    *   使用 <mcsymbol name="AssertRunner.compare_values" filename="AssertRunner.py" path="autotest/runner/AssertRunner.py" startline="47" type="function"></mcsymbol> 根据断言操作符 (`AssertOperator`: EQ, NE, GT, CONTAINS等) 比较实际值与期望值。
    *   生成断言结果 <mcsymbol name="AssertResult" filename="assertModel.py" path="common/models/assertModel.py" startline="29" type="class"></mcsymbol>。
4.  **结果返回**: 最终返回 <mcsymbol name="ApiTestCaseRunResponse" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="44" type="class"></mcsymbol>，包含原始用例信息和每个`Example`的运行结果 (<mcsymbol name="ApiRunnerResult" filename="api_test.py" path="common/models/api_test.py" startline="40" type="class"></mcsymbol>)。

#### b. 步骤化场景测试执行

1.  **初始化**: 通过 <mcsymbol name="ApiTestService.init" filename="ApiTestService.py" path="autotest/service/ApiTestService.py" startline="34" type="function"></mcsymbol> (针对 <mcsymbol name="ApiTestStepsRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="36" type="class"></mcsymbol>)，加载基础用例信息、测试数据、步骤列表 (`steps`) 和初始环境变量 (`env`)，组装成 <mcsymbol name="StepRunModel" filename="step.py" path="common/models/step.py" startline="24" type="class"></mcsymbol>。
    *   <mcsymbol name="convert_step_inputs_to_steps" filename="step.py" path="common/utils/step.py" startline="16" type="function"></mcsymbol> 将输入的 <mcsymbol name="StepInput" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="30" type="class"></mcsymbol> 转换为内部的 <mcsymbol name="Step" filename="step.py" path="common/models/step.py" startline="9" type="class"></mcsymbol> 模型。
2.  **步骤运行**: <mcsymbol name="StepRunner" filename="StepRunner.py" path="autotest/runner/StepRunner.py" startline="17" type="class"></mcsymbol> 负责按顺序执行步骤列表 (<mcsymbol name="StepRunner.run" filename="StepRunner.py" path="autotest/runner/StepRunner.py" startline="26" type="function"></mcsymbol> -> <mcsymbol name="StepRunner.run_steps" filename="StepRunner.py" path="autotest/runner/StepRunner.py" startline="41" type="function"></mcsymbol>)。
    *   **环境变量替换**: 在执行每个步骤之前，<mcsymbol name="StepRunner._replace_step_vars" filename="StepRunner.py" path="autotest/runner/StepRunner.py" startline="63" type="function"></mcsymbol> 会使用当前累积的环境变量替换步骤中用例定义的占位符 (通过 <mcsymbol name="replace_vars_in_case" filename="replace_env.py" path="common/utils/replace_env.py" startline="6" type="function"></mcsymbol>)。
    *   **单步骤执行 (`_run_single_step`)**: 每个步骤本质上是执行一个API测试用例。它会创建一个临时的 <mcsymbol name="ApiTestRunner" filename="ApiTestRunner.py" path="autotest/runner/ApiTestRunner.py" startline="13" type="class"></mcsymbol> 来发送请求并获取响应。
    *   **步骤断言**: 如果步骤定义了`asserts`，则使用 <mcsymbol name="AssertRunner" filename="AssertRunner.py" path="autotest/runner/AssertRunner.py" startline="11" type="class"></mcsymbol> 对当前步骤的响应进行断言。如果任何断言失败，整个场景测试会提前终止。
    *   **变量提取 (`_extract_vars`)**: 如果步骤断言成功且定义了`extract`规则，<mcsymbol name="StepRunner._extract_vars" filename="StepRunner.py" path="autotest/runner/StepRunner.py" startline="99" type="function"></mcsymbol> 会从响应的`body`, `headers`, 或 `cookies`中提取指定路径的值，并更新到环境变量中，供后续步骤使用。
3.  **最终用例执行 (可选)**: 在所有步骤成功执行后，<mcsymbol name="ApiTestService.run_steps" filename="ApiTestService.py" path="autotest/service/ApiTestService.py" startline="72" type="function"></mcsymbol> 会使用最终的环境变量再次替换原始`ApiTestCaseRunParams`中的`case`和`examples`中的占位符，然后像单个API测试一样执行这个最终的用例。
4.  **结果返回**: 最终返回 <mcsymbol name="StepRunResponse" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="53" type="class"></mcsymbol>，包含最终用例的运行结果、步骤的运行成功状态、消息、每个步骤的详细结果 (<mcsymbol name="SingleStepRunnerResult" filename="step.py" path="common/models/step.py" startline="16" type="class"></mcsymbol>)以及最终的环境变量。

### 3. API端点

*   **运行单个/批量API测试**: `POST /autotest/run` (接收 <mcsymbol name="ApiTestCaseRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="25" type="class"></mcsymbol>)
    *   对应处理函数: <mcsymbol name="run_api_test" filename="api_test.py" path="autotest/api/endpoints/api_test.py" startline="60" type="function"></mcsymbol>
*   **运行步骤化/多依赖场景测试**: `POST /autotest/run_steps` (接收 <mcsymbol name="ApiTestStepsRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="36" type="class"></mcsymbol>)
    *   对应处理函数: <mcsymbol name="run_api_test_steps" filename="api_test.py" path="autotest/api/endpoints/api_test.py" startline="67" type="function"></mcsymbol>

### 核心组件

*   **Runners** (<mcfolder name="runner" path="autotest/runner"></mcfolder>):
    *   <mcsymbol name="ApiTestRunner" filename="ApiTestRunner.py" path="autotest/runner/ApiTestRunner.py" startline="13" type="class"></mcsymbol>: 负责单个API请求的发送和初步结果处理。
    *   <mcsymbol name="StepRunner" filename="StepRunner.py" path="autotest/runner/StepRunner.py" startline="17" type="class"></mcsymbol>: 负责编排和执行一系列测试步骤，管理环境变量的传递。
    *   <mcsymbol name="AssertRunner" filename="AssertRunner.py" path="autotest/runner/AssertRunner.py" startline="11" type="class"></mcsymbol>: 负责执行断言逻辑，比较实际结果与预期结果。
*   **Schemas** (<mcfolder name="schemas" path="autotest/schemas"></mcfolder>): 定义了API接口的请求体、响应体以及测试用例相关的数据结构 (Pydantic/SQLModel模型)。
    *   <mcsymbol name="api_test_schemas.py" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py"></mcsymbol>: 包含如 <mcsymbol name="ApiTestCaseCreate" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="11" type="class"></mcsymbol>, <mcsymbol name="ApiTestCaseUpdate" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="19" type="class"></mcsymbol>, <mcsymbol name="ApiTestCaseRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="25" type="class"></mcsymbol>, <mcsymbol name="ApiTestStepsRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="36" type="class"></mcsymbol> 等。
    *   <mcsymbol name="examples.py" filename="examples.py" path="autotest/schemas/examples.py"></mcsymbol>: 提供了一些请求体的示例数据。
*   **CRUD** (<mcfolder name="crud" path="autotest/crud"></mcfolder>):
    *   <mcsymbol name="api_test_crud.py" filename="api_test_crud.py" path="autotest/crud/api_test_crud.py"></mcsymbol>: 提供了测试用例的数据库增删改查操作。
*   **Service** (<mcfolder name="service" path="autotest/service"></mcfolder>):
    *   <mcsymbol name="ApiTestService.py" filename="ApiTestService.py" path="autotest/service/ApiTestService.py"></mcsymbol>: 业务逻辑层，协调Runner和CRUD操作，处理API请求。
*   **Models** (<mcfolder name="models" path="common/models"></mcfolder>): 定义了核心数据模型，如 <mcsymbol name="ApiTestCase" filename="api_test.py" path="common/models/api_test.py" startline="7" type="class"></mcsymbol>, <mcsymbol name="Assert" filename="assertModel.py" path="common/models/assertModel.py" startline="15" type="class"></mcsymbol>, <mcsymbol name="Example" filename="example.py" path="common/models/example.py" startline="6" type="class"></mcsymbol>, <mcsymbol name="Step" filename="step.py" path="common/models/step.py" startline="9" type="class"></mcsymbol>。
*   **Utils** (<mcfolder name="utils" path="common/utils"></mcfolder>):
    *   <mcsymbol name="replace_env.py" filename="replace_env.py" path="common/utils/replace_env.py"></mcsymbol>: 提供环境变量替换功能。
    *   <mcsymbol name="step.py" filename="step.py" path="common/utils/step.py"></mcsymbol>: 提供步骤相关的转换函数。

## 如何运行测试

1.  **准备测试用例**: 可以通过API创建和管理测试用例，或者在请求时直接提供用例详情。
2.  **发送请求**: 
    *   对于单个API测试，向 `POST /autotest/run` 发送请求，请求体为 <mcsymbol name="ApiTestCaseRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="25" type="class"></mcsymbol> 结构。
    *   对于场景测试，向 `POST /autotest/run_steps` 发送请求，请求体为 <mcsymbol name="ApiTestStepsRunParams" filename="api_test_schemas.py" path="autotest/schemas/api_test_schemas.py" startline="36" type="class"></mcsymbol> 结构。
3.  **查看结果**: API会返回详细的测试结果，包括每个断言的成功与否，以及提取的变量（如果适用）。

这个自动化测试框架提供了一个强大而灵活的方式来验证API的正确性和业务流程的连贯性。