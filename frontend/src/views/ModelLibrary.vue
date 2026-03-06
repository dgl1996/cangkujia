<template>
  <div class="model-library">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="logo" @click="goHome">
          <img src="/LOGO.png" alt="仓酷家" class="logo-img" />
        </div>
        <div class="nav-title">3D物流对象库</div>
        <div class="nav-actions">
          <button class="btn-secondary" @click="goUsage">返回主页</button>
        </div>
      </div>
    </nav>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧分类栏 -->
      <aside class="sidebar">
        <div class="category-list">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-item"
            :class="{ active: currentCategory === category.id }"
            @click="selectCategory(category.id)"
          >
            <span class="category-icon">{{ category.icon }}</span>
            <span class="category-name">{{ category.name }}</span>
            <span class="category-count">{{ getModelCount(category.id) }}</span>
          </div>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content">
        <!-- 搜索和筛选 -->
        <div class="toolbar">
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索模型..."
              class="search-input"
            />
            <span class="search-icon">🔍</span>
          </div>
          <div class="toolbar-actions">
            <button class="btn-custom-shelf" @click="openCustomShelfModal">
              <span class="btn-icon">➕</span>
              <span>自定义货架</span>
            </button>
          </div>
          <div class="filter-tags">
            <span
              v-for="tag in currentTags"
              :key="tag"
              class="filter-tag"
              :class="{ active: selectedTags.includes(tag) }"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- 模型网格 -->
        <div class="models-grid">
          <div
            v-for="model in filteredModels"
            :key="model.id"
            class="model-card"
            @click="selectModel(model)"
          >
            <div class="model-preview" @click.stop="previewModel(model)">
              <div class="preview-placeholder">
                <!-- 如果有缩略图则显示，否则显示图标 -->
                <img 
                  v-if="model.thumbnail" 
                  :src="model.thumbnail" 
                  :alt="model.name"
                  class="model-thumbnail"
                />
                <span v-else class="preview-icon">{{ getCategoryIcon(model.category) }}</span>
                <div class="preview-overlay">
                  <span class="preview-text">点击预览</span>
                </div>
              </div>
            </div>
            <div class="model-info">
              <h3 class="model-name">{{ model.name }}</h3>
              <p class="model-desc">{{ model.description }}</p>
              <div class="model-tags">
                <span v-for="tag in model.tags.slice(0, 2)" :key="tag" class="tag">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 模型预览弹窗 -->
    <div v-if="showPreview" class="preview-modal" @click="closePreview">
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h3>{{ selectedModel?.name }}</h3>
          <button class="btn-close" @click="closePreview">×</button>
        </div>
        <div class="preview-body">
          <div class="preview-3d">
            <!-- 3D预览区域 -->
            <ModelPreview 
              :modelUrl="selectedModel?.modelUrl" 
              :autoRotate="true"
              :customColors="selectedModel?.customColors"
            />
            <div class="preview-hint">
              <span class="hint-icon">🖱️</span>
              <span class="hint-text">滚轮放大 / 左键旋转查看</span>
            </div>
          </div>
          <div class="preview-params">
            <h4>参数配置</h4>
            <div
              v-for="(param, key) in selectedModel?.parameters"
              :key="key"
              class="param-item"
            >
              <div class="param-header">
                <label>{{ getParamLabel(key) }}:</label>
                <span class="param-value">{{ param.default }}{{ param.unit || '' }}</span>
              </div>
              <input
                v-if="param.type === 'number'"
                type="range"
                :min="param.min"
                :max="param.max"
                :value="param.default"
                class="param-slider"
                @input="updateParam(key, $event.target.value)"
              />
              <select v-else-if="param.type === 'select'" class="param-select">
                <option v-for="opt in param.options" :key="opt" :value="opt">
                  {{ opt }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="preview-footer">
          <button class="btn-secondary" @click="closePreview">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 自定义货架弹窗 -->
    <div v-if="showCustomShelfModal" class="preview-modal" @click="closeCustomShelfModal">
      <div class="preview-content custom-shelf-modal" @click.stop>
        <div class="preview-header">
          <h3>自定义横梁式货架</h3>
          <button class="btn-close" @click="closeCustomShelfModal">×</button>
        </div>
        <div class="preview-body">
          <div class="form-section">
            <h4>基础尺寸</h4>
            <div class="form-row">
              <div class="form-group">
                <label>长度 (mm)</label>
                <input
                  v-model.number="customShelfParams.length"
                  type="number"
                  min="800"
                  max="5000"
                  step="100"
                  class="form-input"
                />
                <input
                  v-model.number="customShelfParams.length"
                  type="range"
                  min="800"
                  max="5000"
                  step="100"
                  class="form-slider"
                />
              </div>
              <div class="form-group">
                <label>深度 (mm)</label>
                <input
                  v-model.number="customShelfParams.width"
                  type="number"
                  min="300"
                  max="1500"
                  step="50"
                  class="form-input"
                />
                <input
                  v-model.number="customShelfParams.width"
                  type="range"
                  min="300"
                  max="1500"
                  step="50"
                  class="form-slider"
                />
              </div>
              <div class="form-group">
                <label>高度 (mm)</label>
                <input
                  v-model.number="customShelfParams.height"
                  type="number"
                  min="1500"
                  max="12000"
                  step="100"
                  class="form-input"
                />
                <input
                  v-model.number="customShelfParams.height"
                  type="range"
                  min="1500"
                  max="12000"
                  step="100"
                  class="form-slider"
                />
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4>结构参数</h4>
            <div class="form-row">
              <div class="form-group">
                <label>层数</label>
                <input
                  v-model.number="customShelfParams.levels"
                  type="number"
                  min="2"
                  max="10"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>立柱截面宽 (mm)</label>
                <input
                  v-model.number="customShelfParams.uprightWidth"
                  type="number"
                  min="30"
                  max="120"
                  step="5"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>立柱截面深 (mm)</label>
                <input
                  v-model.number="customShelfParams.uprightDepth"
                  type="number"
                  min="20"
                  max="100"
                  step="5"
                  class="form-input"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>横梁高度 (mm)</label>
                <input
                  v-model.number="customShelfParams.beamHeight"
                  type="number"
                  min="30"
                  max="150"
                  step="5"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>横梁宽度 (mm)</label>
                <input
                  v-model.number="customShelfParams.beamWidth"
                  type="number"
                  min="20"
                  max="80"
                  step="5"
                  class="form-input"
                />
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4>货架名称</h4>
            <div class="form-group">
              <input
                v-model="customShelfParams.name"
                type="text"
                placeholder="输入自定义货架名称"
                class="form-input name-input"
              />
            </div>
          </div>

          <!-- 实时预览 -->
          <div class="preview-section">
            <h4>实时预览</h4>
            <div class="preview-info">
              <span>类型: {{ getShelfTypeLabel }}</span>
              <span>视觉特征: {{ getShelfFeatureLabel }}</span>
            </div>
          </div>
        </div>
        <div class="preview-footer">
          <button class="btn-secondary" @click="closeCustomShelfModal">取消</button>
          <button class="btn-primary" @click="saveCustomShelf" :disabled="!customShelfParams.name">
            保存到对象库
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import ModelPreview from '../components/3d/ModelPreview.vue';

const router = useRouter();

// 分类数据
const categories = [
  { id: 'all', name: '全部模型', icon: '📦' },
  { id: 'storage', name: '货架系统', icon: '🏗️' },
  { id: 'handling', name: '搬运设备', icon: '🚛' },
  { id: 'containers', name: '载具容器', icon: '📦' },
  { id: 'conveying', name: '输送设备', icon: '🔄' },
  { id: 'sorting', name: '分拨设备', icon: '📍' },
  { id: 'picking', name: '拣选设备', icon: '🎯' },
  { id: 'others', name: '其他设备', icon: '⚙️' },
];

// 模型数据（初始数据，后续从后端或JSON文件加载）
const models = ref([
  // 货架系统
  {
    id: 'shelf-beam-heavy',
    name: '重型横梁式货架',
    category: 'storage',
    description: '适用于重型货物存储，单层承重2000kg',
    tags: ['重型', '横梁式', '可调节'],
    parameters: {
      length: { type: 'number', min: 2000, max: 4000, default: 2700, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 12000, default: 4500, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 8, default: 4 },
    },
    modelUrl: '/assets/models/shelf-beam-heavy.glb',
  },
  {
    id: 'shelf-beam-medium',
    name: '横梁式货架-中型4层（L2000*D800*H3500）',
    category: 'storage',
    description: '适用于中型货物存储，单层承重500kg',
    tags: ['中型', '横梁式', '标准'],
    parameters: {
      length: { type: 'number', min: 1500, max: 3000, default: 2000, unit: 'mm' },
      width: { type: 'number', min: 600, max: 1000, default: 800, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 8000, default: 3500, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 6, default: 4 },
    },
    modelUrl: '/assets/models/shelf-beam-medium.glb',
  },
  {
    id: 'shelf-drive-in',
    name: '驶入式货架-重型（L3600*D1500*H6000）',
    category: 'storage',
    description: '高密度存储，适合大批量同类型货物',
    tags: ['高密度', '驶入式', '冷链'],
    parameters: {
      length: { type: 'number', min: 2000, max: 6000, default: 3600, unit: 'mm' },
      width: { type: 'number', min: 1200, max: 1800, default: 1500, unit: 'mm' },
      height: { type: 'number', min: 3000, max: 12000, default: 6000, unit: 'mm' },
      depth: { type: 'number', min: 2, max: 10, default: 5, unit: '托盘位' },
    },
    modelUrl: '/assets/models/shelf-drive-in.glb',
  },
  {
    id: 'shelf-flow-4level-1m8',
    name: '流利式货架-4层拣选（L900*D450*H1800）',
    category: 'storage',
    description: '先进先出(FIFO)拣选作业，配送中心产线旁供料，带5度倾斜流利条',
    tags: ['流利式', '4层', 'FIFO', '拣选', '薄荷绿'],
    parameters: {
      length: { type: 'number', min: 600, max: 1200, default: 900, unit: 'mm' },
      width: { type: 'number', min: 300, max: 600, default: 450, unit: 'mm' },
      height: { type: 'number', min: 1200, max: 2500, default: 1800, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 6, default: 4 },
    },
    modelUrl: '/assets/models/shelf-flow-4level.glb',
  },
  {
    id: 'shelf-light-v2',
    name: '横梁式货架-轻型4层（L1200*D400*H2000）',
    category: 'storage',
    description: '基于参考图片改进的轻型货架，蓝色立柱配橙色横梁',
    tags: ['轻型', '横梁式', '蓝色立柱', '橙色横梁'],
    parameters: {
      length: { type: 'number', min: 800, max: 2000, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 300, max: 600, default: 400, unit: 'mm' },
      height: { type: 'number', min: 1500, max: 3000, default: 2000, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 6, default: 4 },
    },
    modelUrl: '/assets/models/shelf-light-v2.glb',
  },
  // 行业标准重型货架
  {
    id: 'shelf-beam-heavy-3level-5m',
    name: '横梁式货架-重型3层（L2300*D1000*H4500）',
    category: 'storage',
    description: '适配净空5.5m仓库，单层高承重2吨，适合重货存储',
    tags: ['重型', '3层', '中高位', '2吨承重'],
    parameters: {
      length: { type: 'number', min: 2000, max: 3000, default: 2300, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 3500, max: 5500, default: 4500, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 5, default: 3 },
    },
    modelUrl: '/assets/models/shelf-beam-heavy-3level.glb',
  },
  {
    id: 'shelf-beam-heavy-4level-6m',
    name: '横梁式货架-重型4层（L2300*D1000*H6500）',
    category: 'storage',
    description: '适配净空7m仓库，电商仓最常用规格，平衡型设计',
    tags: ['重型', '4层', '标准', '电商仓常用'],
    parameters: {
      length: { type: 'number', min: 2000, max: 3000, default: 2300, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 5000, max: 7500, default: 6500, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 6, default: 4 },
    },
    modelUrl: '/assets/models/shelf-beam-heavy-4level.glb',
  },
  {
    id: 'shelf-beam-heavy-5level-8m',
    name: '横梁式货架-重型5层（L2700*D1000*H8200）',
    category: 'storage',
    description: '适配净空9m仓库，高位立体库专用，需要前移式叉车',
    tags: ['重型', '5层', '高位', '立体库'],
    parameters: {
      length: { type: 'number', min: 2300, max: 3500, default: 2700, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 7000, max: 10000, default: 8200, unit: 'mm' },
      levels: { type: 'number', min: 3, max: 8, default: 5 },
    },
    modelUrl: '/assets/models/shelf-beam-heavy-5level.glb',
  },
  // 中型货架（人工拣选）
  {
    id: 'shelf-beam-medium-4level-2m',
    name: '横梁式货架-中型4层（L2000*D600*H2500）',
    category: 'storage',
    description: '人工存取极限（配合2步登高梯），适配层高2.5m仓库',
    tags: ['中型', '4层', '人工拣选', '登高梯'],
    parameters: {
      length: { type: 'number', min: 1500, max: 2500, default: 2000, unit: 'mm' },
      width: { type: 'number', min: 400, max: 800, default: 600, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 3000, default: 2500, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 5, default: 4 },
    },
    modelUrl: '/assets/models/shelf-beam-medium-4level-2m.glb',
  },
  {
    id: 'shelf-beam-medium-5level-2m',
    name: '横梁式货架-中型5层（L1500*D600*H2500）',
    category: 'storage',
    description: '高密度人工仓，层高2.5m极限，适合小件拣选',
    tags: ['中型', '5层', '高密度', '人工仓'],
    parameters: {
      length: { type: 'number', min: 1200, max: 2000, default: 1500, unit: 'mm' },
      width: { type: 'number', min: 400, max: 800, default: 600, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 3000, default: 2500, unit: 'mm' },
      levels: { type: 'number', min: 3, max: 6, default: 5 },
    },
    modelUrl: '/assets/models/shelf-beam-medium-5level-2m.glb',
  },
  // 轻型货架
  {
    id: 'shelf-beam-light-4level-2m',
    name: '横梁式货架-轻型4层（L1200*D400*H2000）',
    category: 'storage',
    description: '便利店后仓、办公室文件、轻型商品存储',
    tags: ['轻型', '4层', '标准', '人工存取'],
    parameters: {
      length: { type: 'number', min: 800, max: 1500, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
      height: { type: 'number', min: 1500, max: 2500, default: 2000, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 5, default: 4 },
    },
    modelUrl: '/assets/models/shelf-beam-light-4level.glb',
  },
  {
    id: 'shelf-beam-light-5level-2m',
    name: '横梁式货架-轻型5层（L1200*D500*H2000）',
    category: 'storage',
    description: '电商小件仓、配件仓、图书档案、多SKU轻货',
    tags: ['轻型', '5层', '宽型', '高密度'],
    parameters: {
      length: { type: 'number', min: 800, max: 1500, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 400, max: 600, default: 500, unit: 'mm' },
      height: { type: 'number', min: 1500, max: 2500, default: 2000, unit: 'mm' },
      levels: { type: 'number', min: 3, max: 6, default: 5 },
    },
    modelUrl: '/assets/models/shelf-beam-light-5level.glb',
  },
  // 载具容器
  {
    id: 'pallet-wooden-1200',
    name: '木质托盘 1200×1000',
    category: 'containers',
    description: '标准欧标木质托盘，四面进叉',
    tags: ['木质', '标准', '欧标'],
    parameters: {
      length: { type: 'number', min: 800, max: 1400, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 120, max: 200, default: 150, unit: 'mm' },
    },
    modelUrl: '/assets/models/pallet-wooden-1200.glb',
  },
  {
    id: 'pallet-plastic-1200',
    name: '塑料托盘 1200×1000',
    category: 'containers',
    description: 'HDPE塑料托盘，防潮防腐蚀',
    tags: ['塑料', '防潮', '耐用'],
    parameters: {
      length: { type: 'number', min: 800, max: 1400, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 120, max: 200, default: 150, unit: 'mm' },
    },
    modelUrl: '/assets/models/pallet-plastic-1200.glb',
  },
  {
    id: 'pallet-wood-1200x1000',
    name: '木质托盘-标准双向（L1200*W1000*H144）',
    category: 'containers',
    description: '标准欧标木质托盘，双向进叉，5块面板+3根纵梁结构，适配重型货架',
    tags: ['木质', '标准', '双向进叉', 'GB/T 2934-2007'],
    parameters: {
      length: { type: 'number', min: 1000, max: 1400, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 120, max: 160, default: 144, unit: 'mm' },
    },
    modelUrl: '/assets/models/pallet-wood-1200x1000.glb',
  },
  {
    id: 'pallet-plastic-1200x1000',
    name: '塑料托盘-网格双面（L1200*W1000*H150）',
    category: 'containers',
    description: 'HDPE塑料托盘，双面网格结构，四向进叉，防潮防腐蚀，适配立体库',
    tags: ['塑料', 'HDPE', '四向进叉', '双面', '网格'],
    parameters: {
      length: { type: 'number', min: 1000, max: 1400, default: 1200, unit: 'mm' },
      width: { type: 'number', min: 800, max: 1200, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 130, max: 170, default: 150, unit: 'mm' },
    },
    modelUrl: '/assets/models/pallet-plastic-1200x1000.glb',
  },
  {
    id: 'container-foldable',
    name: '可折叠周转箱',
    category: 'containers',
    description: '可折叠设计，节省回程运输空间',
    tags: ['可折叠', '周转箱', '省空间'],
    parameters: {
      length: { type: 'number', min: 300, max: 800, default: 600, unit: 'mm' },
      width: { type: 'number', min: 200, max: 600, default: 400, unit: 'mm' },
      height: { type: 'number', min: 200, max: 500, default: 300, unit: 'mm' },
    },
    modelUrl: '/assets/models/container-foldable.glb',
  },
  // EU标准周转箱
  {
    id: 'container-tote-600x400x300',
    name: '可堆叠周转箱-600×400×300',
    category: 'containers',
    description: 'EU标准周转箱，适配中型货架，可堆叠4层，蓝色',
    tags: ['周转箱', 'EU标准', '可堆叠', '蓝色', '中型货架'],
    parameters: {
      length: { type: 'number', min: 500, max: 700, default: 600, unit: 'mm' },
      width: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
      height: { type: 'number', min: 200, max: 400, default: 300, unit: 'mm' },
    },
    modelUrl: '/assets/models/container-tote-600x400.glb',
  },
  {
    id: 'container-tote-600x400x220',
    name: '可堆叠周转箱-600×400×220',
    category: 'containers',
    description: 'EU标准矮型周转箱，适配流利式货架，可堆叠5层，蓝色',
    tags: ['周转箱', 'EU标准', '矮型', '流利式', '蓝色'],
    parameters: {
      length: { type: 'number', min: 500, max: 700, default: 600, unit: 'mm' },
      width: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
      height: { type: 'number', min: 150, max: 300, default: 220, unit: 'mm' },
    },
    modelUrl: '/assets/models/container-tote-600x400-low.glb',
  },
  {
    id: 'container-tote-400x300x150',
    name: '可堆叠周转箱-400×300×150',
    category: 'containers',
    description: '小型零件周转箱，适配轻型货架，可堆叠6层，橙色',
    tags: ['周转箱', '零件盒', '小型', '橙色', '轻型货架'],
    parameters: {
      length: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
      width: { type: 'number', min: 200, max: 400, default: 300, unit: 'mm' },
      height: { type: 'number', min: 100, max: 200, default: 150, unit: 'mm' },
    },
    modelUrl: '/assets/models/container-tote-400x300.glb',
  },
]);

// 状态
const currentCategory = ref('all');
const searchQuery = ref('');
const selectedTags = ref([]);
const showPreview = ref(false);
const selectedModel = ref(null);
const showCustomShelfModal = ref(false);

// 自定义货架参数
const customShelfParams = ref({
  name: '',
  length: 2000,
  width: 600,
  height: 2500,
  levels: 4,
  uprightWidth: 50,
  uprightDepth: 30,
  beamHeight: 80,
  beamWidth: 40,
});

// 从localStorage加载自定义货架
const loadCustomShelves = () => {
  const saved = localStorage.getItem('customShelves');
  if (saved) {
    const customShelves = JSON.parse(saved);
    models.value = [...models.value, ...customShelves];
  }
};

// 计算货架类型标签
const getShelfTypeLabel = computed(() => {
  const { uprightWidth, beamHeight } = customShelfParams.value;
  if (uprightWidth >= 80 || beamHeight >= 100) return '重型货架';
  if (uprightWidth >= 50 || beamHeight >= 60) return '中型货架';
  return '轻型货架';
});

// 计算视觉特征标签
const getShelfFeatureLabel = computed(() => {
  const { uprightWidth, uprightDepth, beamHeight, beamWidth } = customShelfParams.value;
  const uprightArea = uprightWidth * uprightDepth;
  const beamArea = beamHeight * beamWidth;
  
  if (uprightArea > 6000 || beamArea > 4000) return '粗壮，高承载';
  if (uprightArea > 1500 || beamArea > 2000) return '标准，平衡型';
  return '纤细，轻型';
});

// 打开自定义货架弹窗
const openCustomShelfModal = () => {
  console.log('openCustomShelfModal called');
  showCustomShelfModal.value = true;
  // 重置为默认值
  customShelfParams.value = {
    name: '',
    length: 2000,
    width: 600,
    height: 2500,
    levels: 4,
    uprightWidth: 50,
    uprightDepth: 30,
    beamHeight: 80,
    beamWidth: 40,
  };
};

// 关闭自定义货架弹窗
const closeCustomShelfModal = () => {
  showCustomShelfModal.value = false;
};

// 保存自定义货架
const saveCustomShelf = () => {
  const params = customShelfParams.value;
  
  // 根据货架类型确定颜色
  const shelfType = getShelfTypeLabel.value;
  let uprightColor, beamColor, deckColor, colorDesc;
  
  if (shelfType === '重型货架') {
    // 重型货架：立柱-红色，横梁-橙红，层板-白色
    uprightColor = '红色';
    beamColor = '橙红';
    deckColor = '白色';
    colorDesc = '立柱红色/横梁橙红/层板白色';
  } else {
    // 中型/轻型货架：立柱-淡蓝色，横梁-橙红，层板-白色
    uprightColor = '淡蓝色';
    beamColor = '橙红';
    deckColor = '白色';
    colorDesc = '立柱淡蓝/横梁橙红/层板白色';
  }
  
  const newShelf = {
    id: `custom-shelf-${Date.now()}`,
    name: params.name || `自定义货架-${params.length}×${params.width}×${params.height}`,
    category: 'storage',
    description: `自定义${shelfType}：${colorDesc}，立柱${params.uprightWidth}×${params.uprightDepth}mm，横梁${params.beamHeight}×${params.beamWidth}mm`,
    tags: ['自定义', shelfType],
    parameters: {
      length: { type: 'number', min: 800, max: 5000, default: params.length, unit: 'mm' },
      width: { type: 'number', min: 300, max: 1500, default: params.width, unit: 'mm' },
      height: { type: 'number', min: 1500, max: 12000, default: params.height, unit: 'mm' },
      levels: { type: 'number', min: 2, max: 10, default: params.levels },
      uprightWidth: { type: 'number', min: 30, max: 120, default: params.uprightWidth, unit: 'mm' },
      uprightDepth: { type: 'number', min: 20, max: 100, default: params.uprightDepth, unit: 'mm' },
      beamHeight: { type: 'number', min: 30, max: 150, default: params.beamHeight, unit: 'mm' },
      beamWidth: { type: 'number', min: 20, max: 80, default: params.beamWidth, unit: 'mm' },
    },
    modelUrl: '/assets/models/shelf-beam-medium.glb', // 使用中型货架作为基础模型
    isCustom: true,
    customParams: { ...params },
    customColors: {
      upright: uprightColor,
      beam: beamColor,
      deck: deckColor,
      type: shelfType
    }
  };
  
  // 添加到模型列表
  models.value.push(newShelf);
  
  // 保存到localStorage
  const customShelves = models.value.filter(m => m.isCustom);
  localStorage.setItem('customShelves', JSON.stringify(customShelves));
  
  // 关闭弹窗
  closeCustomShelfModal();
  
  // 显示成功提示（可以添加toast组件）
  alert('自定义货架已保存到对象库！');
};

// 初始化时加载自定义货架
loadCustomShelves();

// 计算属性
const currentTags = computed(() => {
  const tags = new Set();
  models.value.forEach(model => {
    if (currentCategory.value === 'all' || model.category === currentCategory.value) {
      model.tags.forEach(tag => tags.add(tag));
    }
  });
  return Array.from(tags);
});

const filteredModels = computed(() => {
  return models.value.filter(model => {
    // 分类筛选
    if (currentCategory.value !== 'all' && model.category !== currentCategory.value) {
      return false;
    }
    // 搜索筛选
    if (searchQuery.value && !model.name.includes(searchQuery.value)) {
      return false;
    }
    // 标签筛选
    if (selectedTags.value.length > 0 && !selectedTags.value.some(tag => model.tags.includes(tag))) {
      return false;
    }
    return true;
  });
});

// 方法
const selectCategory = (id) => {
  currentCategory.value = id;
  selectedTags.value = [];
};

const getModelCount = (categoryId) => {
  if (categoryId === 'all') return models.value.length;
  return models.value.filter(m => m.category === categoryId).length;
};

const getCategoryIcon = (categoryId) => {
  const category = categories.find(c => c.id === categoryId);
  return category?.icon || '📦';
};

const getParamLabel = (key) => {
  const labels = {
    length: '长度',
    width: '宽度',
    height: '高度',
    levels: '层数',
    depth: '深度'
  };
  return labels[key] || key;
};

const updateParam = (key, value) => {
  if (selectedModel.value && selectedModel.value.parameters[key]) {
    selectedModel.value.parameters[key].default = parseInt(value);
  }
};

const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag);
  if (index > -1) {
    selectedTags.value.splice(index, 1);
  } else {
    selectedTags.value.push(tag);
  }
};

