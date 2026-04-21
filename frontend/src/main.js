import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { clerkPlugin } from '@clerk/vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

// Clerk 配置 - 从环境变量读取Key
const clerkConfig = {
  publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
  signInUrl: '/sign-in',
  signUpUrl: '/sign-up',
  signInForceRedirectUrl: '/editor',
  signUpForceRedirectUrl: '/editor',
  routerPush: (to) => router.push(to),
};

app.use(createPinia());
app.use(router);
app.use(clerkPlugin, clerkConfig);

app.mount('#app');
