<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <nav class="navbar" :class="{ 'scrolled': isScrolled }">
      <div class="nav-container">
        <div class="logo" @click="goHome">
          <img src="/LOGO.png" alt="仓酷家" class="logo-img" />
        </div>
        <div class="nav-menu">
          <a href="#features" class="nav-link">功能特点</a>
          <a href="#cases" class="nav-link">案例展示</a>
          <a href="#standards" class="nav-link">标准规范</a>
        </div>
        <div class="nav-actions">
          <button class="btn-login" @click="handleLogin">登录</button>
          <button class="btn-primary" @click="enterApp">开始使用</button>
        </div>
      </div>
    </nav>

    <!-- Hero 区域 -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          中小仓库的美图秀秀
        </h1>
        <p class="hero-subtitle">
          5分钟拖拽输出3D仓库规划效果图和实施清单，不用学CAD，不用等规划部出图，人人都是物流规划师！
        </p>
        <div class="hero-actions">
          <button class="btn-large btn-primary" @click="enterApp">
            免费开始使用
            <span class="arrow">→</span>
          </button>
          <button class="btn-large btn-secondary" @click="scrollToCases">
            查看案例
          </button>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">1000+</span>
            <span class="stat-label">3D物流模型</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">50+</span>
            <span class="stat-label">仓库类型模板</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">5min</span>
            <span class="stat-label">快速出图</span>
          </div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="warehouse-preview">
          <div class="preview-3d">
            <div class="floating-shelf shelf-1">📦</div>
            <div class="floating-shelf shelf-2">📦</div>
            <div class="floating-shelf shelf-3">🚛</div>
            <div class="grid-floor"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 功能特点 -->
    <section id="features" class="features">
      <div class="section-container">
        <h2 class="section-title">为什么选择仓酷家？</h2>
        <p class="section-subtitle">专业、高效、易用的3D仓库设计工具</p>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>标准案例库</h3>
            <p>电商仓、冷链仓、制造业仓库等标准模板一键使用</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3>丰富模型库</h3>
            <p>货架、叉车、托盘等1000+专业物流设备模型</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📐</div>
            <h3>平面图导入</h3>
            <p>支持手绘图纸导入，快速构建仓库功能分区</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h3>3D可视化设计</h3>
            <p>实时3D渲染，所见即所得，让仓库规划更直观</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>快速出图</h3>
            <p>拖拽式操作，5分钟完成专业级效果图输出</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>项目实施清单</h3>
            <p>自动生成设备清单和实施方案，助力项目落地</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 案例展示 -->
    <section id="cases" class="cases">
      <div class="section-container">
        <h2 class="section-title">优秀案例展示</h2>
        <p class="section-subtitle">看看其他用户如何使用仓酷家</p>
        <div class="cases-grid">
          <div class="case-card">
            <div class="case-image">
              <div class="case-placeholder">
                <span>🏭</span>
                <p>电商物流中心</p>
              </div>
            </div>
            <div class="case-info">
              <h3>大型电商物流中心</h3>
              <p>5000㎡智能仓储布局设计</p>
              <div class="case-tags">
                <span class="tag">电商仓</span>
                <span class="tag">AS/RS</span>
              </div>
            </div>
          </div>
          <div class="case-card">
            <div class="case-image">
              <div class="case-placeholder">
                <span>❄️</span>
                <p>冷链仓库</p>
              </div>
            </div>
            <div class="case-info">
              <h3>生鲜冷链配送中心</h3>
              <p>多温区冷链仓库规划设计</p>
              <div class="case-tags">
                <span class="tag">冷链仓</span>
                <span class="tag">多温区</span>
              </div>
            </div>
          </div>
          <div class="case-card">
            <div class="case-image">
              <div class="case-placeholder">
                <span>🏗️</span>
                <p>制造业仓库</p>
              </div>
            </div>
            <div class="case-info">
              <h3>汽车零部件仓库</h3>
              <p>制造业原材料与成品仓设计</p>
              <div class="case-tags">
                <span class="tag">制造业</span>
                <span class="tag">高密度</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 产品背后的故事 -->
    <section class="story">
      <div class="section-container">
        <div class="story-header">
          <span class="story-label">产品背后的故事</span>
          <h2 class="story-title">从物流高管、运营管理专家到AI极客</h2>
        </div>
        <div class="story-content">
          <div class="story-text">
            <p class="story-paragraph">
              作为一名1975年出生的资深物流高管和运营管理专家，我在物流行业深耕了20多年，深知普通物流管理人员对中小仓库日常频繁的规划布局和优化调整的不便和困难，讲不清楚、说不明白、画不出来.......因此
            </p>
            <div class="story-highlight-box">
              <p>我决定自己开发——仓酷家，真正做到不用学CAD、不用搞复杂的3D建模，只需要简单拖拽，5分钟即可输出自己专业的3D效果图，以及实施清单，按图施工，让人人都成为优秀的物流规划师！</p>
            </div>
            <p class="story-paragraph belief">
              相信我，这就是你需要的极致效率工具！
            </p>
            <div class="story-author">
              <div class="author-icon">
                <span>✦</span>
              </div>
              <div class="author-info">
                <h4>安德森（董国礼）</h4>
                <p>产品设计师（前京东、阿里生态物流高管，运营管理专家）</p>
              </div>
            </div>
          </div>
          <div class="story-image">
            <div class="image-wrapper">
              <img src="/anderson.jpg" alt="安德森 - 仓酷家创始人" />
              <div class="image-caption">
                <span class="caption-title">为什么做仓酷家？</span>
                <p class="caption-text">26年物流老兵亲自下场、为物流兄弟们打造一把日常仓库规划的利器！</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 区域 -->
    <section class="cta">
      <div class="cta-container">
        <h2>准备好开始您的仓库设计了吗？</h2>
        <p>立即免费使用仓酷家，5分钟输出专业3D效果图</p>
        <button class="btn-large btn-primary" @click="enterApp">
          免费开始使用
          <span class="arrow">→</span>
        </button>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-brand">
          <div class="logo">
            <img src="/LOGO.png" alt="仓酷家" class="logo-img" />
          </div>
          <p>专业的3D物流仓库设计工具</p>
          <p class="footer-email">anderson2026@163.com</p>
        </div>
        <div class="footer-links">
          <div class="link-group">
            <h4>产品</h4>
            <a href="#">功能介绍</a>
            <a href="#">模型库</a>
            <a href="#">案例库</a>
          </div>
          <div class="link-group">
            <h4>支持</h4>
            <a href="#">使用文档</a>
            <a href="#">常见问题</a>
            <a href="#">联系我们</a>
            <a href="#">反馈建议</a>
          </div>
          <div class="link-group">
            <h4>法律信息</h4>
            <a href="#">关于我们</a>
            <a href="#">隐私政策</a>
            <a href="#">服务条款</a>
            <a href="#">授权协议</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 仓酷家. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isScrolled = ref(false);