const selectModel = (model) => {
  selectedModel.value = model;
};

const previewModel = (model) => {
  selectedModel.value = model;
  showPreview.value = true;
};

const closePreview = () => {
  showPreview.value = false;
  selectedModel.value = null;
};

const addToScene = (model) => {
  // 将模型添加到编辑器场景
  // 通过路由参数或状态管理传递模型信息
  router.push({
    path: '/editor',
    query: { modelId: model.id }
  });
};

const goHome = () => {
  router.push('/');
};

const goEditor = () => {
  router.push('/editor');
};

const goUsage = () => {
  router.push('/usage');
};
</script>

<style scoped>
.model-library {
  min-height: 100vh;
  background: #f5f7fa;
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
  max-width: 1400px;
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
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  min-height: calc(100vh - 60px);
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e8ecff;
  padding: 1.5rem 0;
}

.category-list {
  display: flex;
  flex-direction: column;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 0.875rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.category-item:hover {
  background: #f8f9ff;
}

.category-item.active {
  background: #e8ecff;
  border-left-color: #4361ee;
}

.category-icon {
  font-size: 1.25rem;
  margin-right: 0.75rem;
}

.category-name {
  flex: 1;
  font-size: 0.95rem;
  color: #4a4a68;
}

.category-item.active .category-name {
  color: #4361ee;
  font-weight: 500;
}

.category-count {
  font-size: 0.8rem;
  color: #6b6b8a;
  background: #f0f0f5;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
}

/* 内容区 */
.content {
  flex: 1;
  padding: 1.5rem;
}

/* 工具栏 */
.toolbar {
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e0e0e8;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #4361ee;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b6b8a;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-tag {
  padding: 0.375rem 0.875rem;
  background: white;
  border: 1px solid #e0e0e8;
  border-radius: 16px;
  font-size: 0.85rem;
  color: #4a4a68;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tag:hover {
  border-color: #4361ee;
  color: #4361ee;
}

.filter-tag.active {
  background: #4361ee;
  border-color: #4361ee;
}

/* 自定义货架按钮 */
.toolbar-actions {
  margin-bottom: 1rem;
}

.btn-custom-shelf {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(67, 97, 238, 0.3);
}

.btn-custom-shelf:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.4);
}

