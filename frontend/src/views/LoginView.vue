<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>用户登录</span>
        </div>
      </template>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名"/>
        </el-form-item>
        <el-form-item prop="password">
          <el-input type="password" v-model="loginForm.password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%;">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElCard, ElForm, ElFormItem, ElInput, ElButton } from 'element-plus';
// import { User, Lock } from '@element-plus/icons-vue';
import { useAuthStore } from '@/store/auth'; // Corrected path
import type { LoginCredentials } from '@/api/types';

const router = useRouter();
const authStore = useAuthStore();

const loginFormRef = ref();
const loginForm = reactive<LoginCredentials>({
  username: 'JJack',
  password: '1234567',
});
const loading = ref(false);

const rules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
});

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true;
      try {
        await authStore.login(loginForm);
        ElMessage.success('登录成功');
        router.push('/'); // Or to a default authenticated route like '/autotest'
      } catch (error: any) { // Catching 'any' for now, consider more specific error typing
        ElMessage.error(error.message || '登录失败，请检查您的凭据');
        console.error('Login failed:', error);
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.error('请完整填写登录信息');
      return false;
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* Adjust if you have header/footer */
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 1.5em;
}
</style>