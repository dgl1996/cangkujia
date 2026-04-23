import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { clerkPlugin } from '@clerk/vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

// Clerk 配置 - 从环境变量读取Key
// clerkJSUrl 指向本地打包的 clerk-js，避免从境外CDN加载被墙
const clerkConfig = {
  publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
  clerkJSUrl: '/clerk-js.js',  // 本地路径，Vite打包后会自动处理
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
