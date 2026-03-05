import { createRouter, createWebHistory } from 'vue-router';
import CoreFunction from '../views/CoreFunction.vue';

const routes = [
  {
    path: '/',
    name: 'CoreFunction',
    component: CoreFunction
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;