.btn-icon {
  font-size: 1rem;
}

/* 自定义货架弹窗 */
.custom-shelf-modal {
  max-width: 700px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e8;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h4 {
  font-size: 1rem;
  color: #2d2d44;
  margin-bottom: 1rem;
  font-weight: 600;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.85rem;
  color: #4a4a68;
  font-weight: 500;
}

.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid #e0e0e8;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #4361ee;
}

.form-slider {
  width: 100%;
  margin-top: 0.25rem;
}

.name-input {
  font-size: 1rem;
  padding: 0.75rem 1rem;
}

.preview-section {
  background: #f8f9ff;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.preview-section h4 {
  margin-bottom: 0.75rem;
}

.preview-info {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.preview-info span {
  font-size: 0.9rem;
  color: #4a4a68;
  background: white;
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  border: 1px solid #e0e0e8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  color: white;
}

/* 模型网格 */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.model-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.model-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.model-preview {
  aspect-ratio: 4/3;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.preview-placeholder {
  text-align: center;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-icon {
  font-size: 3rem;
}

.model-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 1rem;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.model-preview:hover .preview-overlay {
  opacity: 1;
}

.preview-text {
  color: white;
  font-size: 1rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  background: rgba(67, 97, 238, 0.9);
  border-radius: 20px;
}

.model-info {
  padding: 1rem;
}

.model-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.375rem;
}

.model-desc {
  font-size: 0.85rem;
  color: #6b6b8a;
  line-height: 1.5;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.model-tags {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.tag {
  padding: 0.25rem 0.5rem;
  background: #f0f0f5;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #6b6b8a;
}

.model-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0 1rem 1rem;
}

.btn-preview,
.btn-add {
  flex: 1;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-preview {
  border: 1px solid #e0e0e8;
  background: white;
  color: #4a4a68;
}

.btn-preview:hover {
  border-color: #4361ee;
  color: #4361ee;
}

.btn-add {
  border: none;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
}

.btn-add:hover {
  opacity: 0.9;
}

/* 预览弹窗 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.preview-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e8ecff;
}

.preview-header h3 {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f0f0f5;
  border-radius: 50%;
  font-size: 1.25rem;
  color: #6b6b8a;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #e0e0e8;
  color: #1a1a2e;
}

.preview-body {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow: auto;
}

.preview-3d {
  aspect-ratio: 4/3;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-hint {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
  pointer-events: none;
  z-index: 10;
}

.hint-icon {
  font-size: 0.9rem;
}

.hint-text {
  white-space: nowrap;
}

.preview-canvas {
  text-align: center;
  color: #6b6b8a;
}

.preview-params {
  padding: 1rem;
  background: #f8f9ff;
  border-radius: 12px;
}

.preview-params h4 {
  font-size: 1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.param-item {
  margin-bottom: 1rem;
}

.param-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.param-header label {
  font-size: 0.85rem;
  color: #4a4a68;
}

.param-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4361ee;
}

.param-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e8;
  outline: none;
  -webkit-appearance: none;
}

.param-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4361ee;
  cursor: pointer;
}

.param-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e0e0e8;
  border-radius: 6px;
  font-size: 0.9rem;
  background: white;
}

.preview-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e8ecff;
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }
  
  .preview-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e8ecff;
    padding: 1rem 0;
  }
  
  .category-list {
    flex-direction: row;
    overflow-x: auto;
    padding: 0 1rem;
  }
  
  .category-item {
    white-space: nowrap;
    border-left: none;
    border-bottom: 3px solid transparent;
  }
  
  .category-item.active {
    border-left-color: transparent;
    border-bottom-color: #4361ee;
  }
  
  .models-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style>
