<template>
  <div class="api-test-runner">
    <el-button type="primary" @click="runQuickTest">快捷测试</el-button>
    <el-button type="success" @click="showExampleRunDialog = true">快捷用例测试（含Examples）</el-button>
    <el-button type="warning" @click="showMultiVarTestDialog = true">多变量依赖测试</el-button> <!-- Added this button -->

    <el-dialog v-model="runTestModalVisible" title="执行API测试用例" width="60%" @closed="resetRunModal">
      <el-form :model="runForm" label-width="120px">
        <el-form-item label="选择用例">
          <el-select v-model="runForm.selectedCaseId" placeholder="请选择一个API用例" filterable style="width: 100%;">
            <el-option
              v-for="item in availableApiCases"
              :key="item.id"
              :label="`${item.name} (${item.method} - ${item.url})`"
              :value="item.id"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <div v-if="executionResult" class="result-display">
        <h4>执行结果:</h4>
        <div class="json-output" v-html="formattedJsonResult"></div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="runTestModalVisible = false">取消</el-button>
          <el-button type="primary" @click="() => executeTestCase()" :loading="isExecuting">
            执行测试
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- New Dialog for running with Examples -->
    <el-dialog v-model="showExampleRunDialog" title="快捷用例测试（含Examples）" width="60%" @closed="resetExampleRunModal">
      <el-form label-width="120px">
        <el-form-item label="测试名称">
          <el-input v-model="quickTestName" placeholder="可选，不填则自动生成"></el-input>
        </el-form-item>
        <el-form-item label="选择基础用例">
          <el-select v-model="selectedBaseCaseId" placeholder="必选，用于填充默认值" filterable required>
            <el-option
              v-for="item in availableApiCases"
              :key="item.id"
              :label="`${item.name} (${item.method} - ${item.url})`"
              :value="item.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Examples JSON">
          <el-input
            type="textarea"
            v-model="examplesJson"
            :rows="10"
            placeholder="输入Examples的JSON数组"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="openNewExampleDialog">修改 Example</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showExampleRunDialog = false">取消</el-button>
          <el-button type="info" @click="() => saveExampleRunConfiguration()">保存配置</el-button>
          <el-button type="primary" @click="() => submitExampleRun()" :loading="exampleRunLoading">
            执行用例
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- New Dialog for creating a single Example -->
    <el-dialog v-model="showNewExampleDialog" title="新建 Example" width="50%">
      <el-form :model="newExampleForm" label-width="120px">
        <el-form-item label="Headers">
          <el-input v-model="newExampleForm.headers" placeholder="JSON 格式的请求头"></el-input>
        </el-form-item>
        <el-form-item label="Params">
          <el-input v-model="newExampleForm.params" placeholder="JSON 格式的 Query 参数"></el-input>
        </el-form-item>
        <el-form-item label="Body">
          <el-input type="textarea" v-model="newExampleForm.body" :rows="4" placeholder="JSON 格式的请求体"></el-input>
        </el-form-item>
        <el-form-item label="Cookies">
          <el-input v-model="newExampleForm.cookies" placeholder="JSON 格式的请求 Cookies"></el-input>
        </el-form-item>
        <el-form-item label="Timeout">
          <el-input-number v-model="newExampleForm.timeout" :min="1" :max="60"></el-input-number>
        </el-form-item>

        <h4>断言 (Asserts)</h4>
        <el-button type="primary" @click="addAssert">添加断言</el-button>
        <div v-for="(assert, index) in newExampleForm.asserts" :key="index" style="margin-top: 10px; border: 1px solid #eee; padding: 10px;">
          <el-form-item label="Category">
            <el-select v-model="assert.category" placeholder="选择断言类别">
              <el-option v-for="category in Object.values(AssertCategory)" :key="category" :label="AssertCategoryMap[category]" :value="category"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Operator">
            <el-select v-model="assert.operator" placeholder="选择操作符">
              <el-option v-for="operator in Object.values(AssertOperator)" :key="operator" :label="AssertOperatorMap[operator]" :value="operator"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="Path">
            <el-input v-model="assert.path" placeholder="断言路径 (如 data.name)"></el-input>
          </el-form-item>
          <el-form-item label="Expected">
            <el-input v-model="assert.expected" placeholder="期望值"></el-input>
          </el-form-item>
          <el-button type="danger" @click="removeAssert(index)">删除断言</el-button>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showNewExampleDialog = false">取消</el-button>
          <el-button type="primary" @click="addNewExample">修改 Examples JSON</el-button>
        </span>
      </template>
    </el-dialog>

    <div class="test-history">
      <h4>测试列表</h4>
      <el-table :data="testHistory" style="width: 100%">
        <el-table-column prop="caseName" label="测试名称/用例名称" min-width="180"></el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.timestamp).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.type === 'singleCase'">单用例</el-tag>
            <el-tag v-else-if="scope.row.type === 'exampleRun'" type="success">快捷用例</el-tag>
            <el-tag v-else-if="scope.row.type === 'exampleConfigSave'" type="info">保存配置</el-tag>
            <span v-else>未知</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="230">
          <template #default="scope">
            <el-button size="small" @click="viewResult(scope.row)" :disabled="!scope.row.result">查看结果</el-button>
            <el-button size="small" type="success" @click="viewTestReport(scope.row)" :disabled="!scope.row.result">查看报告</el-button>            
            <el-button size="small" type="primary" @click="editAndRerun(scope.row, scope.$index)">修改并执行/配置</el-button>
            <el-button size="small" type="danger" @click="deleteHistory(scope.$index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showResultDialog" title="执行结果" width="60%">
      <div v-if="currentResultForDialog" class="json-display">
        <pre v-html="renderJsonResult(currentResultForDialog.result)"></pre>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showResultDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="showTestReportDialog" title="测试报告" width="70%" top="5vh">
      <div v-if="currentTestReportForDialog" class="test-report-display" style="max-height: 70vh; overflow-y: auto;">
        <pre v-html="currentTestReportForDialog"></pre>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTestReportDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Added Dialog for Multi-variable Step Test START -->
    <el-dialog v-model="showMultiVarTestDialog" title="多变量依赖测试" width="70%" @closed="resetMultiVarTestDialog">
      <el-form :model="multiVarForm" label-width="120px">
        <el-tabs v-model="activeTabInMultiVarDialog">
          <el-tab-pane label="快捷用例详情" name="caseDetails">
            <el-form-item label="选择用例 (ID)">
              <el-select 
                v-model="selectedCaseId" 
                placeholder="可选，选择一个已存在的API用例" 
                filterable 
                clearable
                style="width: 100%;"
                @change="handleMultiVarBaseCaseChange"
              >
                <el-option
                  v-for="item in availableApiCases"
                  :key="item.id"
                  :label="`${item.name} (${item.method} - ${item.url})`"
                  :value="item.id"
                ></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="用例名称">
              <el-input v-model="multiVarForm.caseDetail.name" placeholder="必填"></el-input>
            </el-form-item>
            <el-form-item label="请求URL">
              <el-input v-model="multiVarForm.caseDetail.url" placeholder="可选，若不填用例ID则必填"></el-input>
            </el-form-item>
            <el-form-item label="请求方法">
              <el-select v-model="multiVarForm.caseDetail.method" placeholder="可选，若不填用例ID则必填" style="width: 100%;">
                <el-option label="GET" value="GET"></el-option>
                <el-option label="POST" value="POST"></el-option>
                <el-option label="PUT" value="PUT"></el-option>
                <el-option label="DELETE" value="DELETE"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="请求头 (JSON)">
              <el-input type="textarea" :rows="3" v-model="multiVarForm.caseDetail.headers" placeholder="可选，请输入 JSON 对象字符串"></el-input>
            </el-form-item>
            <el-form-item label="Query参数 (JSON)">
              <el-input type="textarea" :rows="3" v-model="multiVarForm.caseDetail.params" placeholder="可选，请输入 JSON 对象字符串"></el-input>
            </el-form-item>
            <el-form-item label="请求体 (JSON)">
              <el-input type="textarea" :rows="5" v-model="multiVarForm.caseDetail.body" placeholder="可选，请输入 JSON 对象字符串"></el-input>
            </el-form-item>
            <el-form-item label="Cookies (JSON)">
              <el-input type="textarea" :rows="2" v-model="multiVarForm.caseDetail.cookies" placeholder="可选，请输入 JSON 对象字符串"></el-input>
            </el-form-item>
            <div style="margin-top: 10px; color: #909399; font-size: 12px;">
              提示：用例ID对应数据库中已存在的用例。若不填写用例ID，则需要手动填写请求URL和请求方法等信息来定义一个临时用例。
            </div>
          </el-tab-pane>
          <el-tab-pane label="环境变量与步骤" name="envAndSteps">
            <el-form-item label="环境变量 (JSON)">
              <el-input type="textarea" v-model="multiVarForm.envJson" :rows="3" placeholder="可选，请输入环境变量，格式为 JSON 对象"></el-input>
            </el-form-item>

            <h4>测试步骤</h4>
            <div v-for="(step, index) in multiVarForm.steps" :key="index" class="step-item-dialog" style="margin-bottom: 20px; border: 1px solid #ebeef5; padding: 15px; border-radius: 4px;">
              <el-card shadow="never">
                <template #header>
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>步骤 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeMultiVarStep(index)">删除步骤</el-button>
                  </div>
                </template>
                <el-form-item :label="`步骤 ${index + 1} 名称`">
                  <el-input v-model="step.name" placeholder="步骤名称"></el-input>
                </el-form-item>
                <el-form-item :label="`请求方法`">
                  <el-select v-model="step.method" placeholder="选择请求方法" style="width: 100%;">
                    <el-option label="GET" value="GET"></el-option>
                    <el-option label="POST" value="POST"></el-option>
                    <el-option label="PUT" value="PUT"></el-option>
                    <el-option label="DELETE" value="DELETE"></el-option>
                    <el-option label="PATCH" value="PATCH"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item :label="`请求URL`">
                  <el-input v-model="step.url" placeholder="请输入请求URL"></el-input>
                </el-form-item>
                <el-form-item :label="`请求头 (JSON)`">
                  <el-input type="textarea" v-model="step.headersJson" placeholder="请输入请求头，格式为 JSON 对象"></el-input>
                </el-form-item>
                <el-form-item :label="`请求体 (JSON)`">
                  <el-input type="textarea" v-model="step.bodyJson" placeholder="请输入请求体，格式为 JSON 对象"></el-input>
                </el-form-item>
                <el-form-item :label="`提取变量 (JSON)`">
                  <el-input type="textarea" v-model="step.extractJson" placeholder="请输入提取规则，格式为 JSON 对象，例如 {'token': 'data.accessToken'}"></el-input>
                </el-form-item>
                <el-form-item :label="`断言 (JSON)`">
                  <el-input type="textarea" v-model="step.assertsJson" placeholder="请输入断言规则，格式为 JSON 数组"></el-input>
                </el-form-item>
              </el-card>
            </div>
            <el-button type="success" @click="addMultiVarStep" style="margin-top: 10px;">添加步骤</el-button>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <div v-if="multiVarTestResult" class="result-display" style="margin-top: 20px; padding: 15px; border: 1px solid #ebeef5; border-radius: 4px; background-color: #f5f7fa;">
        <h4>执行结果:</h4>
        <pre style="white-space: pre-wrap; word-wrap: break-word;">{{ multiVarTestResult }}</pre>
      </div>
      <div v-if="multiVarErrorInfo" class="error-display" style="margin-top: 20px; padding: 15px; border: 1px solid #f56c6c; border-radius: 4px; color: #f56c6c; background-color: #fef0f0;">
        <h4>错误信息:</h4>
        <pre style="white-space: pre-wrap; word-wrap: break-word;">{{ multiVarErrorInfo }}</pre>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showMultiVarTestDialog = false">取消</el-button>
          <el-button type="primary" @click="handleRunMultiVarSteps" :loading="isLoadingMultiVar">
            执行测试
          </el-button>
        </span>
      </template>
    </el-dialog>
    <!-- Added Dialog for Multi-variable Step Test END -->

  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch, reactive } from 'vue';
