<template>
  <div class="product-usage">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="logo" @click="goHome">
          <img src="/仓酷家Alogo.png" alt="仓酷家" class="logo-img" />
        </div>
        <div class="nav-title">产品使用</div>
        <div class="nav-actions">
          <button class="btn-secondary" @click="goHome">返回首页</button>
        </div>
      </div>
    </nav>

    <!-- 主体内容 -->
    <div class="main-content">
      <div class="welcome-section">
        <h1>欢迎使用仓酷家</h1>
        <p>选择您需要的功能模块，开始您的仓库设计之旅</p>
      </div>

      <!-- 功能模块网格 -->
      <div class="modules-grid">
        <!-- P1 设计工作台 -->
        <div class="module-card primary" @click="goTo('/editor')">
          <div class="module-icon">🎨</div>
          <h3>设计工作台</h3>
          <p>3D仓库布局设计核心功能，包含模型库和仓库对象</p>
          <div class="module-badge">核心</div>
        </div>

        <!-- P2 3D物流对象库 -->
        <div class="module-card" @click="goTo('/models')">
          <div class="module-icon">📦</div>
          <h3>3D物流对象库</h3>
          <p>40+物流设备模型，支持自定义货架参数</p>
          <div class="module-badge">可用</div>
        </div>

        <!-- P4 仓库案例库 -->
        <div class="module-card" @click="goTo('/cases')">
          <div class="module-icon">📚</div>
          <h3>仓库案例库</h3>
          <p>优秀仓库设计案例展示</p>
          <div class="module-badge soon">即将上线</div>
        </div>

        <!-- P5 物流规范库 -->
        <div class="module-card" @click="goTo('/standards')">
          <div class="module-icon">📋</div>
          <h3>物流规范库</h3>
          <p>物流行业标准与规范</p>
          <div class="module-badge soon">即将上线</div>
        </div>

        <!-- P6 我的作品 -->
        <div class="module-card" @click="goTo('/my-works')">
          <div class="module-icon">💼</div>
          <h3>我的作品</h3>
          <p>管理您的仓库设计方案</p>
          <div class="module-badge soon">即将上线</div>
        </div>

        <!-- P7 标准案例 -->
        <div class="module-card" @click="goTo('/standard-cases')">
          <div class="module-icon">⭐</div>
          <h3>标准案例</h3>
          <p>电商仓、冷链仓等标准模板</p>
          <div class="module-badge soon">即将上线</div>
        </div>

        <!-- P8 本周热门 -->
        <div class="module-card" @click="goTo('/hot')">
          <div class="module-icon">🔥</div>
          <h3>本周热门</h3>
          <p>热门仓库设计作品展示</p>
          <div class="module-badge soon">即将上线</div>
        </div>

        <!-- P9 用户中心 -->
        <div class="module-card" @click="goTo('/user')">
          <div class="module-icon">👤</div>
          <h3>用户中心</h3>
          <p>账户管理、订阅服务</p>
          <div class="module-badge soon">即将上线</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  router.push('/');
};

const goTo = (path) => {
  // 如果路径是即将上线的功能，显示提示
  if (path.includes('warehouse-models') || 
      path.includes('cases') || 
      path.includes('standards') || 
      path.includes('my-works') || 
      path.includes('standard-cases') || 
      path.includes('hot') || 
      path.includes('user')) {
    alert('该功能即将上线，敬请期待！');
    return;
  }
  router.push(path);
};
</script>

<style scoped>
.product-usage {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
}

/* 导航栏 */
.navbar {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-img {
  height: 40px;
  width: auto;
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  border: 1px solid #4361ee;
  border-radius: 6px;
  background: white;
  color: #4361ee;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #4361ee;
  color: white;
}

/* 主体内容 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-section h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 0.75rem;
}

.welcome-section p {
  font-size: 1.1rem;
  color: #6b6b8a;
}

/* 功能模块网格 */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.module-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
}

.module-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(67, 97, 238, 0.15);
}

.module-card.primary {
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
}

.module-card.primary h3,
.module-card.primary p {
  color: white;
}

.module-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.module-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.module-card p {
  font-size: 0.9rem;
  color: #6b6b8a;
  line-height: 1.5;
}

.module-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  background: #e8ecff;
  color: #4361ee;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.module-badge.soon {
  background: #fff3cd;
  color: #856404;
}

/* 响应式 */
@media (max-width: 1024px) {
  .modules-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-section h1 {
    font-size: 1.75rem;
  }
}
</style>
