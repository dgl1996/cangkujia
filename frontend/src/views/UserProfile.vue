<template>
  <div class="profile-container">
    <div class="profile-box">
      <h1>用户中心</h1>
      
      <UserProfile 
        :appearance="{
          elements: {
            card: 'clerk-card',
            headerTitle: 'clerk-header-title'
          }
        }"
      />
      
      <div class="actions">
        <router-link to="/" class="btn-back">返回首页</router-link>
        <router-link to="/editor" class="btn-editor">进入编辑器</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { UserProfile } from '@clerk/vue';
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.profile-box {
  max-width: 800px;
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

.actions {
  margin-top: 30px;
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-back, .btn-editor {
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-back {
  background: #f3f4f6;
  color: #374151;
}

.btn-back:hover {
  background: #e5e7eb;
  transform: translateY(-2px);
}

.btn-editor {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-editor:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.clerk-card) {
  border: none;
  box-shadow: none;
}

:deep(.clerk-header-title) {
  display: none;
}
</style>
