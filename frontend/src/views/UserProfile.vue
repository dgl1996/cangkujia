<template>
  <div class="profile-container">
    <div class="profile-box">
      <h1>用户中心</h1>
      
      <!-- 自定义用户信息展示 -->
      <div class="user-info-card" v-if="userStore.user">
        <div class="user-header">
          <div class="avatar">
            {{ userStore.user.username?.charAt(0)?.toUpperCase() || 'U' }}
          </div>
          <div class="user-meta">
            <h2 class="username">{{ userStore.user.username || '用户' }}</h2>
            <p class="email">{{ userStore.user.email }}</p>
            <span class="user-id">ID: {{ userStore.user.id }}</span>
          </div>
        </div>
        
        <div class="membership-info">
          <div class="info-row">
            <span class="label">会员状态：</span>
            <span class="value" :class="userStore.isPro ? 'pro' : 'free'">
              {{ userStore.isPro ? 'Pro 会员' : '免费版' }}
            </span>
          </div>
          <div class="info-row" v-if="userStore.isPro && userStore.expireAt">
            <span class="label">到期时间：</span>
            <span class="value">{{ formatExpireDate(userStore.expireAt) }}</span>
          </div>
          <div class="info-row">
            <span class="label">注册时间：</span>
            <span class="value">{{ formatDate(userStore.user.created_at) }}</span>
          </div>
        </div>
        
        <div class="action-buttons">
          <button v-if="!userStore.isPro" class="btn-upgrade" @click="goPricing">
            升级会员
          </button>
          <button class="btn-logout" @click="handleLogout">
            退出登录
          </button>
        </div>
      </div>
      
      <div class="not-login" v-else>
        <p>您尚未登录</p>
        <router-link to="/sign-in" class="btn-login">去登录</router-link>
      </div>
      
      <div class="actions">
        <router-link to="/" class="btn-back">返回首页</router-link>
        <router-link to="/editor" class="btn-editor">进入编辑器</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN');
};

const formatExpireDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const goPricing = () => {
  router.push('/pricing');
};

const handleLogout = () => {
  userStore.logout();
};
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.profile-box {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

/* 用户信息卡片 */
.user-info-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e9ecef;
}

.avatar {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.user-meta {
  flex: 1;
}

.username {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
}

.email {
  font-size: 14px;
  color: #666;
  margin: 0 0 4px 0;
}

.user-id {
  font-size: 12px;
  color: #999;
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 4px;
}

/* 会员信息 */
.membership-info {
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e9ecef;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  color: #666;
  font-size: 14px;
}

.value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.value.pro {
  color: #10b981;
  font-weight: 600;
}

.value.free {
  color: #f59e0b;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-upgrade {
  flex: 1;
  padding: 12px 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-upgrade:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-logout {
  flex: 1;
  padding: 12px 24px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #fecaca;
}

/* 未登录状态 */
.not-login {
  text-align: center;
  padding: 40px 0;
}

.not-login p {
  color: #666;
  margin-bottom: 16px;
}

.btn-login {
  display: inline-block;
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 底部导航 */
.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-back,
.btn-editor {
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-back {
  background: #f3f4f6;
  color: #666;
}

.btn-back:hover {
  background: #e5e7eb;
}

.btn-editor {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-editor:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

@media (max-width: 480px) {
  .profile-box {
    padding: 24px;
  }
  
  .user-header {
    flex-direction: column;
    text-align: center;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>
