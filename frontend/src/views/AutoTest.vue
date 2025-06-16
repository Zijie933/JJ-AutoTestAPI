<template>
  <el-container class="autotest-container">
    <el-header class="app-header">
      <span>接口自动化测试平台</span>
      <div class="user-info">
        <span>你好, {{ authStore.user?.username }}</span>
        <el-button type="danger" plain @click="handleLogout" size="small">退出登录</el-button>
      </div>
    </el-header>
    <el-main>
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane label="API测试用例管理" name="apiCaseManagement">
          <api-case-management />
        </el-tab-pane>
        <el-tab-pane label="执行API测试" name="runApiTest">
          <run-api-test />
        </el-tab-pane>
        <el-tab-pane label="执行场景测试" name="runStepTest">
          // <RunStepTest v-if="activeTab === 'runStepTest'" />
        </el-tab-pane> 
        <!-- Add more tabs for other functionalities -->
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '../store/auth'; // Corrected import
// Placeholder components - you'll need to create these
import ApiCaseManagement from '../components/autotest/ApiCaseManagement.vue';
// import RunApiTest from '../components/autotest/RunApiTest.vue'; // Assuming this is ApiTestRunner.vue
import ApiTestRunner from '../components/autotest/ApiTestRunner.vue'; // Corrected to actual component
import RunStepTest from '../components/autotest/RunStepTest.vue';

const router = useRouter();
const authStore = useAuthStore(); // Corrected usage

const activeTab = ref('apiCaseManagement');

const handleLogout = () => {
  ElMessageBox.confirm('您确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      authStore.logout(); // Corrected usage
      ElMessage.success('已退出登录');
      router.push('/login');
    })
    .catch(() => {
      // Catch cancel action
    });
};

// If username is not available on initial load, you might want to fetch it
// or ensure it's set during login.
// The username is now accessed via authStore.user?.username
// This block can be removed or adjusted if specific logic for missing username is needed.
// if (!authStore.user?.username) { 
//   // Potentially fetch user info if token exists but username is missing
//   console.warn('Username not found in store. Ensure it is set upon login.');
// }

</script>

<style scoped>
.autotest-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #409eff;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  line-height: 60px;
  font-size: 20px;
}

.user-info {
  font-size: 14px;
  display: flex;
  align-items: center;
}

.user-info span {
  margin-right: 15px;
}

.el-main {
  padding: 20px;
  background-color: #f4f4f5;
  flex-grow: 1;
  overflow-y: auto; /* Allows scrolling if content overflows */
}

.main-tabs {
  background-color: #fff;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}
</style>

<template>
  <div class="autotest-container">
    <el-tabs v-model="activeTab" class="autotest-tabs">
      <el-tab-pane label="API用例管理" name="apiCaseManagement">
        <ApiCaseManagement v-if="activeTab === 'apiCaseManagement'" />
      </el-tab-pane>
      <el-tab-pane label="API测试执行" name="apiTestRunner">
        <ApiTestRunner v-if="activeTab === 'apiTestRunner'" />
      </el-tab-pane>
      <!-- <el-tab-pane label="执行场景测试" name="runStepTest">
        // <RunStepTest v-if="activeTab === 'runStepTest'" /> 
      </el-tab-pane> --> // Ensure this block is commented out or removed
      <!-- Add more tabs for other functionalities -->
    </el-tabs>
  </div>
</template>