import { ElMessage, ElButton, ElDialog, ElForm, ElFormItem, ElSelect, ElOption, ElCard, ElInput, ElInputNumber, ElTabs, ElTabPane } from 'element-plus'; // Added ElTabs, ElTabPane
import { getAllApiCases, type ApiCase, ApiTestCaseRunPayload, Example, AssertCategory, AssertOperator, Assert, runApiTestSteps, type ApiTestStepsRunParams, type StepInput, type StepRunResponse, type ApiTestCaseData } from '@/api/autotest'; // Added runApiTestSteps and related types
import apiClient from '@/api'; // Or your specific API client if different
import { runApiTestCase as actualRunApiTestCase } from '@/api/autotest';
import type { FormInstance } from 'element-plus';

// Multi-variable Step Test related reactive variables
const showMultiVarTestDialog = ref(false);
const isLoadingMultiVar = ref(false);
const multiVarTestResult = ref<StepRunResponse[] | null>(null);
const multiVarErrorInfo = ref<string | null>(null);
const activeTabInMultiVarDialog = ref('caseDetails'); // Added this line

interface FormStepInput {
  name: string;
  method: string;
  url: string;
  headersJson?: string;
  bodyJson?: string;
  extractJson?: string;
  assertsJson?: string;
}

// Define a type for the caseDetail part of the form
interface MultiVarCaseDetailForm {
  id?: number | null; // Allow null for empty input, convert to undefined or handle in logic
  name: string;
  url: string;
  method: string;
  headers?: string; // JSON string
  params?: string;  // JSON string
  body?: string;    // JSON string
  cookies?: string; // JSON string
}

