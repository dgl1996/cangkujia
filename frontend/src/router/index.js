import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import CoreFunction from '../views/CoreFunction.vue';
import ModelLibrary from '../views/ModelLibrary.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/editor',
    name: 'CoreFunction',
    component: CoreFunction
  },
  {
    path: '/models',
    name: 'ModelLibrary',
    component: ModelLibrary
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
