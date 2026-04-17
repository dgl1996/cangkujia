import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { clerkPlugin } from '@clerk/vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

// Clerk 配置
const clerkConfig = {
  publishableKey: 'pk_test_Y2hlZXJmdWwtZmx5LTc0LmNsZXJrLmFjY291bnRzLmRldiQ',
  signInUrl: '/sign-in',
  signUpUrl: '/sign-up',
  afterSignInUrl: '/',
  afterSignUpUrl: '/',
};

app.use(createPinia());
app.use(router);
app.use(clerkPlugin, clerkConfig);

app.mount('#app');
