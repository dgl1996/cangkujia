<template>
  <div class="sign-up-container">
    <div class="sign-up-box">
      <h1>注册</h1>
      <p class="subtitle">创建您的仓酷家账号</p>

      <SignUp
        routing="path"
        path="/sign-up"
        signUpForceRedirectUrl="/editor"
        :appearance="{
          elements: {
            formButtonPrimary: 'clerk-button-primary',
            card: 'clerk-card',
            headerTitle: 'clerk-header-title',
            headerSubtitle: 'clerk-header-subtitle'
          }
        }"
      />

      <div class="links">
        <router-link to="/sign-in">已有账号？立即登录</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { SignUp } from '@clerk/vue';
</script>

<style scoped>
.sign-up-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.sign-up-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 8px;
  font-size: 28px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.links {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: center;
}

.links a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.links a:hover {
  color: #764ba2;
  text-decoration: underline;
}

:deep(.clerk-button-primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

:deep(.clerk-button-primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.clerk-card) {
  border: none;
  box-shadow: none;
  padding: 0;
}

:deep(.clerk-header-title) {
  display: none;
}

:deep(.clerk-header-subtitle) {
  display: none;
}
</style>