const multiVarForm = reactive<{
  caseDetail: MultiVarCaseDetailForm;
  envJson: string;
  steps: FormStepInput[];
}> ({
  caseDetail: {
    id: undefined,
    name: '',
    url: '',
    method: 'GET',
    headers: '{}',
    params: '{}',
    body: '{}',
    cookies: '{}',
  },
  envJson: '',
  steps: [],
});

const selectedCaseId = computed({
  get: () => multiVarForm.caseDetail.id === null ? undefined : multiVarForm.caseDetail.id,
  set: (val) => {
    multiVarForm.caseDetail.id = val === null ? undefined : val;
  }
});

const resetMultiVarTestDialog = () => {
  multiVarForm.caseDetail = {
    id: null,
    name: '',
    url: '',
    method: 'GET',
    headers: '{}',
    params: '{}',
    body: '{}',
    cookies: '{}',
  };
  multiVarForm.envJson = '';
  multiVarForm.steps = [];
  multiVarTestResult.value = null;
  multiVarErrorInfo.value = null;
  isLoadingMultiVar.value = false;
  activeTabInMultiVarDialog.value = 'caseDetails'; // Reset active tab
};

const handleMultiVarBaseCaseChange = (selectedId: number | null | undefined) => {
  if (selectedId) {
    const selectedCase = availableApiCases.value.find(c => c.id === selectedId);
    if (selectedCase) {
      // Only fill if the corresponding field in multiVarForm.caseDetail is empty or default
      if (!multiVarForm.caseDetail.name) {
        multiVarForm.caseDetail.name = selectedCase.name;
      }
      if (!multiVarForm.caseDetail.url) {
        multiVarForm.caseDetail.url = selectedCase.url;
      }
      if (multiVarForm.caseDetail.method === 'GET' || !multiVarForm.caseDetail.method) { // Assuming GET is default
        multiVarForm.caseDetail.method = selectedCase.method;
      }
      if (multiVarForm.caseDetail.headers === '{}' || !multiVarForm.caseDetail.headers) {
        multiVarForm.caseDetail.headers = typeof selectedCase.headers === 'object' ? JSON.stringify(selectedCase.headers) : selectedCase.headers || '{}';
      }
      if (multiVarForm.caseDetail.params === '{}' || !multiVarForm.caseDetail.params) {
        multiVarForm.caseDetail.params = typeof selectedCase.params === 'object' ? JSON.stringify(selectedCase.params) : selectedCase.params || '{}';
      }
      if (multiVarForm.caseDetail.body === '{}' || !multiVarForm.caseDetail.body) {
        multiVarForm.caseDetail.body = typeof selectedCase.body === 'object' ? JSON.stringify(selectedCase.body) : selectedCase.body || '{}';
      }
      if (multiVarForm.caseDetail.cookies === '{}' || !multiVarForm.caseDetail.cookies) {
        multiVarForm.caseDetail.cookies = typeof selectedCase.cookies === 'object' ? JSON.stringify(selectedCase.cookies) : selectedCase.cookies || '{}';
      }
    }
  } else {
    // If cleared, reset relevant fields if they were potentially auto-filled, or leave as is for manual input
    // For now, let's not auto-clear, user can manually clear if needed or rely on placeholder text
  }
};

const addMultiVarStep = () => {
  multiVarForm.steps.push({
    name: `Step ${multiVarForm.steps.length + 1}`,
    method: 'GET', // Default method
    url: '',      // Default empty URL
    headersJson: '{}',
    bodyJson: '{}',
    extractJson: '{}',
    assertsJson: '[]'
  });
};

const removeMultiVarStep = (index: number) => {
  multiVarForm.steps.splice(index, 1);
};