// 监听滚动事件
const handleScroll = () => {
  isScrolled.value = window.scrollY > 50;
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

// 进入应用
const enterApp = () => {
  router.push('/usage');
};

// 返回首页
const goHome = () => {
  router.push('/');
};

// 登录
const handleLogin = () => {
  alert('登录功能开发中...');
};

// 滚动到案例
const scrollToCases = () => {
  document.getElementById('cases')?.scrollIntoView({ behavior: 'smooth' });
};
</script>

<style scoped>
/* 基础样式 */
.home-page {
  min-height: 100vh;
  background: #ffffff;
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: transparent;
  transition: all 0.3s ease;
  padding: 1rem 0;
}

.navbar.scrolled {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 0.5rem 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-img {
  height: 120px;
  width: auto;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #4a4a68;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #4361ee;
}

.nav-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* 按钮样式 */
.btn-login {
  padding: 0.5rem 1.5rem;
  border: none;
  background: transparent;
  color: #4a4a68;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s;
}

.btn-login:hover {
  color: #4361ee;
}

.btn-primary {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(67, 97, 238, 0.4);
}

.btn-secondary {
  padding: 0.5rem 1.5rem;
  border: 2px solid #4361ee;
  border-radius: 8px;
  background: transparent;
  color: #4361ee;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #4361ee;
  color: white;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.arrow {
  transition: transform 0.3s;
}

.btn-primary:hover .arrow {
  transform: translateX(4px);
}

/* Hero 区域 */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 6rem 2rem 4rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 80%;
  height: 150%;
  background: radial-gradient(ellipse, rgba(67, 97, 238, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  width: 100%;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.2;
  color: #1a1a2e;
  margin-bottom: 1.5rem;
}

.highlight {
  display: block;
  background: linear-gradient(135deg, #4361ee 0%, #f72585 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #4a4a68;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
}

.hero-stats {
  display: flex;
  gap: 3rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: #4361ee;
}

.stat-label {
  font-size: 0.9rem;
  color: #6b6b8a;
}

/* 3D预览区域 */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.warehouse-preview {
  width: 100%;
  max-width: 500px;
  aspect-ratio: 1;
  position: relative;
}

.preview-3d {
  width: 100%;
  height: 100%;
  position: relative;
  perspective: 1000px;
}

.floating-shelf {
  position: absolute;
  font-size: 4rem;
  animation: float 3s ease-in-out infinite;
}

.shelf-1 {
  top: 20%;
  left: 20%;
  animation-delay: 0s;
}

.shelf-2 {
  top: 40%;
  right: 20%;
  animation-delay: 0.5s;
}

.shelf-3 {
  bottom: 30%;
  left: 40%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotateY(0deg);
  }
  50% {
    transform: translateY(-20px) rotateY(10deg);
  }
}

.grid-floor {
  position: absolute;
  bottom: 10%;
  left: 10%;
  right: 10%;
  height: 40%;
  background: 
    linear-gradient(90deg, rgba(67, 97, 238, 0.1) 1px, transparent 1px),
    linear-gradient(rgba(67, 97, 238, 0.1) 1px, transparent 1px);
  background-size: 40px 40px;
  transform: perspective(500px) rotateX(60deg);
  animation: grid-move 10s linear infinite;
}

@keyframes grid-move {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 40px 40px;
  }
}

/* 功能特点 */
.features {
  padding: 6rem 2rem;
  background: #ffffff;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  text-align: center;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.section-subtitle {
  text-align: center;
  color: #6b6b8a;
  font-size: 1.1rem;
  margin-bottom: 4rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.feature-card {
  padding: 2rem;
  background: #f8f9ff;
  border-radius: 16px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(67, 97, 238, 0.15);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  color: #1a1a2e;
  margin-bottom: 0.75rem;
}

.feature-card p {
  color: #6b6b8a;
  line-height: 1.6;
}

/* 案例展示 */
.cases {
  padding: 6rem 2rem;
  background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%);
}

.cases-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.case-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.case-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.case-image {
  aspect-ratio: 16/10;
  background: linear-gradient(135deg, #e8ecff 0%, #d4d9ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-placeholder {
  text-align: center;
  color: #4361ee;
}

.case-placeholder span {
  font-size: 4rem;
  display: block;
  margin-bottom: 0.5rem;
}

.case-info {
  padding: 1.5rem;
}

.case-info h3 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.case-info p {
  color: #6b6b8a;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.case-tags {
  display: flex;
  gap: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  background: #e8ecff;
  color: #4361ee;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* 产品背后的故事 */
.story {
  padding: 6rem 2rem;
  background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%);
}

.story-header {
  text-align: center;
  margin-bottom: 3rem;
}

.story-label {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.story-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1a1a2e;
  line-height: 1.3;
}

.story-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.story-text {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.story-paragraph {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #4a4a68;
}

.story-highlight-box {
  padding: 1.5rem;
  background: linear-gradient(135deg, #e8ecff 0%, #d4d9ff 100%);
  border-radius: 12px;
  border-left: 4px solid #4361ee;
}

.story-highlight-box p {
  color: #1a1a2e;
  font-weight: 500;
  line-height: 1.8;
  margin: 0;
}

.story-paragraph.belief {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a2e;
  font-style: italic;
}

.story-author {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e8ecff;
}

.author-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(67, 97, 238, 0.4);
}

.author-icon span {
  font-size: 1.5rem;
  color: white;
}

.author-info h4 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 0.25rem;
}

.author-info p {
  font-size: 0.9rem;
  color: #6b6b8a;
}

.story-image {
  display: flex;
  justify-content: center;
}

.image-wrapper {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  max-width: 500px;
}

.image-wrapper img {
  width: 100%;
  height: auto;
  display: block;
}

.image-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.6) 60%, transparent 100%);
  color: white;
  padding: 3rem 1.5rem 1.5rem;
}

.caption-title {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #fff;
}

.caption-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
}

