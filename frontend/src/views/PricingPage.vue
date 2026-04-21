<template>
  <div class="pricing-page">
    <!-- 头部 -->
    <header class="header">
      <div class="logo" @click="goHome">
        <span class="logo-icon">🏠</span>
        <span class="logo-text">仓酷家</span>
      </div>
      <nav class="nav">
        <button class="nav-btn" @click="goHome">首页</button>
        <button class="nav-btn" @click="goEditor">编辑器</button>
        <button class="nav-btn primary">定价</button>
      </nav>
      <div class="user-section">
        <button v-if="isSignedIn" class="nav-btn" @click="goProfile">用户中心</button>
        <button v-else class="login-btn" @click="goSignIn">登录</button>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="main-content">
      <!-- 标题区 -->
      <section class="hero-section">
        <h1 class="title">选择适合您的方案</h1>
        <p class="subtitle">免费体验全部功能，升级后可保存项目</p>
        <div class="billing-toggle">
          <span :class="{ active: !isYearly }">月付</span>
          <label class="switch">
            <input type="checkbox" v-model="isYearly">
            <span class="slider"></span>
          </label>
          <span :class="{ active: isYearly }">年付</span>
          <span class="save-badge" v-if="isYearly">省30%</span>
        </div>
      </section>

      <!-- 价格卡片 -->
      <section class="pricing-cards">
        <!-- 免费版 -->
        <div class="pricing-card free">
          <div class="card-header">
            <h3 class="plan-name">免费版</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">0</span>
              <span class="period">/永久</span>
            </div>
            <p class="plan-desc">体验全部功能</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>使用全部3D模型</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>自由创建仓库布局</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>实时3D预览</span>
              </li>
              <li class="feature-item disabled">
                <span class="cross">✗</span>
                <span>保存项目（升级后可用）</span>
              </li>
              <li class="feature-item disabled">
                <span class="cross">✗</span>
                <span>云端同步</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-free" @click="goEditor">免费体验</button>
          </div>
        </div>

        <!-- 月付 -->
        <div class="pricing-card">
          <div class="card-header">
            <h3 class="plan-name">月付会员</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">19.9</span>
              <span class="period">/月</span>
            </div>
            <p class="plan-desc">灵活按月付费</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>免费版全部功能</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>无限保存项目</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>云端自动同步</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>优先客服支持</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>新功能优先体验</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-primary" @click="createOrder('monthly')">立即开通</button>
          </div>
        </div>

        <!-- 首月特惠 -->
        <div class="pricing-card special">
          <div class="badge hot">新用户专享</div>
          <div class="card-header">
            <h3 class="plan-name">首月特惠</h3>
            <div class="price">
              <span class="original-price">¥19.9</span>
              <div class="current-price">
                <span class="currency">¥</span>
                <span class="amount">9.9</span>
                <span class="period">/首月</span>
              </div>
            </div>
            <p class="plan-desc">限新用户首次购买</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>月付会员全部权益</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>首月5折优惠</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>次月自动续费¥19.9</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>可随时取消</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-special" @click="createOrder('first_month')">立即抢购</button>
          </div>
        </div>

        <!-- 季度 -->
        <div class="pricing-card">
          <div class="card-header">
            <h3 class="plan-name">季度会员</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">49</span>
              <span class="period">/季度</span>
            </div>
            <p class="plan-desc">约 ¥16.3/月</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>月付会员全部权益</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>比月付省 ¥10.7</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>90天无忧使用</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-primary" @click="createOrder('quarterly')">立即开通</button>
          </div>
        </div>

        <!-- 半年（推荐） -->
        <div class="pricing-card recommended">
          <div class="badge recommended-badge">⭐ 推荐</div>
          <div class="card-header">
            <h3 class="plan-name">半年会员</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">89</span>
              <span class="period">/半年</span>
            </div>
            <p class="plan-desc">约 ¥14.8/月</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>月付会员全部权益</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>比月付省 ¥30.4</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>180天稳定服务</span>
              </li>
              <li class="feature-item highlight">
                <span class="check">✓</span>
                <span>性价比之选</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-recommended" @click="createOrder('half_year')">立即开通</button>
          </div>
        </div>

        <!-- 年付（默认选中） -->
        <div class="pricing-card popular">
          <div class="badge popular-badge">🔥 最佳性价比</div>
          <div class="card-header">
            <h3 class="plan-name">年度会员</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">168</span>
              <span class="period">/年</span>
            </div>
            <p class="plan-desc">约 ¥14/月，省 ¥70.8</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>月付会员全部权益</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>比月付省 ¥70.8</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>全年无忧使用</span>
              </li>
              <li class="feature-item highlight">
                <span class="check">✓</span>
                <span>最优惠价格</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-popular" @click="createOrder('yearly')">立即开通</button>
          </div>
        </div>

        <!-- 3年 -->
        <div class="pricing-card">
          <div class="card-header">
            <h3 class="plan-name">3年会员</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">399</span>
              <span class="period">/3年</span>
            </div>
            <p class="plan-desc">约 ¥11.1/月</p>
          </div>
          <div class="card-body">
            <ul class="features">
              <li class="feature-item">
                <span class="check">✓</span>
                <span>月付会员全部权益</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>比年付再省 ¥105</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>3年长期承诺</span>
              </li>
              <li class="feature-item">
                <span class="check">✓</span>
                <span>专属VIP标识</span>
              </li>
            </ul>
          </div>
          <div class="card-footer">
            <button class="btn btn-primary" @click="createOrder('three_year')">立即开通</button>
          </div>
        </div>
      </section>

      <!-- 常见问题 -->
      <section class="faq-section">
        <h2 class="section-title">常见问题</h2>
        <div class="faq-list">
          <div class="faq-item">
            <h4 class="faq-question">免费版和付费版有什么区别？</h4>
            <p class="faq-answer">免费版可以体验全部功能，但无法保存项目，刷新后数据会丢失。付费版可以无限保存项目并自动同步到云端。</p>
          </div>
          <div class="faq-item">
            <h4 class="faq-question">可以随时取消订阅吗？</h4>
            <p class="faq-answer">是的，您可以随时取消订阅，取消后仍可使用到当前付费周期结束。</p>
          </div>
          <div class="faq-item">
            <h4 class="faq-question">支持哪些支付方式？</h4>
            <p class="faq-answer">目前支持微信支付，后续将支持支付宝和银行卡支付。</p>
          </div>
          <div class="faq-item">
            <h4 class="faq-question">购买后可以退款吗？</h4>
            <p class="faq-answer">虚拟商品一经购买不支持退款，建议您先使用免费版体验功能。</p>
          </div>
        </div>
      </section>
    </main>

    <!-- 支付弹窗 -->
    <div v-if="showPaymentModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>确认订单</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="order-info">
            <div class="order-item">
              <span class="label">商品名称：</span>
              <span class="value">{{ selectedPlan?.name }}</span>
            </div>
            <div class="order-item">
              <span class="label">订单金额：</span>
              <span class="value price">¥{{ selectedPlan?.price }}</span>
            </div>
          </div>
          <div class="payment-method">
            <h4>选择支付方式</h4>
            <div class="method-options">
              <label class="method-option active">
                <input type="radio" name="payment" value="wechat" checked>
                <span class="method-icon">💳</span>
                <span class="method-name">微信支付</span>
              </label>
            </div>
          </div>
          <div v-if="qrCodeUrl" class="qr-code-section">
            <p>请使用微信扫描二维码支付</p>
            <img :src="qrCodeUrl" alt="支付二维码" class="qr-code">
            <p class="qr-tip">二维码有效期5分钟</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">取消</button>
          <button class="btn btn-primary" @click="confirmPayment" :disabled="loading">
            {{ loading ? '创建订单中...' : '确认支付' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2026 仓酷家 Cangkujia. All rights reserved.</p>
      <p>沪ICP备2026013469号</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@clerk/vue';

const router = useRouter();
const { isSignedIn, userId } = useAuth();

const isYearly = ref(true);
const showPaymentModal = ref(false);
const selectedPlan = ref(null);
const loading = ref(false);
const qrCodeUrl = ref('');

const planPrices = {
  monthly: { name: '月付会员', price: 19.9, code: 'monthly' },
  first_month: { name: '首月特惠', price: 9.9, code: 'first_month' },
  quarterly: { name: '季度会员', price: 49, code: 'quarterly' },
  half_year: { name: '半年会员', price: 89, code: 'half_year' },
  yearly: { name: '年度会员', price: 168, code: 'yearly' },
  three_year: { name: '3年会员', price: 399, code: 'three_year' }
};

const goHome = () => router.push('/');
const goEditor = () => router.push('/editor');
const goSignIn = () => router.push('/sign-in');

const createOrder = async (planType) => {
  if (!userId.value) {
    alert('请先登录后再购买');
    router.push('/sign-in');
    return;
  }

  selectedPlan.value = planPrices[planType];
  showPaymentModal.value = true;
  qrCodeUrl.value = '';
};

const confirmPayment = async () => {
  if (!selectedPlan.value) return;

  loading.value = true;
  try {
    const response = await fetch('/api/payment/create-order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId.value,
        amount: selectedPlan.value.price,
        product_name: selectedPlan.value.name,
        description: selectedPlan.value.code
      })
    });

    const result = await response.json();
    const data = result.data || result;
    if (data.code_url) {
      qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data.code_url)}`;
      // 开始轮询订单状态
      pollOrderStatus(data.order_no);
    } else {
      alert('创建订单失败：' + (result.message || result.error || '未知错误'));
    }
  } catch (error) {
    console.error('创建订单失败:', error);
    alert('创建订单失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const pollOrderStatus = async (orderNo) => {
  const checkStatus = async () => {
    try {
      const response = await fetch(`/api/payment/order-status/${orderNo}`);
      const result = await response.json();
      
      // 后端返回格式: { code: 0, data: { status: 'paid' } }
      const status = result.data?.status || result.status;
      
      if (status === 'paid') {
        alert('支付成功！感谢您的购买。');
        closeModal();
        router.push('/profile');
        return;
      } else if (status === 'failed') {
        alert('支付失败，请重试');
        return;
      }
      
      // 继续轮询
      setTimeout(checkStatus, 3000);
    } catch (error) {
      console.error('查询订单状态失败:', error);
    }
  };
  
  setTimeout(checkStatus, 3000);
};

const closeModal = () => {
  showPaymentModal.value = false;
  selectedPlan.value = null;
  qrCodeUrl.value = '';
};
</script>

<style scoped>
.pricing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 1.5rem;
  font-weight: bold;
}

.logo-icon {
  font-size: 1.8rem;
}

.nav {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-btn:hover,
.nav-btn.primary {
  background: #e94560;
  border-color: #e94560;
}

.login-btn {
  padding: 0.5rem 1.5rem;
  background: #e94560;
  border: none;
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn:hover {
  background: #ff6b6b;
}

/* 主要内容 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

/* Hero区域 */
.hero-section {
  text-align: center;
  margin-bottom: 4rem;
}

.title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #fff 0%, #e94560 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2rem;
}

.billing-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 1.1rem;
}

.billing-toggle span {
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.3s;
}

.billing-toggle span.active {
  color: #fff;
  font-weight: bold;
}

.switch {
  position: relative;
  width: 60px;
  height: 32px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.2);
  transition: 0.4s;
  border-radius: 32px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 24px;
  width: 24px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #e94560;
}

input:checked + .slider:before {
  transform: translateX(28px);
}

.save-badge {
  background: #e94560;
  color: #fff;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
}

/* 价格卡片 */
.pricing-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.pricing-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  transition: all 0.3s;
}

.pricing-card:hover {
  transform: translateY(-8px);
  border-color: rgba(233, 69, 96, 0.5);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.pricing-card.free {
  border-color: rgba(255, 255, 255, 0.2);
}

.pricing-card.special {
  border-color: #ff9f43;
}

.pricing-card.recommended {
  border-color: #10ac84;
  transform: scale(1.05);
}

.pricing-card.popular {
  border-color: #e94560;
  transform: scale(1.05);
}

.pricing-card.recommended:hover,
.pricing-card.popular:hover {
  transform: scale(1.05) translateY(-8px);
}

.badge {
  position: absolute;
  top: -12px;
  right: 20px;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.badge.hot {
  background: #ff9f43;
  color: #fff;
}

.badge.recommended-badge {
  background: #10ac84;
  color: #fff;
}

.badge.popular-badge {
  background: #e94560;
  color: #fff;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.plan-name {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.price {
  margin-bottom: 0.5rem;
}

.currency {
  font-size: 1.5rem;
  vertical-align: top;
}

.amount {
  font-size: 3.5rem;
  font-weight: bold;
}

.period {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.original-price {
  text-decoration: line-through;
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.current-price {
  display: inline-flex;
  align-items: baseline;
}

.plan-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
}

.card-body {
  margin-bottom: 2rem;
}

.features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item.disabled {
  color: rgba(255, 255, 255, 0.4);
}

.feature-item.highlight {
  color: #e94560;
  font-weight: bold;
}

.check {
  color: #10ac84;
  font-weight: bold;
}

.cross {
  color: #ff6b6b;
}

.card-footer {
  text-align: center;
}

.btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
}

.btn-free {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-free:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.btn-primary:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
}

.btn-special {
  background: linear-gradient(135deg, #ff9f43 0%, #ee5a24 100%);
  color: #fff;
}

.btn-special:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 20px rgba(255, 159, 67, 0.4);
}

.btn-recommended {
  background: linear-gradient(135deg, #10ac84 0%, #1dd1a1 100%);
  color: #fff;
}

.btn-recommended:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 20px rgba(16, 172, 132, 0.4);
}

.btn-popular {
  background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
  color: #fff;
}

.btn-popular:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 20px rgba(233, 69, 96, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  width: auto;
  padding: 0.75rem 1.5rem;
}

/* FAQ区域 */
.faq-section {
  max-width: 800px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.faq-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
}

.faq-question {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: #e94560;
}

.faq-answer {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.order-info {
  margin-bottom: 1.5rem;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.order-item .price {
  color: #e94560;
  font-weight: bold;
  font-size: 1.2rem;
}

.payment-method {
  margin-bottom: 1.5rem;
}

.payment-method h4 {
  margin-bottom: 1rem;
}

.method-options {
  display: flex;
  gap: 1rem;
}

.method-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.method-option.active,
.method-option:hover {
  border-color: #e94560;
  background: rgba(233, 69, 96, 0.1);
}

.method-option input {
  display: none;
}

.method-icon {
  font-size: 1.5rem;
}

.qr-code-section {
  text-align: center;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.qr-code {
  width: 200px;
  height: 200px;
  margin: 1rem 0;
  border-radius: 8px;
}

.qr-tip {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-footer .btn {
  flex: 1;
}

/* 页脚 */
.footer {
  text-align: center;
  padding: 2rem;
  background: rgba(0, 0, 0, 0.3);
  color: rgba(255, 255, 255, 0.5);
}

.footer p {
  margin: 0.5rem 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .header {
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
  }

  .nav {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .title {
    font-size: 2rem;
  }

  .pricing-cards {
    grid-template-columns: 1fr;
  }

  .pricing-card.recommended,
  .pricing-card.popular {
    transform: none;
  }

  .pricing-card.recommended:hover,
  .pricing-card.popular:hover {
    transform: translateY(-8px);
  }
}
</style>