import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import ProductUsage from '../views/ProductUsage.vue';
import CoreFunction from '../views/CoreFunction.vue';
import ModelLibrary from '../views/ModelLibrary.vue';
import SignIn from '../views/SignIn.vue';
import SignUp from '../views/SignUp.vue';
import UserProfile from '../views/UserProfile.vue';
import PricingPage from '../views/PricingPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/usage',
    name: 'ProductUsage',
    component: ProductUsage
  },
  {
    path: '/editor',
    name: 'CoreFunction',
    component: CoreFunction,
    meta: { requiresAuth: true }
  },
  {
    path: '/models',
    name: 'ModelLibrary',
    component: ModelLibrary
  },
  {
    path: '/sign-in',
    name: 'SignIn',
    component: SignIn
  },
  {
    path: '/sign-in/factor-two',
    name: 'SignInFactorTwo',
    component: SignIn
  },
  {
    path: '/sign-up',
    name: 'SignUp',
    component: SignUp
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: PricingPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    // 检查用户是否登录的逻辑会在组件中处理
    next();
  } else {
    next();
  }
});

export default router;