const handleRunMultiVarSteps = async () => {
  isLoadingMultiVar.value = true;
  multiVarTestResult.value = null;
  multiVarErrorInfo.value = null;

  // Validation: If caseDetail.id is not provided, then name, url, and method are required for the ad-hoc case.
  if (!multiVarForm.caseDetail.id && (!multiVarForm.caseDetail.name || !multiVarForm.caseDetail.url || !multiVarForm.caseDetail.method)) {
    multiVarErrorInfo.value = '未提供用例ID时，用例名称、请求URL和请求方法为必填项。';
    isLoadingMultiVar.value = false;
    ElMessage.error(multiVarErrorInfo.value);
    return;
  }

  let stepsInput: StepInput[];
  try {
    stepsInput = multiVarForm.steps.map(s => {
      const step: StepInput = {
        name: s.name,
        case: {
          name: s.name, 
          method: s.method,
          url: s.url,
          headers: s.headersJson && s.headersJson.trim() !== '' && s.headersJson.trim() !== '{}' ? s.headersJson : undefined, 
          body: s.bodyJson && s.bodyJson.trim() !== '' && s.bodyJson.trim() !== '{}' ? s.bodyJson : undefined, 
        }
      };
      // Only parse if extractJson is not empty or just whitespace
      if (s.extractJson && s.extractJson.trim() !== '' && s.extractJson.trim() !== '{}') {
        step.extract = JSON.parse(s.extractJson);
      } else {
        step.extract = {}; // Default to empty object if no valid JSON
      }
      // Only parse if assertsJson is not empty or just whitespace
      if (s.assertsJson && s.assertsJson.trim() !== '' && s.assertsJson.trim() !== '[]') {
        step.asserts = JSON.parse(s.assertsJson);
      } else {
        step.asserts = []; // Default to empty array if no valid JSON
      }
      return step;
    });
  } catch (e: any) {
    const stepWithError = multiVarForm.steps.find(s => {
        try { 
            // Only parse extractJson and assertsJson here as headersJson/bodyJson are passed as strings
            if(s.extractJson) JSON.parse(s.extractJson); 
            if(s.assertsJson) JSON.parse(s.assertsJson); 
            return false; 
        } catch { return true; }
    });
    const stepName = stepWithError ? stepWithError.name : '未知步骤';
    multiVarErrorInfo.value = `步骤 "${stepName}" 的提取或断言JSON解析错误: ${e.message}`;
    isLoadingMultiVar.value = false;
    ElMessage.error(multiVarErrorInfo.value);
    return;
  }

  const params: ApiTestStepsRunParams = {
    steps: stepsInput,
    id: multiVarForm.caseDetail.id === null ? undefined : multiVarForm.caseDetail.id, // Assign id at root level
  };

  // Construct the case_detail from the form if name and url are provided
  if (multiVarForm.caseDetail.name && multiVarForm.caseDetail.url) {
    const caseData: Partial<ApiTestCaseData> = {
      // id: multiVarForm.caseDetail.id === null ? undefined : multiVarForm.caseDetail.id, // Remove id from here
      name: multiVarForm.caseDetail.name,
      url: multiVarForm.caseDetail.url,
      method: multiVarForm.caseDetail.method,
    };
    try {
      if (multiVarForm.caseDetail.headers) caseData.headers = multiVarForm.caseDetail.headers; // Already a string
      if (multiVarForm.caseDetail.params) caseData.params = multiVarForm.caseDetail.params; // Already a string
      if (multiVarForm.caseDetail.body) caseData.body = multiVarForm.caseDetail.body;    // Already a string
      if (multiVarForm.caseDetail.cookies) caseData.cookies = multiVarForm.caseDetail.cookies; // Already a string
      
      // Validate JSON strings if they are not empty or default '{}'
      const validateJsonString = (jsonStr: string | undefined, fieldName: string) => {
        if (jsonStr && jsonStr.trim() !== '{}' && jsonStr.trim() !== '') {
          JSON.parse(jsonStr); // This will throw an error if invalid
        }
      };
      validateJsonString(caseData.headers, '请求头');
      validateJsonString(caseData.params, 'Query参数');
      validateJsonString(caseData.body, '请求体');
      validateJsonString(caseData.cookies, 'Cookies');

      params.case = caseData as ApiTestCaseData; // Type assertion after checks
    } catch (e: any) {
      multiVarErrorInfo.value = `快捷用例 ${e.fieldName || ''} JSON解析错误: ${e.message}`;
      isLoadingMultiVar.value = false;
      ElMessage.error(multiVarErrorInfo.value);
      return;
    }
  }
  
  if (multiVarForm.envJson) {
    try {
      params.env = JSON.parse(multiVarForm.envJson);
    } catch (e: any) {
      multiVarErrorInfo.value = `环境变量JSON解析错误: ${e.message}`;
      isLoadingMultiVar.value = false;
      ElMessage.error(multiVarErrorInfo.value);
      return;
    }
  }
  console.info(params)

  try {
    const response = await runApiTestSteps(params);
    multiVarTestResult.value = response;
    ElMessage.success('多变量依赖测试执行完成！');
  } catch (error: any) {
    console.error('Error running multi-variable steps:', error);
    multiVarErrorInfo.value = error.response?.data?.detail || error.message || '执行多变量依赖测试失败';
    ElMessage.error(); // Ensure error message is displayed
  } finally {
    isLoadingMultiVar.value = false;
  }
};

interface NewExampleFormType extends Omit<Example, 'asserts'> {
  asserts: Assert[];
}

const AssertCategoryMap: Record<AssertCategory, string> = {
  [AssertCategory.STATUS_CODE]: '状态码 (status_code)',
  [AssertCategory.RESPONSE_TIME]: '响应时间 (response_time)',
  [AssertCategory.BODY_FIELD]: '响应体字段 (body_field)',
  [AssertCategory.BODY_TEXT]: '响应体文本 (body_text)',
  [AssertCategory.HEADER_FIELD]: '响应头字段 (header_field)',
  [AssertCategory.COOKIES_FIELD]: 'Cookies字段 (cookies_field)',
  [AssertCategory.ENV]: '环境变量 (env)',
};
const AssertOperatorMap: Record<AssertOperator, string> = {
  [AssertOperator.EQ]: '等于 (==)',
  [AssertOperator.NE]: '不等于 (!=)',
  [AssertOperator.GT]: '大于 (>)',
  [AssertOperator.GE]: '大于等于 (>=)',
  [AssertOperator.LT]: '小于 (<)',
  [AssertOperator.LE]: '小于等于 (<=)',
  [AssertOperator.CONTAINS]: '包含',
  [AssertOperator.NOT_CONTAINS]: '不包含',
  [AssertOperator.REGEX_MATCH]: '正则匹配',
  [AssertOperator.EXISTS]: '存在',
  [AssertOperator.NOT_EXISTS]: '不存在',
  [AssertOperator.STARTS_WITH]: '开头为',
  [AssertOperator.ENDS_WITH]: '结尾为',
};

const runTestModalVisible = ref(false);
const availableApiCases = ref<ApiCase[]>([]);
const runForm = ref({
  selectedCaseId: undefined as number | undefined,
});
const executionResult = ref<any>(null); // Stores the result of the *current* execution
const testHistory = ref<Array<any>>([]);
const showResultDialog = ref(false);
const currentResultForDialog = ref<any>(null);
const showTestReportDialog = ref(false);
const currentTestReportForDialog = ref<string>('');

const escapeHtml = (unsafe: string): string => {
  if (unsafe === null || unsafe === undefined) return '';
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}; // Renamed to avoid conflict with any existing currentResult
const isExecuting = ref(false);
const TEST_HISTORY_STORAGE_KEY = 'apiTestHistory';

// New reactive variables for Example Run Dialog
const showExampleRunDialog = ref(false);
const quickTestName = ref(''); // For the optional test name
const selectedBaseCaseId: any = ref(undefined);
const examplesJson = ref('');
const exampleRunLoading = ref(false);

// New reactive variables for creating a single Example
const showNewExampleDialog = ref(false);

