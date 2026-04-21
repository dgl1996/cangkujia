import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { clerkPlugin } from '@clerk/vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

// Clerk 配置
const clerkConfig = {
  publishableKey: 'pk_live_Y2xlcmsuY2FuZ2t1amlhNjY2LmNvbSQ',
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
