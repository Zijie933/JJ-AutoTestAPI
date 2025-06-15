<template>
  <el-container class="login-container">
    <el-main>
      <el-card class="login-card">
        <template #header>
          <div class="card-header">
            <span>用户登录</span>
          </div>
        </template>
        <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input type="password" v-model="loginForm.password" placeholder="请输入密码" show-password @keyup.enter="handleLogin"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
          </el-form-item>
        </el-form>
        <el-alert v-if="error" :title="error" type="error" show-icon :closable="false"></el-alert>
      </el-card>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, FormInstance, FormRules } from 'element-plus';
import { useUserStore } from '../store/user';
import { login as apiLogin } from '../api/auth';
import type { LoginCredentials } from '@/api/types';

const router = useRouter();
const userStore = useUserStore();

const loginFormRef = ref<FormInstance>();
const loginForm = reactive<LoginCredentials>({
  username: '',
  password: '',
});

const loginRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
});

const loading = ref(false);
const error = ref<string | null>(null);

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      error.value = null;
      try {
        const response = await apiLogin(loginForm);
        userStore.setToken(response.access_token);
        // Assuming your backend login response includes username, or you fetch it separately
        // For now, let's use the input username or a placeholder
        userStore.setUsername(loginForm.username); 
        ElMessage.success('登录成功');
        router.push('/'); // Redirect to AutoTest page or dashboard
      } catch (err: any) {
        console.error('Login failed:', err);
        error.value = err.response?.data?.detail || err.message || '登录失败，请检查您的凭据或联系管理员。';
        ElMessage.error();
      }
      loading.value = false;
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 20px;
}
</style>