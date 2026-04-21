<template>
  <div class="model-library">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="logo" @click="goHome">
          <img src="/仓酷家Alogo.png" alt="仓酷家" class="logo-img" />
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
            <component :is="category.icon" class="category-icon" :size="20" />
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
            <Search class="search-icon" :size="18" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索模型..."
              class="search-input"
            />
          </div>
          <div class="toolbar-actions">
            <button class="btn-custom-shelf" @click="openCustomShelfModal">
              <Plus class="btn-icon" :size="18" />
              <span>自定义货架</span>
            </button>
            <button class="btn-custom-wall" @click="openCustomWallModal">
              <Plus class="btn-icon" :size="18" />
              <span>自定义墙体</span>
            </button>
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
                <component v-else :is="getCategoryIcon(model.category)" class="preview-icon" :size="48" />
                <div class="preview-overlay">
                  <span class="preview-text">点击预览</span>
                </div>
              </div>
            </div>
            <div class="model-info">
              <h3 class="model-name">
                <span class="model-id">[{{ model.shortId }}]</span>
                {{ model.name }}
              </h3>
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
          <button class="btn-close" @click="closePreview">
            <X :size="20" />
          </button>
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
              <Eye class="hint-icon" :size="16" />
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

    <!-- 自定义货架弹窗 - 两层级联选择器 -->
    <div v-if="showCustomShelfModal" class="preview-modal" @click="closeCustomShelfModal">
      <div class="preview-content custom-shelf-modal" @click.stop>
        <div class="preview-header">
          <h3>自定义货架</h3>
          <button class="btn-close" @click="closeCustomShelfModal">
            <X :size="20" />
          </button>
        </div>
        <div class="preview-body custom-shelf-body">
          <!-- 第一行：两层下拉选择 -->
          <div class="selectors-row">
            <!-- 第一层选择：分类 -->
            <div class="form-section selector-half">
              <h4>选择货架类型</h4>
              <div class="form-group">
                <select v-model="selectedCategory" class="form-input category-select" @change="onCategoryChange">
                  <option value="">请选择货架类型</option>
                  <option v-for="cat in shelfCategories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
            </div>

            <!-- 第二层选择：具体型号 -->
            <div class="form-section selector-half" v-if="selectedCategory">
              <h4>选择货架规格</h4>
              <div class="form-group">
                <select v-model="selectedModel" class="form-input model-select" @change="onModelChange">
                  <option value="">请选择货架规格</option>
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id" 
                    :value="model"
                    :disabled="model.prebuilt"
                  >
                    {{ model.name }} {{ model.prebuilt ? '(已预置)' : '' }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- 3D预览和规格信息并排 -->
          <div class="preview-and-specs" v-if="selectedModel">
            <!-- 3D预览（左侧，更大） -->
            <div class="preview-3d-section-large">
              <h4>3D预览</h4>
              <div class="preview-3d-container-large">
                <ModelPreview 
                  :modelUrl="selectedModel.file" 
                  :autoRotate="true"
                />
              </div>
            </div>

            <!-- 规格信息显示（右侧） -->
            <div class="specs-section-compact">
              <h4>货架规格</h4>
              <div class="specs-list">
                <div class="spec-row">
                  <span class="spec-label">承重:</span>
                  <span class="spec-value">{{ selectedModel.specs.承重 }}</span>
                </div>
                <div class="spec-row">
                  <span class="spec-label">层高:</span>
                  <span class="spec-value">{{ selectedModel.specs.层高 }}</span>
                </div>
                <div class="spec-row">
                  <span class="spec-label">适配净高:</span>
                  <span class="spec-value">{{ selectedModel.specs.净高 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="preview-footer">
          <button class="btn-secondary" @click="closeCustomShelfModal">取消</button>
          <button 
            class="btn-primary" 
            @click="addToMyModels" 
            :disabled="!selectedModel || selectedModel.prebuilt"
          >
            添加到我的模型
          </button>
        </div>
      </div>
    </div>

    <!-- 自定义墙体弹窗 -->
    <div v-if="showCustomWallModal" class="preview-modal" @click="closeCustomWallModal">
      <div class="preview-content custom-wall-modal" @click.stop>
        <div class="preview-header">
          <h3>自定义半透明墙体</h3>
          <button class="btn-close" @click="closeCustomWallModal">
            <X :size="20" />
          </button>
        </div>
        <div class="preview-body">
          <div class="form-section">
            <h4>墙体尺寸</h4>
            <div class="form-row">
              <div class="form-group">
                <label>长度 (mm)</label>
                <input
                  v-model.number="customWallParams.length"
                  type="number"
                  min="1000"
                  max="50000"
                  step="1000"
                  class="form-input"
                />
                <input
                  v-model.number="customWallParams.length"
                  type="range"
                  min="1000"
                  max="50000"
                  step="1000"
                  class="form-slider"
                />
                <span class="form-hint">{{ customWallParams.length / 1000 }}米</span>
              </div>
              <div class="form-group">
                <label>高度 (mm)</label>
                <input
                  v-model.number="customWallParams.height"
                  type="number"
                  min="2000"
                  max="15000"
                  step="500"
                  class="form-input"
                />
                <input
                  v-model.number="customWallParams.height"
                  type="range"
                  min="2000"
                  max="15000"
                  step="500"
                  class="form-slider"
                />
                <span class="form-hint">{{ customWallParams.height / 1000 }}米</span>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4>墙体名称</h4>
            <div class="form-group">
              <input
                v-model="customWallParams.name"
                type="text"
                placeholder="输入自定义墙体名称"
                class="form-input name-input"
              />
            </div>
          </div>

          <!-- 实时预览 -->
          <div class="preview-section">
            <h4>实时预览</h4>
            <div class="preview-info">
              <span>尺寸: {{ customWallParams.length }}×200×{{ customWallParams.height }}mm</span>
              <span>颜色: 淡青灰色调 (#E0F2F1)</span>
              <span>透明度: 70%通透</span>
              <span>风格: 草图大师纯色描边</span>
            </div>
          </div>
        </div>
        <div class="preview-footer">
          <button class="btn-secondary" @click="closeCustomWallModal">取消</button>
          <button class="btn-primary" @click="saveCustomWall" :disabled="!customWallParams.name">
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
import {
  LayoutGrid,
  Warehouse,
  Forklift,
  Package,
  MoveRight,
  ArrowLeftRight,
  Target,
  Settings,
  Users,
  Search,
  Plus,
  X,
  Eye
} from 'lucide-vue-next';

const router = useRouter();

// 分类数据（使用 Lucide 图标组件）
const categories = [
  { id: 'all', name: '全部模型', icon: LayoutGrid },
  { id: 'my-models', name: '我的模型', icon: Users },
  { id: 'facility', name: '仓库附属设施', icon: Warehouse },
  { id: 'light-shelf', name: '轻型货架', icon: Warehouse },
  { id: 'medium-shelf', name: '中型货架', icon: Warehouse },
  { id: 'heavy-shelf', name: '高位货架', icon: Warehouse },
  { id: 'other-shelf', name: '其他货架', icon: Warehouse },
  { id: 'handling', name: '搬运设备', icon: Forklift },
  { id: 'containers', name: '载具容器', icon: Package },
  { id: 'conveying', name: '输送设备', icon: MoveRight },
  { id: 'sorting', name: '分拨设备', icon: ArrowLeftRight },
  { id: 'picking', name: '拣选设备', icon: Target },
  { id: 'others', name: '其他设备', icon: Settings },
  { id: 'personnel', name: '人物模型', icon: Users },
];

// 模型数据（初始数据，后续从后端或JSON文件加载）
const models = ref([
  // 仓库附属设施 (F001-F099)
  {
    id: 'door-warehouse-standard',
    shortId: 'F001',
    name: '仓库标准门',
    category: 'facility',
    description: '仓库常用标准门，适用于人员进出和货物搬运',
    tags: ['门', '标准', '仓库设施'],
    parameters: {
      width: { type: 'number', min: 800, max: 2000, default: 1200, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 3000, default: 2400, unit: 'mm' },
    },
    modelUrl: '/assets/models/door-warehouse-standard.glb',
  },
  {
    id: 'window-warehouse-standard',
    shortId: 'F002',
    name: '仓库标准窗',
    category: 'facility',
    description: '仓库采光标准窗，提供自然光照',
    tags: ['窗', '标准', '仓库设施'],
    parameters: {
      width: { type: 'number', min: 600, max: 1500, default: 1000, unit: 'mm' },
      height: { type: 'number', min: 600, max: 1500, default: 1000, unit: 'mm' },
    },
    modelUrl: '/assets/models/window-warehouse-standard.glb',
  },
  {
    id: 'wall-warehouse-perimeter-glass',
    shortId: 'F003',
    name: '仓库外围墙体-半透明',
    category: 'facility',
    description: '长10m标准段，厚200mm，高8m',
    tags: ['墙体', '玻璃幕墙', '半透明', '仓库设施', '草图风格', '边界界定'],
    parameters: {
      length: { type: 'number', min: 5000, max: 20000, default: 10000, unit: 'mm' },
      width: { type: 'number', min: 100, max: 500, default: 200, unit: 'mm' },
      height: { type: 'number', min: 3000, max: 12000, default: 8000, unit: 'mm' },
    },
    modelUrl: '/assets/models/wall-warehouse-perimeter-glass.glb',
  },
  {
    id: 'door-industrial-sectional-4m',
    shortId: 'F004',
    name: '工业滑升门-标准4米',
    category: 'facility',
    description: '4米宽、4.2米高',
    tags: ['门', '滑升门', '工业门', '仓库设施', '装卸月台'],
    parameters: {
      openingWidth: { type: 'number', min: 3000, max: 6000, default: 4000, unit: 'mm' },
      openingHeight: { type: 'number', min: 3000, max: 6000, default: 4200, unit: 'mm' },
    },
    modelUrl: '/assets/models/door-industrial-sectional-4m.glb',
  },
  {
    id: 'window-industrial-awning-2m',
    shortId: 'F005',
    name: '工业采光窗-上悬式',
    category: 'facility',
    description: '宽2m×高1.2m、离地2m',
    tags: ['窗', '采光窗', '上悬窗', '仓库设施', '通风'],
    parameters: {
      frameWidth: { type: 'number', min: 1000, max: 3000, default: 2000, unit: 'mm' },
      frameHeight: { type: 'number', min: 600, max: 2000, default: 1200, unit: 'mm' },
      installationHeight: { type: 'number', min: 800, max: 4000, default: 2000, unit: 'mm' },
    },
    modelUrl: '/assets/models/window-industrial-awning-2m.glb',
  },
  // 货架系统 (A101-A199)
  // C23系列高位货架（只保留C23-3和配组）
  {
    id: 'high-duty-C23-3',
    shortId: 'C233',
    name: '3层高位货架-L2.3xD1.0xH3.0',
    category: 'heavy-shelf',
    description: '标准3层高位货架，适合4.5米以下仓库，叉车存取重型货物，单层层载1000-2000kg，层高1.35米，层板透明，带侧拉梁（4根40x25mm），立柱橙红色，横梁深蓝色',
    tags: ['高位货架', '叉车存取', '重型', 'C23系列'],
    parameters: {
      长度: { type: 'number', min: 2300, max: 2300, default: 2300, unit: 'mm' },
      深度: { type: 'number', min: 1000, max: 1000, default: 1000, unit: 'mm' },
      高度: { type: 'number', min: 3000, max: 3000, default: 3000, unit: 'mm' },
      层数: { type: 'number', min: 3, max: 3, default: 3, unit: '层' },
      层载重: { type: 'number', min: 1000, max: 2000, default: 1500, unit: 'kg' },
      标准层高: { type: 'number', min: 1350, max: 1350, default: 1350, unit: 'mm' },
      层板厚度: { type: 'number', min: 20, max: 20, default: 20, unit: 'mm' },
      适配净高: { type: 'string', default: '4.5米以下' },
      立柱颜色: { type: 'color', default: '#FF4500' },
      横梁颜色: { type: 'color', default: '#00008B' },
      层板颜色: { type: 'color', default: null },  // 透明
    },
    modelUrl: '/assets/models/high-duty-C23-3.glb',
  },
  // C23系列高位货架配组（背靠背，间距200mm）
  {
    id: 'high-duty-C23-3-pair',
    shortId: 'C233P',
    name: '3层高位货架-L2.3xD2.0xH3.0配组',
    category: 'heavy-shelf',
    description: 'C23-3高位货架背靠背配组，两组货架间距200mm，适合节省空间布局，总深度2200mm，层板透明，带侧拉梁和背靠背拉梁（8根40x25mm），立柱橙红色，横梁深蓝色',
    tags: ['高位货架', '叉车存取', '配组', '背靠背', 'C23系列'],
    parameters: {
      长度: { type: 'number', min: 2300, max: 2300, default: 2300, unit: 'mm' },
      深度: { type: 'number', min: 2200, max: 2200, default: 2200, unit: 'mm' },
      高度: { type: 'number', min: 3000, max: 3000, default: 3000, unit: 'mm' },
      层数: { type: 'number', min: 3, max: 3, default: 3, unit: '层' },
      层载重: { type: 'number', min: 1000, max: 2000, default: 1500, unit: 'kg' },
      标准层高: { type: 'number', min: 1350, max: 1350, default: 1350, unit: 'mm' },
      背靠背间距: { type: 'number', min: 200, max: 200, default: 200, unit: 'mm' },
      立柱颜色: { type: 'color', default: '#FF4500' },
      横梁颜色: { type: 'color', default: '#00008B' },
      层板颜色: { type: 'color', default: null },  // 透明
    },
    modelUrl: '/assets/models/high-duty-C23-3-pair.glb',
  },
  // B20系列中型货架定义在上面
  // 其他中型货架已清除，只保留B20-4和B20-4-pair
  {
    id: 'shelf-drive-in',
    shortId: 'A103',
    name: '驶入式货架-重型（L3600*D1500*H6000）',
    category: 'other-shelf',
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
    shortId: 'A104',
    name: '流利式货架-4层拣选（L900*D450*H1800）',
    category: 'other-shelf',
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
  // A15系列轻型货架
  {
    id: 'light-duty-A15-4',
    shortId: 'A104',
    name: '4层轻型货架-L1.5xD0.4xH2.0',
    category: 'light-shelf',
    description: '标准4层轻型搁板式货架，适合3米以下仓库，人工存取轻型货物，单层层载300-800kg，层高600mm，顶层配5cm挡板',
    tags: ['轻型货架', '搁板式', '人工存取', 'A15系列'],
    parameters: {
      长度: { type: 'number', min: 1500, max: 1500, default: 1500, unit: 'mm' },
      深度: { type: 'number', min: 400, max: 400, default: 400, unit: 'mm' },
      高度: { type: 'number', min: 2000, max: 2000, default: 2000, unit: 'mm' },
      层数: { type: 'number', min: 4, max: 4, default: 4, unit: '层' },
      层载重: { type: 'number', min: 300, max: 800, default: 500, unit: 'kg' },
      标准层高: { type: 'number', min: 600, max: 600, default: 600, unit: 'mm' },
      层板厚度: { type: 'number', min: 20, max: 20, default: 20, unit: 'mm' },
      适配净高: { type: 'string', default: '3米以下' },
      立柱颜色: { type: 'color', default: '#0066CC' },
      横梁颜色: { type: 'color', default: '#FF4500' },
      层板颜色: { type: 'color', default: '#FFFFFF' },
    },
    modelUrl: '/assets/models/light-duty-A15-4.glb',
  },
  // A15系列轻型货架配组（背靠背）
  {
    id: 'light-duty-A15-4-pair',
    shortId: 'A104P',
    name: '4层轻型货架-L1.5xD0.8xH2.0配组',
    category: 'light-shelf',
    description: 'A15-4轻型货架背靠背配组，两组货架间距0mm，适合节省空间布局，总深度800mm',
    tags: ['轻型货架', '搁板式', '配组', '背靠背', 'A15系列'],
    parameters: {
      长度: { type: 'number', min: 1500, max: 1500, default: 1500, unit: 'mm' },
      深度: { type: 'number', min: 800, max: 800, default: 800, unit: 'mm' },
      高度: { type: 'number', min: 2000, max: 2000, default: 2000, unit: 'mm' },
      层数: { type: 'number', min: 4, max: 4, default: 4, unit: '层' },
      层载重: { type: 'number', min: 300, max: 800, default: 500, unit: 'kg' },
      标准层高: { type: 'number', min: 600, max: 600, default: 600, unit: 'mm' },
      背靠背间距: { type: 'number', min: 0, max: 0, default: 0, unit: 'mm' },
      立柱颜色: { type: 'color', default: '#0066CC' },
      横梁颜色: { type: 'color', default: '#FF4500' },
      层板颜色: { type: 'color', default: '#FFFFFF' },
    },
    modelUrl: '/assets/models/light-duty-A15-4-pair.glb',
  },
  // C23系列高位货架定义在上面
  // 其他高位货架已清除，只保留C23-3和C23-3-pair
  // B20系列中型货架（只保留B20-4和配组）
  {
    id: 'medium-duty-B20-4',
    shortId: 'B204',
    name: '4层中型货架-L2.0xD0.6xH2.0',
    category: 'medium-shelf',
    description: '标准4层中型货架，适合3米以下仓库，人工存取中型货物，单层层载500-800kg，层高600mm，顶层配50mm挡板，立柱深蓝色，横梁橙红色',
    tags: ['中型货架', '搁板式', '人工存取', 'B20系列'],
    parameters: {
      长度: { type: 'number', min: 2000, max: 2000, default: 2000, unit: 'mm' },
      深度: { type: 'number', min: 600, max: 600, default: 600, unit: 'mm' },
      高度: { type: 'number', min: 2000, max: 2000, default: 2000, unit: 'mm' },
      层数: { type: 'number', min: 4, max: 4, default: 4, unit: '层' },
      层载重: { type: 'number', min: 500, max: 800, default: 800, unit: 'kg' },
      标准层高: { type: 'number', min: 600, max: 600, default: 600, unit: 'mm' },
      层板厚度: { type: 'number', min: 20, max: 20, default: 20, unit: 'mm' },
      适配净高: { type: 'string', default: '3米以下' },
      立柱颜色: { type: 'color', default: '#00008B' },
      横梁颜色: { type: 'color', default: '#FF4500' },
      层板颜色: { type: 'color', default: '#FFFFFF' },
    },
    modelUrl: '/assets/models/medium-duty-B20-4.glb',
  },
  // B20系列中型货架配组（背靠背）
  {
    id: 'medium-duty-B20-4-pair',
    shortId: 'B204P',
    name: '4层中型货架-L2.0xD1.2xH2.0配组',
    category: 'medium-shelf',
    description: 'B20-4中型货架背靠背配组，两组货架间距0mm，适合节省空间布局，总深度1200mm，立柱深蓝色，横梁橙红色',
    tags: ['中型货架', '搁板式', '配组', '背靠背', 'B20系列'],
    parameters: {
      长度: { type: 'number', min: 2000, max: 2000, default: 2000, unit: 'mm' },
      深度: { type: 'number', min: 1200, max: 1200, default: 1200, unit: 'mm' },
      高度: { type: 'number', min: 2000, max: 2000, default: 2000, unit: 'mm' },
      层数: { type: 'number', min: 4, max: 4, default: 4, unit: '层' },
      层载重: { type: 'number', min: 500, max: 800, default: 800, unit: 'kg' },
      标准层高: { type: 'number', min: 600, max: 600, default: 600, unit: 'mm' },
      背靠背间距: { type: 'number', min: 0, max: 0, default: 0, unit: 'mm' },
      立柱颜色: { type: 'color', default: '#00008B' },
      横梁颜色: { type: 'color', default: '#FF4500' },
      层板颜色: { type: 'color', default: '#FFFFFF' },
    },
    modelUrl: '/assets/models/medium-duty-B20-4-pair.glb',
  },
  // 载具容器 (C101-C199)
  {
    id: 'pallet-wooden-1200',
    shortId: 'C101',
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
    shortId: 'C102',
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
    shortId: 'C103',
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
    shortId: 'C104',
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
    shortId: 'C105',
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
    shortId: 'C106',
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
    shortId: 'C107',
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
    shortId: 'C108',
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
  // 搬运设备 (B101-B199)
  {
    id: 'forklift-reach-2t-9m',
    shortId: 'B101',
    name: '前移式叉车-2吨9米',
    category: 'handling',
    description: '前移式叉车，窄通道高位存取，适配重型5层立体库，举升高度9米，通道宽度2.8米',
    tags: ['前移式叉车', '窄通道', '高位存取', '2吨', '9米', '搬运设备'],
    parameters: {
      length: { type: 'number', min: 2500, max: 3500, default: 2900, unit: 'mm' },
      width: { type: 'number', min: 1000, max: 1300, default: 1100, unit: 'mm' },
      height: { type: 'number', min: 2200, max: 2800, default: 2500, unit: 'mm' },
      liftHeight: { type: 'number', min: 6000, max: 12000, default: 9000, unit: 'mm' },
    },
    modelUrl: '/assets/models/forklift-reach-2t.glb',
  },
  {
    id: 'forklift-counterbalance-2.5t-4m',
    shortId: 'B102',
    name: '平衡重叉车-2.5吨4米',
    category: 'handling',
    description: '平衡重叉车，通用型搬运设备，适合室内外作业，适配重型3-4层货架，通道宽度3.5米',
    tags: ['平衡重叉车', '通用型', '室内外', '2.5吨', '4米', '搬运设备'],
    parameters: {
      length: { type: 'number', min: 2800, max: 3600, default: 3200, unit: 'mm' },
      width: { type: 'number', min: 1100, max: 1300, default: 1200, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 2400, default: 2200, unit: 'mm' },
      liftHeight: { type: 'number', min: 3000, max: 6000, default: 4000, unit: 'mm' },
    },
    modelUrl: '/assets/models/forklift-counterbalance-2.5t.glb',
  },
  {
    id: 'forklift-pallet-truck-electric-2t',
    shortId: 'B103',
    name: '电动搬运车-2吨步行式',
    category: 'handling',
    description: '平库及重型货架底层搬运专用，步行式操作，适合短距离水平搬运，通道宽度2.2米',
    tags: ['电动搬运车', '步行式', '平库搬运', '2吨', '搬运设备'],
    parameters: {
      length: { type: 'number', min: 1600, max: 2100, default: 1850, unit: 'mm' },
      width: { type: 'number', min: 550, max: 750, default: 680, unit: 'mm' },
      height: { type: 'number', min: 1200, max: 1500, default: 1350, unit: 'mm' },
      liftHeight: { type: 'number', min: 150, max: 250, default: 200, unit: 'mm' },
    },
    modelUrl: '/assets/models/forklift-pallet-truck-electric.glb',
  },
  {
    id: 'forklift-pallet-jack-manual-2.5t',
    shortId: 'B104',
    name: '手动液压搬运车-2.5吨',
    category: 'handling',
    description: '最基础搬运设备，纯机械操作，适合小仓库或预算有限场景',
    tags: ['手动搬运车', '液压', '基础款', '2.5吨', '搬运设备'],
    parameters: {
      length: { type: 'number', min: 1400, max: 1700, default: 1550, unit: 'mm' },
      width: { type: 'number', min: 500, max: 600, default: 550, unit: 'mm' },
      height: { type: 'number', min: 1100, max: 1300, default: 1200, unit: 'mm' },
      liftHeight: { type: 'number', min: 150, max: 250, default: 200, unit: 'mm' },
    },
    modelUrl: '/assets/models/forklift-pallet-jack-manual.glb',
  },
  {
    id: 'cart-picking-3tier-900',
    shortId: 'B105',
    name: '三层拣货车-标准型',
    category: 'handling',
    description: '人工拣选作业专用，配合中型/轻型货架使用，适用于电商仓、零售仓的订单拣选',
    tags: ['拣货车', '三层', '人工拣选', '电商仓', '搬运设备'],
    parameters: {
      length: { type: 'number', min: 700, max: 1100, default: 900, unit: 'mm' },
      width: { type: 'number', min: 350, max: 550, default: 450, unit: 'mm' },
      height: { type: 'number', min: 1000, max: 1400, default: 1200, unit: 'mm' },
      tiers: { type: 'number', min: 2, max: 4, default: 3 },
    },
    modelUrl: '/assets/models/cart-picking-3tier.glb',
  },
  {
    id: 'cart-cage-logistics-2tier',
    shortId: 'B106',
    name: '物流笼车-2层标准款',
    category: 'handling',
    description: '带围栏多层结构，适用于电商仓、配送中心货物转运及超市配送',
    tags: ['笼车', '物流笼车', '2层', '可折叠', '配送'],
    parameters: {
      length: { type: 'number', min: 700, max: 900, default: 800, unit: 'mm' },
      width: { type: 'number', min: 500, max: 700, default: 600, unit: 'mm' },
      height: { type: 'number', min: 1500, max: 1900, default: 1700, unit: 'mm' },
    },
    modelUrl: '/assets/models/cart-cage-logistics-2tier.glb',
  },
  // 输送设备 (D101-D199)
  {
    id: 'lift-cargo-hydraulic-3floor',
    shortId: 'D101',
    name: '液压货物提升机-3层阁楼',
    category: 'conveying',
    description: '3层阁楼库专用，货物垂直转运，严禁载人',
    tags: ['提升机', '液压', '3层', '阁楼库', '垂直转运'],
    parameters: {
      cabinLength: { type: 'number', min: 1200, max: 1600, default: 1400, unit: 'mm' },
      cabinWidth: { type: 'number', min: 1000, max: 1400, default: 1200, unit: 'mm' },
      totalHeight: { type: 'number', min: 5000, max: 7000, default: 6000, unit: 'mm' },
      loadCapacity: { type: 'number', min: 500, max: 2000, default: 1000, unit: 'kg' },
    },
    modelUrl: '/assets/models/lift-cargo-hydraulic-3floor.glb',
  },
  {
    id: 'conveyor-curve-90degree-600',
    shortId: 'D102',
    name: '90度皮带转弯机-带宽600mm',
    category: 'conveying',
    description: '用于输送线在水平面内90度转向，连接直段输送线形成闭环或改变输送方向',
    tags: ['转弯机', '90度', '皮带输送', '输送线'],
    parameters: {
      width: { type: 'number', min: 1000, max: 1500, default: 1200, unit: 'mm' },
      height: { type: 'number', min: 600, max: 1000, default: 800, unit: 'mm' },
      innerRadius: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
      beltWidth: { type: 'number', min: 400, max: 800, default: 600, unit: 'mm' },
    },
    modelUrl: '/assets/models/conveyor-curve-90degree-600.glb',
  },
  {
    id: 'conveyor-roller-straight-600-red',
    shortId: 'D103',
    name: '动力滚筒输送机-直线段（红框银筒）',
    category: 'conveying',
    description: '红框银筒配色，与90度转弯机配套使用，视觉对比强烈',
    tags: ['滚筒输送机', '红框银筒', '直线段', '输送线'],
    parameters: {
      length: { type: 'number', min: 1000, max: 4000, default: 2000, unit: 'mm' },
      width: { type: 'number', min: 400, max: 800, default: 600, unit: 'mm' },
      height: { type: 'number', min: 600, max: 1000, default: 800, unit: 'mm' },
    },
    modelUrl: '/assets/models/conveyor-roller-straight-600-red.glb',
  },
  // 拣选设备 (E101-E199)
  {
    id: 'putwall-standard-16cell',
    shortId: 'E101',
    name: '电子标签播种墙-16格口',
    category: 'picking',
    description: '电商仓订单分拣核心设备，用于货到人后的订单播种作业',
    tags: ['播种墙', '电子标签', '分拣', '16格口', '电商仓'],
    parameters: {
      width: { type: 'number', min: 1200, max: 2000, default: 1600, unit: 'mm' },
      depth: { type: 'number', min: 400, max: 600, default: 500, unit: 'mm' },
      height: { type: 'number', min: 1500, max: 2200, default: 1800, unit: 'mm' },
      rows: { type: 'number', min: 2, max: 6, default: 4 },
      cols: { type: 'number', min: 2, max: 6, default: 4 },
    },
    modelUrl: '/assets/models/putwall-standard-16cell.glb',
  },
  {
    id: 'station-packcheck-integrated-red',
    shortId: 'E102',
    name: '复核打包一体作业台-红白配色',
    category: 'picking',
    description: '红白配色与红色输送线配套，视觉冲击力强，适用于电商仓订单处理末端',
    tags: ['作业台', '复核打包', '红白配色', '电商仓'],
    parameters: {
      length: { type: 'number', min: 1500, max: 2200, default: 1800, unit: 'mm' },
      width: { type: 'number', min: 700, max: 1100, default: 900, unit: 'mm' },
      height: { type: 'number', min: 1800, max: 2200, default: 2000, unit: 'mm' },
    },
    modelUrl: '/assets/models/station-packcheck-integrated-red.glb',
  },
  {
    id: 'weigher-automatic-check-600-red',
    shortId: 'E103',
    name: '自动称重机-动态检重（红白配色）',
    category: 'picking',
    description: '三段式皮带结构，用于包裹自动称重与异常剔除，与红色输送线配套',
    tags: ['称重机', '动态检重', '三段式', '红白配色', '电商仓'],
    parameters: {
      length: { type: 'number', min: 1400, max: 2000, default: 1600, unit: 'mm' },
      width: { type: 'number', min: 600, max: 800, default: 700, unit: 'mm' },
      height: { type: 'number', min: 700, max: 900, default: 800, unit: 'mm' },
    },
    modelUrl: '/assets/models/weigher-automatic-check-600-red.glb',
  },
  // 其他设备 (F101-F199)
  {
    id: 'guard-rack-heavy-redyellow',
    shortId: 'F101',
    name: '高位货架防撞护栏-红黄警示',
    category: 'others',
    description: '红黄间隔反光警示色，安装于重型货架端头或转角，防止叉车碰撞',
    tags: ['防撞护栏', '红黄警示', '货架防护', '安全设施'],
    parameters: {
      length: { type: 'number', min: 1200, max: 2000, default: 1500, unit: 'mm' },
      width: { type: 'number', min: 100, max: 200, default: 150, unit: 'mm' },
      height: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
    },
    modelUrl: '/assets/models/guard-rack-heavy-redyellow.glb',
  },
  {
    id: 'guard-column-protector-redyellow',
    shortId: 'F102',
    name: '货架立柱防撞护角-红黄U型',
    category: 'others',
    description: '红黄间隔反光警示色，紧密安装于重型货架立柱底部，防止叉车叉臂直接撞击立柱',
    tags: ['防撞护角', '立柱保护', 'U型包裹', '红黄警示'],
    parameters: {
      width: { type: 'number', min: 100, max: 150, default: 120, unit: 'mm' },
      depth: { type: 'number', min: 100, max: 150, default: 120, unit: 'mm' },
      height: { type: 'number', min: 300, max: 500, default: 400, unit: 'mm' },
    },
    modelUrl: '/assets/models/guard-column-protector-redyellow.glb',
  },
  // 人员 (G101-G199)
  {
    id: 'person-warehouse-admin-red',
    shortId: 'G101',
    name: '仓库管理员-红帽黄马甲',
    category: 'personnel',
    description: '佩戴红色安全帽、红黄反光马甲，用于场景人员密度规划、作业流程演示及安全规范展示',
    tags: ['人员', '仓库管理员', '红帽黄马甲', '安全着装'],
    parameters: {
      height: { type: 'number', min: 1600, max: 1900, default: 1750, unit: 'mm' },
      shoulderWidth: { type: 'number', min: 400, max: 500, default: 450, unit: 'mm' },
    },
    modelUrl: '/assets/models/person-warehouse-admin-red.glb',
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

// ==================== 新的自定义货架选择器状态 ====================
const shelfCategories = ref([]);
const selectedCategory = ref('');
// selectedModel 已在第957行声明，这里不再重复声明
const availableModels = ref([]);

// 加载货架元数据
const loadShelfMetadata = async () => {
  try {
    const response = await fetch('/assets/shelf-models-metadata.json');
    const data = await response.json();
    shelfCategories.value = data.categories;
  } catch (error) {
    console.error('加载货架元数据失败:', error);
  }
};

// 分类改变时更新可用模型列表
const onCategoryChange = () => {
  selectedModel.value = null;
  if (selectedCategory.value) {
    const category = shelfCategories.value.find(c => c.id === selectedCategory.value);
    availableModels.value = category ? category.models : [];
  } else {
    availableModels.value = [];
  }
};

// 模型选择改变
const onModelChange = () => {
  // 模型选择后自动触发预览更新
};

// 添加到我的模型
const addToMyModels = () => {
  if (!selectedModel.value || selectedModel.value.prebuilt) {
    alert('该模型已预置，无需重复添加');
    return;
  }
  
  // 检查是否已存在
  const existingMyModels = models.value.filter(m => m.category === 'my-models');
  const exists = existingMyModels.some(m => m.id === selectedModel.value.id);
  
  if (exists) {
    alert('该模型已在"我的模型"中，请勿重复添加');
    return;
  }
  
  // 创建新模型对象
  const newModel = {
    id: selectedModel.value.id,
    shortId: `M${Date.now().toString().slice(-3)}`,
    name: selectedModel.value.name,
    category: 'my-models',
    description: `${selectedCategory.value === 'light-shelf' ? '轻型' : selectedCategory.value === 'medium-shelf' ? '中型' : '高位'}货架，承重${selectedModel.value.specs.承重}，层高${selectedModel.value.specs.层高}，适配${selectedModel.value.specs.净高}`,
    tags: ['自定义货架', selectedCategory.value === 'light-shelf' ? '轻型' : selectedCategory.value === 'medium-shelf' ? '中型' : '高位'],
    parameters: {
      承重: { type: 'string', default: selectedModel.value.specs.承重 },
      层高: { type: 'string', default: selectedModel.value.specs.层高 },
      适配净高: { type: 'string', default: selectedModel.value.specs.净高 }
    },
    modelUrl: selectedModel.value.file,
    isCustom: true,
    specs: selectedModel.value.specs
  };
  
  // 添加到模型列表
  models.value.push(newModel);
  
  // 保存到localStorage
  const myModels = models.value.filter(m => m.category === 'my-models');
  localStorage.setItem('myModels', JSON.stringify(myModels));
  
  // 关闭弹窗并提示
  closeCustomShelfModal();
  alert(`"${selectedModel.value.name}"已添加到"我的模型"！`);
};

// 初始化时加载货架元数据
loadShelfMetadata();

// ==================== 自定义墙体弹窗显示状态
const showCustomWallModal = ref(false);

// 自定义墙体参数
const customWallParams = ref({
  name: '',
  length: 10000,
  height: 8000,
});

// 从localStorage加载自定义货架（兼容旧数据）
const loadCustomShelves = () => {
  // 加载新的"我的模型"
  const myModelsSaved = localStorage.getItem('myModels');
  if (myModelsSaved) {
    const myModels = JSON.parse(myModelsSaved);
    models.value = [...models.value, ...myModels];
  }
  
  // 兼容旧数据：加载旧的 customShelves
  const saved = localStorage.getItem('customShelves');
  if (saved) {
    const customShelves = JSON.parse(saved);
    // 将旧数据转换为 my-models 分类
    const migratedModels = customShelves.map(shelf => ({
      ...shelf,
      category: 'my-models'
    }));
    models.value = [...models.value, ...migratedModels];
    // 保存到新的 key
    const allMyModels = models.value.filter(m => m.category === 'my-models');
    localStorage.setItem('myModels', JSON.stringify(allMyModels));
    // 删除旧 key
    localStorage.removeItem('customShelves');
  }
};

// 为模型分配短ID（用户识别ID）
const assignShortIds = () => {
  const categoryLetters = {
    'facility': 'F',
    'storage': 'A',
    'handling': 'B',
    'containers': 'C',
    'conveying': 'D',
    'picking': 'E',
    'sorting': 'H',
    'others': 'I',
    'personnel': 'G',
  };

  // 计算每个类别当前的最新短ID编号
  const categoryCounters = {};
  
  models.value.forEach((model) => {
    if (model.shortId) {
      const letter = model.shortId.charAt(0);
      const num = parseInt(model.shortId.slice(1));
      if (!categoryCounters[letter] || categoryCounters[letter] < num) {
        categoryCounters[letter] = num;
      }
    }
  });

  models.value.forEach((model) => {
    if (!model.shortId) {
      const letter = categoryLetters[model.category] || 'H';
      // 从当前最大编号+1开始，或从101开始
      const currentMax = categoryCounters[letter] || 100;
      const counter = currentMax + 1;
      categoryCounters[letter] = counter;
      model.shortId = `${letter}${counter}`;
    }
  });
};

// 在初始化时分配短ID
assignShortIds();

// 通过短ID查找模型（用于人机交互）
const findModelByShortId = (shortId) => {
  return models.value.find(model => model.shortId === shortId);
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
  // 重置选择器状态
  selectedCategory.value = '';
  selectedModel.value = null;
  availableModels.value = [];
  // 重新加载元数据
  loadShelfMetadata();
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
    category: 'my-models', // 【修改】保存到"我的模型"分类
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

  // 分配短ID
  assignShortIds();

  // 【修改】保存到localStorage（使用myModels key）
  const myModels = models.value.filter(m => m.category === 'my-models');
  localStorage.setItem('myModels', JSON.stringify(myModels));
  
  // 关闭弹窗
  closeCustomShelfModal();
  
  // 显示成功提示（可以添加toast组件）
  alert('自定义货架已保存到对象库！');
};

// 打开自定义墙体弹窗
const openCustomWallModal = () => {
  console.log('openCustomWallModal called');
  showCustomWallModal.value = true;
};

// 关闭自定义墙体弹窗
const closeCustomWallModal = () => {
  showCustomWallModal.value = false;
};

// 保存自定义墙体
const saveCustomWall = () => {
  const params = customWallParams.value;
  
  const newWall = {
    id: `custom-wall-${Date.now()}`,
    name: params.name || `自定义墙体-${params.length/1000}×${params.height/1000}m`,
    category: 'facility',
    description: `长${params.length/1000}m×厚0.2m×高${params.height/1000}m`,
    tags: ['自定义', '墙体', '半透明', '玻璃幕墙'],
    parameters: {
      length: { type: 'number', min: 1000, max: 50000, default: params.length, unit: 'mm' },
      width: { type: 'number', min: 200, max: 200, default: 200, unit: 'mm' },
      height: { type: 'number', min: 2000, max: 15000, default: params.height, unit: 'mm' },
    },
    modelUrl: '/assets/models/wall-warehouse-perimeter-glass.glb', // 使用现有墙体模型作为基础
    isCustom: true,
    customParams: { ...params },
    customType: 'wall'
  };
  
  // 添加到模型列表
  models.value.push(newWall);
  
  // 分配短ID
  assignShortIds();
  
  // 保存到localStorage
  const customWalls = models.value.filter(m => m.isCustom && m.category === 'facility');
  localStorage.setItem('customWalls', JSON.stringify(customWalls));
  
  // 关闭弹窗
  closeCustomWallModal();
  
  // 显示成功提示
  alert('自定义墙体已保存到对象库！');
};

// 从localStorage加载自定义墙体
const loadCustomWalls = () => {
  const saved = localStorage.getItem('customWalls');
  if (saved) {
    const customWalls = JSON.parse(saved);
    models.value = [...models.value, ...customWalls];
  }
};

// 初始化时加载自定义货架
loadCustomShelves();

// 初始化时加载自定义墙体
loadCustomWalls();

// 加载自定义货架后，再次分配短ID
assignShortIds();

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
  return category?.icon || LayoutGrid;
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
  display: flex;
  gap: 0.75rem;
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

.btn-custom-wall {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3);
}

.btn-custom-wall:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
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

/* 自定义墙体弹窗 */
.custom-wall-modal {
  max-width: 600px;
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

/* 新的自定义货架弹窗样式 */
/* 覆盖默认的grid布局 */
.preview-content.custom-shelf-modal .preview-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: auto;
  min-height: 400px;
}

.custom-shelf-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selectors-row {
  display: flex;
  gap: 1rem;
}

.selector-half {
  flex: 1;
}

.category-select,
.model-select {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  border: 1px solid #e0e0e8;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.category-select:focus,
.model-select:focus {
  outline: none;
  border-color: #4361ee;
  box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
}

.model-select option:disabled {
  color: #999;
  background: #f5f5f5;
  font-style: italic;
}

/* 3D预览和规格并排布局 */
.preview-and-specs {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.preview-3d-section-large {
  flex: 2;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e0e0e8;
}

.preview-3d-section-large h4 {
  padding: 0.75rem 1rem;
  background: #f8f9ff;
  margin: 0;
  font-size: 0.95rem;
  color: #2d2d44;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e8;
}

.preview-3d-container-large {
  height: 300px;
  background: #f0f0f5;
}

.specs-section-compact {
  flex: 1;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid #e8ecff;
}

.specs-section-compact h4 {
  color: #2d2d44;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  font-weight: 600;
}

.specs-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.spec-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e0e0e8;
}

.spec-row:last-child {
  border-bottom: none;
}

.spec-label {
  font-size: 0.85rem;
  color: #6b6b8a;
  font-weight: 500;
}

.spec-value {
  font-size: 0.95rem;
  color: #4361ee;
  font-weight: 600;
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
  line-height: 1.4;
}

.model-id {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #4361ee;
  background: #f0f3ff;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  margin-right: 0.5rem;
  vertical-align: middle;
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
  grid-template-columns: 3fr 1fr;
  gap: 1rem;
  padding: 1rem;
  overflow: hidden;
  height: 600px;
}

.preview-3d {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
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
  padding: 0.75rem;
  background: #f8f9ff;
  border-radius: 12px;
  overflow-y: auto;
  max-height: 100%;
}

.preview-params h4 {
  font-size: 1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.param-item {
  margin-bottom: 0.5rem;
}

.param-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.param-header label {
  font-size: 0.75rem;
  color: #4a4a68;
}

.param-value {
  font-size: 0.75rem;
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