const openNewExampleDialog = () => {
  // Reset form to default values
  newExampleForm.value = {
    headers: undefined,
    params: undefined,
    body: undefined,
    cookies: undefined,
    timeout: 10, // Default timeout
    asserts: [],
  };

  // Try to pre-fill from examplesJson if it's a valid array of examples
  if (examplesJson.value) {
    try {
      const parsedExamples = JSON.parse(examplesJson.value);
      if (Array.isArray(parsedExamples) && parsedExamples.length > 0) {
        const firstExample = parsedExamples[0]; // Use the first example to pre-fill
        
        const formatJsonField = (fieldValue: any) => {
          if (!fieldValue) return undefined;
          try {
            // Attempt to parse, if it's a JSON string, stringify it prettily
            const parsed = JSON.parse(fieldValue);
            return JSON.stringify(parsed, null, 2);
          } catch (e) {
            // If not a valid JSON string, return the original value
            return fieldValue;
          }
        };

        newExampleForm.value = {
          headers: formatJsonField(firstExample.headers),
          params: formatJsonField(firstExample.params),
          body: formatJsonField(firstExample.body),
          cookies: formatJsonField(firstExample.cookies),
          timeout: firstExample.timeout !== undefined ? firstExample.timeout : 10,
          asserts: firstExample.asserts ? JSON.parse(JSON.stringify(firstExample.asserts)) : [], // Deep copy asserts
        };
      }
    } catch (e) {
      console.warn('Could not parse examplesJson to pre-fill new example form:', e);
      // Keep default empty form if parsing fails
    }
  }
  showNewExampleDialog.value = true;
};
const newExampleForm = ref<NewExampleFormType>({
  headers: undefined,
  params: undefined,
  body: undefined,
  cookies: undefined,
  timeout: undefined,
  asserts: [],
});

const addAssert = () => {
  newExampleForm.value.asserts.push({
    category: AssertCategory.STATUS_CODE,
    operator: AssertOperator.EQ,
    path: undefined,
    expected: undefined,
  });
};

const removeAssert = (index: number) => {
  newExampleForm.value.asserts.splice(index, 1);
};

const addNewExample = () => {
  try {
    const exampleToSet: Example = {
      headers: newExampleForm.value.headers ? newExampleForm.value.headers : undefined,
      params: newExampleForm.value.params ? newExampleForm.value.params : undefined,
      body: newExampleForm.value.body ? newExampleForm.value.body : undefined,
      cookies: newExampleForm.value.cookies ? newExampleForm.value.cookies : undefined,
      timeout: newExampleForm.value.timeout,
      asserts: newExampleForm.value.asserts.map(assert => ({
        ...assert,
        path: (assert.path === '' || assert.path === null) ? undefined : assert.path,
        expected: (assert.expected === '' || assert.expected === null) ? undefined : assert.expected,
      })).filter(a => a.category && a.operator) // Ensure basic assert structure
    };

    // Directly overwrite examplesJson with an array containing only the new/modified example
    examplesJson.value = JSON.stringify([exampleToSet], null, 2);
    showNewExampleDialog.value = false;
    ElMessage.success('Examples JSON 已被修改');

    // Reset form for next use is good practice, though it's pre-filled on open now
    newExampleForm.value = {
      headers: undefined,
      params: undefined,
      body: undefined,
      cookies: undefined,
      timeout: 10, // Reset to default
      asserts: [],
    };
  } catch (e: any) {
    ElMessage.error('修改 Examples JSON 失败: ' + (e.message || '未知错误'));
  }
};

const submitExampleRun = async (isRerun: boolean = false, originalIndex?: number) => {
  try {
    exampleRunLoading.value = true;
    let parsedExamples: Example[] = [];

    if (examplesJson.value) {
      parsedExamples = JSON.parse(examplesJson.value);
      if (!Array.isArray(parsedExamples)) {
        ElMessage.error('Examples 必须是 JSON 数组');
        return;
      }
    } else if (newExampleForm.value.headers || newExampleForm.value.params || newExampleForm.value.body || newExampleForm.value.cookies || newExampleForm.value.timeout !== 10 || (newExampleForm.value.asserts && newExampleForm.value.asserts.length > 0)) {
      // If examplesJson is empty, but newExampleForm has data, use it as a single example
      const exampleToAdd: Example = {
        headers: (newExampleForm.value.headers === '' || newExampleForm.value.headers === null) ? undefined : newExampleForm.value.headers,
        params: (newExampleForm.value.params === '' || newExampleForm.value.params === null) ? undefined : newExampleForm.value.params,
        body: (newExampleForm.value.body === '' || newExampleForm.value.body === null) ? undefined : newExampleForm.value.body,
        cookies: (newExampleForm.value.cookies === '' || newExampleForm.value.cookies === null) ? undefined : newExampleForm.value.cookies,
        timeout: newExampleForm.value.timeout,
        asserts: newExampleForm.value.asserts && newExampleForm.value.asserts.length > 0 ? newExampleForm.value.asserts.map(assert => ({
          ...assert,
          path: (assert.path === '' || assert.path === null) ? undefined : assert.path,
          expected: (assert.expected === '' || assert.expected === null) ? undefined : assert.expected,
        })) : undefined,
      };
      parsedExamples.push(exampleToAdd);
    }

    // If no base case selected and no examples provided, show warning
    if ((selectedBaseCaseId.value === null || selectedBaseCaseId.value === undefined) && parsedExamples.length === 0) {
      ElMessage.warning('请选择一个基础用例或输入 Examples JSON 或新建 Example。');
      return;
    }

    const payload: ApiTestCaseRunPayload = {
      id: selectedBaseCaseId.value === undefined ? null : selectedBaseCaseId.value,
      case: undefined,
      examples: parsedExamples.length > 0 ? parsedExamples : undefined,
    };

    const result = await actualRunApiTestCase(payload);
    if (result) {
      executionResult.value = result; // Keep for any immediate display if needed
      const baseCase = availableApiCases.value.find(c => c.id === selectedBaseCaseId.value);
      const baseCaseName = baseCase ? baseCase.name : '未选基础用例';
      let finalCaseName = quickTestName.value.trim();
      if (!finalCaseName) {
        finalCaseName = `快捷用例 - ${baseCaseName} - ${new Date().toLocaleTimeString()}`;
      }

      const historyEntry = {
        caseName: finalCaseName,
        originalBaseCaseName: baseCaseName, // Store for potential future use or display
        params: { id: selectedBaseCaseId.value, examples: parsedExamples, quickTestName: quickTestName.value }, // Store params for rerun
        result: result,
        timestamp: Date.now(),
        type: 'exampleRun'
      };
      if (isRerun && originalIndex !== undefined) {
        testHistory.value.splice(originalIndex, 1, historyEntry);
      } else {
        testHistory.value.unshift(historyEntry);
      }
      ElMessage.success('用例测试已提交并执行成功！');
    } else {
      executionResult.value = { error: true, message: '执行成功，但未收到有效数据。', details: null };
      ElMessage.warning('执行成功，但未收到有效数据。');
    }
    showExampleRunDialog.value = false;
  } catch (e: any) {
    ElMessage.error('提交失败: ' + (e.message || '未知错误'));
    executionResult.value = { error: true, message: e.message || '未知错误', details: e };
  } finally {
    exampleRunLoading.value = false;
  }
};

