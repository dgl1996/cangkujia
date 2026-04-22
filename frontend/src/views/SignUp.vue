<template>
  <div class="sign-up-container">
    <div class="sign-up-box">
      <h1>注册</h1>
      <p class="subtitle">创建您的仓酷家账号</p>

      <!-- 升级引导文案 -->
      <div class="upgrade-banner">
        <h2 class="upgrade-title">🎉 升级会员，保存您的仓库设计</h2>
        <p class="upgrade-subtitle">免费版可无限设计，保存项目需升级</p>
        <p class="upgrade-tip">💡 请使用真实邮箱注册，用于找回密码和接收会员通知</p>
      </div>

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

      <!-- 底部价格提示 -->
      <div class="pricing-hint">
        <span class="pricing-badge">Pro版 ¥168/年（最佳性价比）</span>
      </div>

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
  min-height: 350px; /* 确保表单区域有足够高度 */
}

/* 只隐藏Clerk自带的标题，不隐藏表单元素 */
:deep(.clerk-header-title) {
  display: none;
}

:deep(.clerk-header-subtitle) {
  display: none;
}

/* 确保Clerk表单输入框可见 */
:deep(.clerk-form-field) {
  display: block !important;
  visibility: visible !important;
}

:deep(.clerk-form-field input) {
  display: block !important;
  visibility: visible !important;
  width: 100%;
}

/* 升级引导样式 */
.upgrade-banner {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  text-align: center;
}

.upgrade-title {
  font-size: 16px;
  font-weight: 600;
  color: #0369a1;
  margin: 0 0 8px 0;
}

.upgrade-subtitle {
  font-size: 14px;
  color: #0ea5e9;
  margin: 0 0 8px 0;
}

.upgrade-tip {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.pricing-hint {
  text-align: center;
  margin: 16px 0;
}

.pricing-badge {
  display: inline-block;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}
</style>
