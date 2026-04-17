<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="logo" @click="goHome">
          <img src="/仓酷家Alogo.png" alt="仓酷家" class="logo-img" />
        </div>
        <div class="nav-menu">
          <a href="#features" class="nav-link">功能特点</a>
          <a href="#story" class="nav-link">产品故事</a>
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
        <div class="hero-left">
          <h1 class="hero-title">
            中小仓库的3D规划设计神器
          </h1>
          <p class="hero-subtitle">
            不用学 CAD，不用等规划部。<br>
            10 分钟零基础拖拽，快速生成 3D 效果图与实施清单。<br>
            所见即所得，人人都是物流规划师！
          </p>
          <div class="hero-actions">
            <button class="btn-large btn-primary" @click="enterApp">
              免费开始使用
              <span class="arrow">→</span>
            </button>
          </div>
        </div>
        <div class="hero-right">
          <!-- 背景图在右侧 -->
        </div>
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
          <span class="stat-number">10min</span>
          <span class="stat-label">快速出图</span>
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
            <div class="feature-icon">📚</div>
            <h3>丰富模型库</h3>
            <p>货架、叉车、托盘等1000+专业物流设备模型</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h3>3D可视化设计</h3>
            <p>实时3D渲染，所见即所得，让仓库规划更直观</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>标准案例库</h3>
            <p>电商仓、冷链仓、制造业仓库等标准模板一键使用</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>快速出图</h3>
            <p>拖拽式操作，10分钟完成专业级效果图输出</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🖼️</div>
            <h3>专业级3D效果图演示</h3>
            <p>3D视角随意切换、360度角度任意旋转，专业级3D效果图展示，一切尽在不言中！</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>项目实施清单</h3>
            <p>自动生成设备清单和实施方案，助力项目落地</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 产品背后的故事 -->
    <section id="story" class="story">
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
              <p>我决定自己开发——仓酷家，真正做到不用学CAD、不用搞复杂的3D建模，只需要简单拖拽，10分钟即可输出自己专业的3D效果图，以及实施清单，按图施工，让人人都成为优秀的物流规划师！</p>
            </div>
            <p class="story-paragraph belief">
              相信我，这就是你需要的专业、高效、易用的3D仓库设计工具！
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

    <!-- CTA + 页脚合并区域 -->
    <section class="cta-footer">
      <div class="cta-footer-container">
        <!-- CTA 内容 -->
        <div class="cta-content">
          <h2>准备好开始您的仓库设计了吗？</h2>
          <p>立即免费使用仓酷家，10分钟输出专业3D效果图</p>
          <button class="btn-large btn-primary" @click="enterApp">
            免费开始使用
            <span class="arrow">→</span>
          </button>
        </div>

        <!-- 页脚链接 -->
        <div class="footer-links-section">
          <div class="footer-brand">
            <div class="logo">
              <img src="/仓酷家Alogo.png" alt="仓酷家" class="logo-img" />
            </div>
            <p>专业、高效、易用的3D仓库设计工具</p>
            <p class="footer-email">anderson2026@163.com（欢迎交流）</p>
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

        <!-- 版权信息 -->
        <div class="footer-bottom">
          <p>© 2026 仓酷家. All rights reserved. | 沪ICP备2026013469号</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 进入应用
const enterApp = () => {
  router.push('/editor');
};

// 返回首页
const goHome = () => {
  router.push('/');
};

// 登录
const handleLogin = () => {
  router.push('/sign-in');
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
  background: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  height: 100px;
  display: flex;
  align-items: center;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
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
  height: 80px;
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
  min-height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4rem 4rem 2rem;
  margin-top: 100px;
  background: url('/仓酷家首页背景图2.png') center/cover no-repeat;
  position: relative;
  overflow: hidden;
}

.hero-content {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
  flex: 1;
}

.hero-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 2rem;
}

.hero-right {
  /* 右侧区域用于背景图展示 */
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.2;
  color: #1E1E1E;
  margin-bottom: 1.5rem;
  white-space: nowrap;
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
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.hero-stats {
  display: flex;
  gap: 3rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 0;
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

/* 功能特点 */
.features {
  padding: 6rem 2rem;
  background: #F0F5FF;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  text-align: center;
  color: #1E1E1E;
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
  background: #ffffff;
  border-radius: 16px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(67, 97, 238, 0.2);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  color: #1E1E1E;
  margin-bottom: 0.75rem;
}

.feature-card p {
  color: #6b6b8a;
  line-height: 1.6;
}



/* 产品背后的故事 */
.story {
  padding: 6rem 2rem;
  background: linear-gradient(180deg, #F8F8F6 0%, #f5f0e6 100%);
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
  color: #1E1E1E;
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
  color: #1E1E1E;
  font-weight: 500;
  line-height: 1.8;
  margin: 0;
}

.story-paragraph.belief {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1E1E1E;
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
  color: #1E1E1E;
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

/* CTA + 页脚合并区域 */
.cta-footer {
  min-height: calc(100vh - 100px);
  padding: 4rem 2rem 2rem;
  background: #f0f0e6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cta-footer-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* CTA 内容 */
.cta-content {
  text-align: center;
  margin-bottom: 4rem;
}

.cta-content h2 {
  font-size: 2.5rem;
  color: #1E1E1E;
  margin-bottom: 1rem;
}

.cta-content p {
  color: #4a4a68;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.cta-content .btn-primary {
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
}

.cta-content .btn-primary:hover {
  background: linear-gradient(135deg, #3a0ca3 0%, #4361ee 100%);
  box-shadow: 0 8px 25px rgba(67, 97, 238, 0.4);
}

/* 页脚链接区域 */
.footer-links-section {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 4rem;
  margin-bottom: 3rem;
  padding-top: 3rem;
  border-top: 1px solid #d0d0c6;
}

.footer-brand .logo {
  margin-bottom: 1rem;
}

.footer-brand .logo-img {
  height: 100px;
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
  color: #1E1E1E;
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
  border-top: 1px solid #d0d0c6;
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