const saveExampleRunConfiguration = async () => {
  try {
    let parsedExamples: Example[] = [];

    if (examplesJson.value) {
      try {
        parsedExamples = JSON.parse(examplesJson.value);
        if (!Array.isArray(parsedExamples)) {
          ElMessage.error('Examples 必须是 JSON 数组');
          return;
        }
      } catch (e) {
        ElMessage.error('Examples JSON 格式不正确，请检查。');
        return;
      }
    }

    // If no base case selected and no examples provided, show warning
    if ((selectedBaseCaseId.value === null || selectedBaseCaseId.value === undefined) && parsedExamples.length === 0) {
      ElMessage.warning('请选择一个基础用例或输入 Examples JSON。');
      return;
    }

    const baseCase = availableApiCases.value.find(c => c.id === selectedBaseCaseId.value);
    const baseCaseName = baseCase ? baseCase.name : '未选基础用例';
    let finalCaseName = quickTestName.value.trim();
    if (!finalCaseName) {
      finalCaseName = `快捷配置 - ${baseCaseName} - ${new Date().toLocaleTimeString()}`;
    }

    const historyEntry = {
      caseName: finalCaseName,
      originalBaseCaseName: baseCaseName, // Store for potential future use or display
      params: { id: selectedBaseCaseId.value, examples: parsedExamples, quickTestName: quickTestName.value }, // Store params
      result: null, // No execution result for saving configuration
      timestamp: Date.now(),
      type: 'exampleConfigSave' // New type for saved configurations
    };

    testHistory.value.unshift(historyEntry);
    ElMessage.success('配置已保存到测试历史！');
    showExampleRunDialog.value = false;

  } catch (e: any) {
    ElMessage.error('保存配置失败: ' + (e.message || '未知错误'));
  }
};

// Fetch available API cases when the component is mounted
onMounted(async () => {
  // Load test history from localStorage
  const storedHistory = localStorage.getItem(TEST_HISTORY_STORAGE_KEY);
  if (storedHistory) {
    try {
      testHistory.value = JSON.parse(storedHistory);
    } catch (e) {
      console.error('Failed to parse test history from localStorage:', e);
      localStorage.removeItem(TEST_HISTORY_STORAGE_KEY); // Clear corrupted data
    }
  }

  try {
    const cases = await getAllApiCases();
    availableApiCases.value = Array.isArray(cases) ? cases : [];
  } catch (error) {
    ElMessage.error('获取API用例列表失败');
    console.error('Failed to fetch API cases for runner:', error);
  }
});

// Watch for changes in testHistory and save to localStorage
watch(testHistory, (newHistory) => {
  try {
    localStorage.setItem(TEST_HISTORY_STORAGE_KEY, JSON.stringify(newHistory));
  } catch (e) {
    console.error('Failed to save test history to localStorage:', e);
    ElMessage.error('保存测试历史到本地存储失败，可能已超出存储限制。');
  }
}, { deep: true });

const viewResult = (historyItem: any) => {
  currentResultForDialog.value = historyItem;
  showResultDialog.value = true;
};

