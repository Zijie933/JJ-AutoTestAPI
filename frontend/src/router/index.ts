import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

import HomeView from '../views/HomeView.vue';
import ApiCaseManagement from '../components/autotest/ApiCaseManagement.vue';
import ApiTestRunner from '../components/autotest/ApiTestRunner.vue'; // Import the new component
// import Login from '../views/Login.vue'; // This line seems to be unused if LoginView is lazy loaded
import AutoTest from '../views/AutoTest.vue';
import { useAuthStore } from '../store/auth'; // Corrected to useAuthStore from auth.ts

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true } // Assuming home also requires auth
  },
  
  {
    path: '/api-case-management',
    name: 'ApiCaseManagement',
    component: ApiCaseManagement,
    meta: { requiresAuth: true } // Example: If this route requires authentication
  },
  {
    path: '/api-test-runner',
    name: 'ApiTestRunner',
    component: ApiTestRunner, // Add route for the new component
    meta: { requiresAuth: true } // Example: If this route requires authentication
  },
  {
    path: '/login',
    name: 'Login',
    // route level code-splitting
    // this generates a separate chunk (About.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import('../views/LoginView.vue'),
  },
  // Add other routes here
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(); // Corrected to useAuthStore
  if (to.meta.requiresAuth && !authStore.isAuthenticated) { // Corrected to authStore
    next({ name: 'Login' });
  } else if (to.name === 'Login' && authStore.isAuthenticated) { // Corrected to authStore
    next({ name: 'Home' }); // Redirect to Home after login, or AutoTest if preferred
  } else {
    next();
  }
});

export default router;