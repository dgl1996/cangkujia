<template>
  <div class="sign-in-container">
    <div class="sign-in-box">
      <h1>登录</h1>
      <p class="subtitle">欢迎回到仓酷家</p>

      <!-- 升级引导文案 -->
      <div class="upgrade-banner">
        <h2 class="upgrade-title">🎉 升级会员，保存您的仓库设计</h2>
        <p class="upgrade-subtitle">免费版可无限设计，保存项目需升级</p>
        <p class="upgrade-tip">💡 请使用真实邮箱注册，用于找回密码和接收会员通知</p>
      </div>

      <!-- 检查登录状态中 -->
      <div v-if="isCheckingAuth" class="loading-state">
        <div class="spinner"></div>
        <p>正在检查登录状态...</p>
      </div>

      <!-- 自定义登录表单 -->
      <form v-else @submit.prevent="handleSubmit" class="custom-form">
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="请输入邮箱"
            required
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="isSubmitting"
          />
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button
          type="submit"
          class="submit-btn"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting">登录中...</span>
          <span v-else>登录</span>
        </button>
      </form>

      <!-- 底部价格提示 -->
      <div class="pricing-hint">
        <span class="pricing-badge">Pro版 ¥168/年（最佳性价比）</span>
      </div>

      <div class="links">
        <router-link to="/sign-up">还没有账号？立即注册</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';

const router = useRouter();
const userStore = useUserStore();

// 表单数据
const email = ref('');
const password = ref('');

// 状态
const isSubmitting = ref(false);
const errorMessage = ref('');
const isCheckingAuth = ref(true); // 正在检查登录状态

// 进入登录页时，检查是否已有有效 token
onMounted(async () => {
  const token = localStorage.getItem('cangkujia_token');
  
  if (token) {
    try {
      // 验证 token 是否有效
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        // token 有效，更新用户状态并跳转工作台
        userStore.setUser(userData);
        router.push('/editor');
        return;
      }
    } catch (error) {
      console.error('Token 验证失败:', error);
    }
  }
  
  // 没有 token 或 token 无效，显示登录表单
  isCheckingAuth.value = false;
});

// 处理登录提交
async function handleSubmit() {
  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || '登录失败');
    }

    // 保存 token 到 localStorage
    localStorage.setItem('cangkujia_token', data.access_token);

    // 更新用户状态
    userStore.setUser(data.user);

    // 检查订阅状态（确保Pro状态正确显示）
    await userStore.checkSubscription();

    // 跳转到工作台
    router.push('/editor');
  } catch (error) {
    console.error('登录失败:', error);
    errorMessage.value = error.message || '登录失败，请重试';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.sign-in-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.sign-in-box {
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

/* 自定义表单 */
.custom-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

/* 错误提示 */
.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

/* 提交按钮 */
.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

/* 加载状态样式 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  gap: 16px;
}

.loading-state p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