const generateTestReportHtml = (resultData: any): string => {
  if (!resultData || !resultData.result) {
    return '<p>没有可用的测试结果来生成报告。</p>';
  }

  const result = resultData.result;
  let reportHtml = `<h2>测试报告: ${escapeHtml(resultData.caseName || '未命名测试')}</h2>`;
  reportHtml += `<p><strong>执行时间:</strong> ${new Date(resultData.timestamp).toLocaleString()}</p>`;

  // 整体测试状态 (简单判断，后续可以根据断言结果更精确)
  const overallSuccess = result.running_results ? 
                         result.running_results.every((rr: any) => rr.assert_result && rr.assert_result.every((ar: any) => ar.success)) :
                         (result.assert_result && result.assert_result.every((ar: any) => ar.success));

  reportHtml += `<p><strong>总体结果:</strong> <span style="color: ${overallSuccess ? 'green' : 'red'}; font-weight: bold;">${overallSuccess ? '通过' : '失败'}</span></p>`;
  reportHtml += '<hr>';

  if (result.running_results && Array.isArray(result.running_results)) {
    reportHtml += '<h3>详细执行步骤:</h3>';
    result.running_results.forEach((runResult: any, index: number) => {
      reportHtml += `<h4>步骤 ${index + 1}: ${escapeHtml(runResult.example_name || '未命名步骤')}</h4>`;
      
      // 请求信息
      reportHtml += '<h5>请求详情:</h5>';
      if (runResult.request_info) {
        reportHtml += `<p><strong>URL:</strong> ${escapeHtml(runResult.request_info.url)}</p>`;
        reportHtml += `<p><strong>Method:</strong> ${escapeHtml(runResult.request_info.method)}</p>`;
        if (runResult.request_info.headers) {
          reportHtml += `<p><strong>Headers:</strong></p><pre>${escapeHtml(JSON.stringify(runResult.request_info.headers, null, 2))}</pre>`;
        }
        if (runResult.request_info.body) {
          reportHtml += `<p><strong>Body:</strong></p><pre>${escapeHtml(JSON.stringify(runResult.request_info.body, null, 2))}</pre>`;
        }
      }

      // 断言结果
      reportHtml += '<h5>断言结果:</h5>';
      if (runResult.assert_result && Array.isArray(runResult.assert_result)) {
        reportHtml += '<ul>';
        runResult.assert_result.forEach((assert: any) => {
          const color = assert.success ? 'green' : 'red';
          reportHtml += `<li style="color: ${color};"><strong>${assert.success ? '[通过]' : '[失败]'}</strong> ${escapeHtml(assert.message || assert.description || '无描述')}</li>`;
        });
        reportHtml += '</ul>';
      } else {
        reportHtml += '<p>无断言信息。</p>';
      }

      // 响应信息
      reportHtml += '<h5>响应详情:</h5>';
      if (runResult.response) {
        reportHtml += `<p><strong>Status Code:</strong> ${runResult.response.status_code}</p>`;
        reportHtml += `<p><strong>Response Time:</strong> ${runResult.response.response_time_ms} ms</p>`;
        if (runResult.response.headers) {
          reportHtml += `<p><strong>Headers:</strong></p><pre>${escapeHtml(JSON.stringify(runResult.response.headers, null, 2))}</pre>`;
        }
        let responseBody = runResult.response.body;
        if (typeof responseBody === 'string') {
          try {
            responseBody = JSON.parse(responseBody); //尝试解析为JSON以美化显示
            reportHtml += `<p><strong>Body:</strong></p><pre>${escapeHtml(JSON.stringify(responseBody, null, 2))}</pre>`;
          } catch (e) {
            reportHtml += `<p><strong>Body (Text):</strong></p><pre>${escapeHtml(responseBody)}</pre>`;
          }
        } else if (typeof responseBody === 'object'){
            reportHtml += `<p><strong>Body:</strong></p><pre>${escapeHtml(JSON.stringify(responseBody, null, 2))}</pre>`;
        } else {
            reportHtml += `<p><strong>Body:</strong> ${escapeHtml(String(responseBody))}</p>`;
        }
      }
      reportHtml += '<hr style="margin-top: 1em; margin-bottom: 1em;">';
    });
  } else if (result.assert_result) { // 单个用例执行结果
      // 请求信息 (假设在 result.request_info)
      if (result.request_info) {
        reportHtml += '<h5>请求详情:</h5>';
        reportHtml += `<p><strong>URL:</strong> ${escapeHtml(result.request_info.url)}</p>`;
        reportHtml += `<p><strong>Method:</strong> ${escapeHtml(result.request_info.method)}</p>`;
        if (result.request_info.headers) {
          reportHtml += `<p><strong>Headers:</strong></p><pre>${escapeHtml(JSON.stringify(result.request_info.headers, null, 2))}</pre>`;
        }
        if (result.request_info.body) {
          reportHtml += `<p><strong>Body:</strong></p><pre>${escapeHtml(JSON.stringify(result.request_info.body, null, 2))}</pre>`;
        }
      }

      // 断言结果
      reportHtml += '<h5>断言结果:</h5>';
      if (Array.isArray(result.assert_result)) {
        reportHtml += '<ul>';
        result.assert_result.forEach((assert: any) => {
          const color = assert.success ? 'green' : 'red';
          reportHtml += `<li style="color: ${color};"><strong>${assert.success ? '[通过]' : '[失败]'}</strong> ${escapeHtml(assert.message || assert.description || '无描述')}</li>`;
        });
        reportHtml += '</ul>';
      } else {
        reportHtml += '<p>无断言信息。</p>';
      }
      
      // 响应信息 (假设在 result.response)
      if (result.response) {
        reportHtml += '<h5>响应详情:</h5>';
        reportHtml += `<p><strong>Status Code:</strong> ${result.response.status_code}</p>`;
        reportHtml += `<p><strong>Response Time:</strong> ${result.response.response_time_ms} ms</p>`;
        if (result.response.headers) {
          reportHtml += `<p><strong>Headers:</strong></p><pre>${escapeHtml(JSON.stringify(result.response.headers, null, 2))}</pre>`;
        }
        let responseBody = result.response.body;
        if (typeof responseBody === 'string') {
          try {
            responseBody = JSON.parse(responseBody); //尝试解析为JSON以美化显示
            reportHtml += `<p><strong>Body:</strong></p><pre>${escapeHtml(JSON.stringify(responseBody, null, 2))}</pre>`;
          } catch (e) {
            reportHtml += `<p><strong>Body (Text):</strong></p><pre>${escapeHtml(responseBody)}</pre>`;
          }
        } else if (typeof responseBody === 'object'){
            reportHtml += `<p><strong>Body:</strong></p><pre>${escapeHtml(JSON.stringify(responseBody, null, 2))}</pre>`;
        } else {
            reportHtml += `<p><strong>Body:</strong> ${escapeHtml(String(responseBody))}</p>`;
        }
      }
  } else {
    reportHtml += '<p>未找到详细的执行结果或断言信息。</p>';
  }

  return reportHtml;
};

const viewTestReport = (historyItem: any) => {
  currentTestReportForDialog.value = generateTestReportHtml(historyItem);
  showTestReportDialog.value = true;
};


const editAndRerun = (historyItem: any, index: number) => {
  if (historyItem.type === 'singleCase' && historyItem.params && historyItem.params.id) {
    runForm.value.selectedCaseId = historyItem.params.id;
    // To make 'executeTestCase' update the existing item, we'd pass true for isRerun and the index.
    // For now, opening the dialog and letting the user click 'Execute' will create a new entry.
    // To update in place, the 'Execute' button in the dialog would need to call executeTestCase(true, index)
    runTestModalVisible.value = true; 
    // If you want the execute button in the dialog to update, you'll need to manage the 'isRerun' and 'originalIndex' state for that dialog's execution.
  } else if ((historyItem.type === 'exampleRun' || historyItem.type === 'exampleConfigSave') && historyItem.params) {
    selectedBaseCaseId.value = historyItem.params.id;
    examplesJson.value = historyItem.params.examples ? JSON.stringify(historyItem.params.examples, null, 2) : '';
    quickTestName.value = historyItem.params.quickTestName || historyItem.caseName || ''; // Populate quickTestName
    showExampleRunDialog.value = true;
  }
  // Store the index if you want the dialog's execute button to update the specific history item.
  // This might involve adding a temporary ref like 'currentIndexForRerun' and using it in the dialog's execute methods.
};

const deleteHistory = (index: number) => {
  testHistory.value.splice(index, 1);
  ElMessage.success('测试历史已删除');
};

const showRunTestModal = () => {
  executionResult.value = null; // Clear previous results
  runForm.value.selectedCaseId = undefined; // Reset selection
  runTestModalVisible.value = true;
};

const resetRunModal = () => {
  executionResult.value = null;
  runForm.value.selectedCaseId = undefined;
  isExecuting.value = false;
};

const resetExampleRunModal = () => {
  quickTestName.value = ''; // Reset the test name
  selectedBaseCaseId.value = undefined;
  examplesJson.value = '';
  exampleRunLoading.value = false;
  // Reset newExampleForm as well if it's tied to this dialog's lifecycle for clearing
  newExampleForm.value = {
    headers: undefined,
    params: undefined,
    body: undefined,
    cookies: undefined,
    timeout: undefined,
    asserts: [],
  };
  // Ensure any other state related to this dialog is reset here if necessary
};