/* CTA 区域 */
.cta {
  padding: 6rem 2rem;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  text-align: center;
}

.cta-container {
  max-width: 600px;
  margin: 0 auto;
}

.cta h2 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 1rem;
}

.cta p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.cta .btn-primary {
  background: white;
  color: #4361ee;
}

.cta .btn-primary:hover {
  background: #f8f9ff;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

/* 页脚 */
.footer {
  background: #1a1a2e;
  color: white;
  padding: 4rem 2rem 2rem;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 4rem;
  margin-bottom: 3rem;
}

.footer-brand .logo {
  margin-bottom: 1rem;
}

.footer-brand .logo-img {
  height: 150px;
}

.footer-brand p {
  color: #6b6b8a;
}

.footer-email {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #4361ee !important;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.link-group h4 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: white;
}

.link-group a {
  display: block;
  color: #6b6b8a;
  text-decoration: none;
  margin-bottom: 0.5rem;
  transition: color 0.3s;
}

.link-group a:hover {
  color: #4361ee;
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 2rem;
  border-top: 1px solid #2a2a3e;
  text-align: center;
  color: #6b6b8a;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-stats {
    justify-content: center;
  }

  .hero-visual {
    display: none;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .cases-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .story-content {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .story-title {
    font-size: 2rem;
  }

  .story-image {
    order: -1;
  }
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-stats {
    flex-direction: column;
    gap: 1.5rem;
    align-items: center;
  }

  .features-grid,
  .cases-grid {
    grid-template-columns: 1fr;
  }

  .footer-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .footer-links {
    grid-template-columns: repeat(2, 1fr);
  }

  .cta h2 {
    font-size: 1.75rem;
  }

  .story-title {
    font-size: 1.5rem;
  }

  .story-paragraph {
    font-size: 1rem;
  }

  .image-caption {
    padding: 2rem 1rem 1rem;
  }

  .caption-title {
    font-size: 1rem;
  }

  .caption-text {
    font-size: 0.8rem;
  }
}
</style>
