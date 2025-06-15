<template>
  <div id="app">
    <el-header v-if="isAuthenticated" class="app-header">
      <div class="logo-title">
        <!-- <img alt="Vue logo" src="./assets/logo.png" class="logo" /> -->
        <span class="title">JJ-ApiAutoTest</span>
      </div>
      <nav class="navigation-links">
        <router-link to="/">首页</router-link>
        <router-link to="/api-case-management">用例管理</router-link>
        <router-link to="/api-test-runner">测试执行</router-link> <!-- Added link to Test Runner -->
        <!-- Add other navigation links here -->
      </nav>
      <div class="user-actions">
        <el-dropdown @command="handleUserCommand">
          <span class="el-dropdown-link">
            {{ username || '用户' }}<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main class="app-main-content">
      <router-view />
    </el-main>

    <el-footer v-if="isAuthenticated" class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} API Automation Platform. All rights reserved.</p>
    </el-footer>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { useAuthStore } from './store/auth.js';
import { useRouter } from 'vue-router';
import { ElHeader, ElMain, ElFooter, ElDropdown, ElDropdownMenu, ElDropdownItem, ElIcon } from 'element-plus';


const authStore = useAuthStore();
const router = useRouter();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const username = computed(() => authStore.user?.username);

const handleUserCommand = (command: string) => {
  if (command === 'logout') {
    authStore.logout();
    router.push('/login');
  }
};

// Optional: Redirect to login if not authenticated and trying to access a protected route
// This can also be handled by navigation guards in router/index.ts
// router.beforeEach((to, from, next) => {
//   if (to.meta.requiresAuth && !isAuthenticated.value && to.name !== 'Login') {
//     next({ name: 'Login' });
//   } else {
//     next();
//   }
// });

</script>

<style>
/* General App Styles */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #409EFF; /* Element Plus primary color */
  color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between; /* Restore for overall layout */
  height: 60px;
  border-bottom: 1px solid #e0e0e0;
}

.logo-title {
  display: flex;
  align-items: center;
  flex-shrink: 0; /* Prevent shrinking */
}

.logo {
  height: 40px;
  margin-right: 10px;
}

.title {
  font-size: 1.5em;
  font-weight: bold;
}

.navigation-links {
  flex-grow: 1; /* Allow navigation to take available space */
  text-align: center; /* Center the links within the navigation area */
}

.navigation-links a {
  font-weight: bold;
  color: #ffffff; /* White links */
  margin: 0 15px;
  text-decoration: none;
  padding: 5px 0;
}

.navigation-links a.router-link-exact-active {
  color: #ffd04b; /* Element Plus warning color for active link */
  border-bottom: 2px solid #ffd04b;
}

.user-actions {
  flex-shrink: 0; /* Prevent shrinking */
}

.user-actions .el-dropdown-link {
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
}

.app-main-content {
  flex-grow: 1;
  padding: 20px;
  background-color: #f4f6f8; /* Light background for content area */
}

.app-footer {
  background-color: #f0f2f5;
  color: #606266;
  text-align: center;
  padding: 15px 0;
  border-top: 1px solid #e0e0e0;
  font-size: 0.9em;
}

/* Ensure Element Plus components are styled correctly if not globally imported */
</style>