const executeTestCase = async () => {
  if (!runForm.value.selectedCaseId) {
    ElMessage.warning('请先选择一个API用例');
    return;
  }
  isExecuting.value = true;
  executionResult.value = null; // Clear previous results
  try {
    const result = await actualRunApiTestCase({ id: runForm.value.selectedCaseId });
    if (result) {
      executionResult.value = result; // Keep for any immediate display if needed
    } else {
      executionResult.value = { error: true, message: '执行成功，但未收到有效数据。', details: null };
      ElMessage.warning('执行成功，但未收到有效数据。');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '执行测试用例失败');
    executionResult.value = { error: true, message: error.message || '未知错误', details: error };
    console.error('Failed to execute test case:', error);
  } finally {
    isExecuting.value = false;
  }
};

const runQuickTest = async () => {
  showRunTestModal(); // Use the existing modal for running test cases
};




// Helper to style keys based on depth
function getStyleForKey(level: number): string {
  const colors = ['#D32F2F', '#1976D2', '#388E3C', '#7B1FA2', '#C2185B']; // Material Design Red, Blue, Green, Purple, Pink
  const color = colors[level % colors.length];
  return `font-weight: bold; color: ${color};`;
}

// Recursive function to convert JSON object to HTML string
function jsonToHtml(obj: any, indentLevel = 0): string {
  const indent = '&nbsp;'.repeat(indentLevel * 2); // 2 spaces per indent level

  if (obj === null) return `<span style="color: #90A4AE;">null</span>`;
  if (obj === undefined) return `<span style="color: #90A4AE;">undefined</span>`;

  switch (typeof obj) {
    case 'string':
      return `<span style="color: #43A047;">"${escapeHtml(obj)}"</span>`; // Green for strings
    case 'number':
      return `<span style="color: #FB8C00;">${obj}</span>`; // Orange for numbers
    case 'boolean':
      return `<span style="color: #E53935;">${obj}</span>`; // Red for booleans
    case 'object':
      if (Array.isArray(obj)) {
        let arrHtml = `${indent}[`;
        if (obj.length === 0) {
          arrHtml += `]`;
        } else {
          arrHtml += '<br>';
          arrHtml += obj.map((item) => `${indent}&nbsp;&nbsp;${jsonToHtml(item, indentLevel + 1)}`).join(',<br>');
          arrHtml += `<br>${indent}]`;
        }
        return arrHtml;
      } else {
        // Regular object
        const keys = Object.keys(obj);
        let objHtml = `${indent}{`;
        if (keys.length === 0) {
          objHtml += `}`;
        } else {
          objHtml += '<br>';
          objHtml += keys.map(key => {
            const escapedKey = escapeHtml(key);
            return `${indent}&nbsp;&nbsp;<span style="${getStyleForKey(indentLevel)}">${escapedKey}</span>: ${jsonToHtml(obj[key], indentLevel + 1)}`;
          }).join(',<br>');
          objHtml += `<br>${indent}}`;
        }
        return objHtml;
      }
    default:
      return escapeHtml(String(obj)); // Fallback for other types
  }
}

const renderJsonResult = (data: any) => {
  if (!data) return '';
  try {
    // Create a deep copy to modify for display
    const displayResult = JSON.parse(JSON.stringify(data));

    // Iterate through running_results, reorder properties, and try to parse 'body' in each response
    if (displayResult.running_results && Array.isArray(displayResult.running_results)) {
      displayResult.running_results = displayResult.running_results.map((runResult: any) => {
        if (runResult && typeof runResult === 'object') {
          // Try to parse response body
          if (runResult.response && typeof runResult.response.body === 'string') {
            try {
              runResult.response.body = JSON.parse(runResult.response.body);
            } catch (e) {
              // Not a valid JSON string, leave as is
            }
          }

          // Reorder properties: assert_result first, then response, then others
          const { assert_result, response, ...otherProps } = runResult;
          const reorderedRunResult: any = {};
          if (assert_result !== undefined) {
            reorderedRunResult.assert_result = assert_result;
          }
          if (response !== undefined) {
            reorderedRunResult.response = response;
          }
          // Add back other properties
          for (const key in otherProps) {
            if (Object.prototype.hasOwnProperty.call(otherProps, key)) {
              reorderedRunResult[key] = otherProps[key];
            }
          }
          return reorderedRunResult;
        }
        return runResult; // Return as is if not an object or null
      });
    }
    return jsonToHtml(displayResult);
  } catch (e) {
    console.error("Error formatting JSON result:", e);
    return '<span style="color: red;">无法格式化结果为JSON</span>';
  }
};

const formattedJsonResult = computed(() => { // Original computed, now used for the old direct display if any part still uses it.
  if (!executionResult.value) return '';
  try {
    // Create a deep copy to modify for display
    const displayResult = JSON.parse(JSON.stringify(executionResult.value));

    // Iterate through running_results and try to parse 'body' in each response
    // This ensures that if response.body is a JSON string, it's parsed into an object/array
    // before being passed to jsonToHtml.
    if (displayResult.running_results && Array.isArray(displayResult.running_results)) {
      displayResult.running_results.forEach((runResult: any) => {
        if (runResult && runResult.response && typeof runResult.response.body === 'string') {
          try {
            runResult.response.body = JSON.parse(runResult.response.body);
          } catch (e) {
            // Not a valid JSON string, jsonToHtml will treat it as a plain string
          }
        }
      });
    }

    return jsonToHtml(displayResult);
  } catch (e) {
    console.error("Error formatting JSON result:", e);
    return '<span style="color: red;">无法格式化结果为JSON</span>'; // Return HTML error message
  }
});

</script>

<style scoped>
.api-test-runner {
  padding: 20px;
}

.result-display {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #f9fafc;
}

.result-display h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.json-display {
  font-family: 'Courier New', Courier, monospace;
  background-color: #f9fafc; /* Dialog background color */
  padding: 10px;
  border-radius: 4px;
  max-height: 500px; /* Adjust as needed for dialog content */
  overflow-y: auto;
  text-align: left; /* Ensures left alignment */
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.json-output {
  font-family: 'Courier New', Courier, monospace;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  text-align: left;
  line-height: 1.4;
  word-wrap: break-word;
}

.json-output .toggler {
  cursor: pointer;
  margin-right: 5px;
  user-select: none; /* Prevent text selection on click */
  display: inline-block;
  width: 1em; /* Ensure consistent spacing for toggler */
}

</style>