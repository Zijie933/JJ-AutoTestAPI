<template>
  <div class="api-case-management">
    <div class="toolbar">
      <el-button type="primary" @click="handleAdd">新增案例</el-button>
      <el-button @click="fetchApiCases" :loading="loading">刷新</el-button> 
    </div>
    <el-table :data="apiCases" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="用例名称"></el-table-column>
      <el-table-column prop="method" label="请求方法" width="100"></el-table-column>
      <el-table-column prop="url" label="URL"></el-table-column>
      <el-table-column label="Headers" width="120">
        <template #default="scope">
          <span>{{ scope.row.headers || '/' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Params" width="120">
        <template #default="scope">
          <span>{{ scope.row.params || '/' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Body" width="120">
        <template #default="scope">
          <span>{{ scope.row.body || '/' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Cookies" width="120">
        <template #default="scope">
          <span>{{ scope.row.cookies || '/' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="currentCase" :rules="rules" ref="caseFormRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="currentCase.name" placeholder="请输入用例名称"></el-input>
        </el-form-item>
        <el-form-item label="请求URL" prop="url">
          <el-input v-model="currentCase.url" placeholder="请输入请求URL"></el-input>
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="currentCase.method" placeholder="请选择请求方法">
            <el-option label="GET" value="GET"></el-option>
            <el-option label="POST" value="POST"></el-option>
            <el-option label="PUT" value="PUT"></el-option>
            <el-option label="DELETE" value="DELETE"></el-option>
            <!-- <el-option label="PATCH" value="PATCH"></el-option> --> 
            <!-- Add other methods if needed -->
          </el-select>
        </el-form-item>
        <el-form-item label="Headers" prop="headers">
          <el-input v-model="currentCase.headers" type="textarea" :rows="2" placeholder="请输入请求头 (JSON格式)"></el-input>
        </el-form-item>
        <el-form-item label="Params" prop="params">
          <el-input v-model="currentCase.params" type="textarea" :rows="2" placeholder="请输入Query参数 (JSON格式)"></el-input>
        </el-form-item>
        <el-form-item label="Body" prop="body">
          <el-input v-model="currentCase.body" type="textarea" :rows="3" placeholder="请输入请求体 (JSON格式)"></el-input>
        </el-form-item>
        <el-form-item label="Cookies" prop="cookies">
          <el-input v-model="currentCase.cookies" type="textarea" :rows="2" placeholder="请输入Cookies (JSON格式)"></el-input>
        </el-form-item>
        <!-- Add other fields here if needed, e.g., headers, body -->
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive, watch } from 'vue'; // Added watch
import { getAllApiCases, createApiCase, updateApiCase, deleteApiCase, type ApiCase } from '@/api/autotest';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';

const apiCases = ref<ApiCase[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const isEditMode = ref(false);

const initialCaseData: ApiCase = {
  id: 0,
  name: '',
  url: '',
  method: 'GET', // Default method
  headers: '',
  params: '',
  body: '',
  cookies: '',
};
const currentCase = ref<ApiCase>({ ...initialCaseData });
const caseFormRef = ref<FormInstance>();

// Custom validator for JSON format
const validateJson = (rule: any, value: any, callback: any) => {
  if (value && value.trim() !== '') {
    try {
      JSON.parse(value);
      callback();
    } catch (e) {
      callback(new Error('请输入有效的JSON格式'));
    }
  } else {
    callback(); // Allow empty value, or make it required if needed
  }
};

const rules = reactive<FormRules<ApiCase>>({
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  url: [
    { required: true, message: '请输入URL', trigger: 'blur' },
    // Basic URL validation (can be improved with a more robust regex)
    { type: 'url', message: '请输入有效的URL', trigger: ['blur', 'change'] }
  ],
  headers: [{ validator: validateJson, trigger: 'blur' }],
  params: [{ validator: validateJson, trigger: 'blur' }],
  body: [{ validator: validateJson, trigger: 'blur' }],
  cookies: [{ validator: validateJson, trigger: 'blur' }],
  // Add other validation rules as needed
});

const fetchApiCases = async () => {
  loading.value = true;
  try {
    const res = await getAllApiCases(); // getAllApiCases now returns ApiCase[] directly
    // The response (res) is now expected to be ApiCase[] directly
    // due to the updated request interceptor in src/api/index.ts
    if (Array.isArray(res)) {
      apiCases.value = res.map((item: ApiCase) => ({
        ...item,
        headers: item.headers === null ? '' : item.headers,
        params: item.params === null ? '' : item.params,
        body: item.body === null ? '' : item.body,
        cookies: item.cookies === null ? '' : item.cookies,
      }));
    } else {
      // This case should ideally not happen if the backend and types are correct
      console.error('fetchApiCases: Expected an array but received:', res);
      ElMessage.error('获取API用例列表失败: 数据格式不正确');
      apiCases.value = []; // Clear existing cases or handle as appropriate
    }
  } catch (error) {
    ElMessage.error('获取API用例列表失败');
    console.error('Error in fetchApiCases:', error); // More specific logging
    console.error(error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchApiCases();
});

const handleAdd = () => {
  isEditMode.value = false;
  dialogTitle.value = '新增API测试案例';
  currentCase.value = { ...initialCaseData };
  dialogVisible.value = true;
  caseFormRef.value?.resetFields(); // Reset validation
};

const handleEdit = (row: ApiCase) => {
  isEditMode.value = true;
  dialogTitle.value = '编辑API测试案例';
  currentCase.value = { ...row };
  dialogVisible.value = true;
};

const handleDelete = async (id: number | undefined) => {
  if (id === undefined) return;
  try {
    await ElMessageBox.confirm('确定删除此测试案例吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    await deleteApiCase(id);
    ElMessage.success('删除成功');
    fetchApiCases(); // Refresh the list
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
      console.error(error);
    }
  }
};

const submitForm = async () => {
  if (!caseFormRef.value) return;
  await caseFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditMode.value && currentCase.value.id) {
          // updateApiCase now returns the updated ApiCase directly or throws an error
          await updateApiCase(currentCase.value.id, currentCase.value);
          ElMessage.success('更新成功');
        } else {
          // createApiCase now returns the created ApiCase directly or throws an error
          await createApiCase(currentCase.value);
          ElMessage.success('新增成功');
        }
        dialogVisible.value = false;
        fetchApiCases(); // Refresh the list
      } catch (error) {
        // Error messages are now handled by the interceptor or can be more specific here
        // ElMessage.error(isEditMode.value ? '更新失败' : '新增失败');
        console.error('Error in submitForm:', error); // Error already logged by interceptor
      }
    }
  });
};

// Watch for changes in form data to potentially re-validate or provide live feedback if needed
// This is optional but can enhance UX for complex validation scenarios.
// For simple JSON validation on blur, it might not be strictly necessary.
//watch(form, (newValue) => {
  // Example: if you wanted to do something more complex on value change
  // console.log('Form data changed:', newValue);
//}, { deep: true });

</script>

<style scoped>
.api-case-management {
  padding: 20px;
}
.toolbar {
  margin-bottom: 20px;
  text-align: right;
}
</style>