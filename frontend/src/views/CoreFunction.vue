<template>
  <div class="core-function">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-group">
        <span class="group-title">项目</span>
        <button @click="importProject">导入项目</button>
        <button @click="saveProject">保存项目</button>
        <button @click="generateReport" :disabled="!isProjectSaved">项目报告</button>
        <button @click="deleteProject">删除项目</button>
        <button @click="exportImage">导出效果图</button>
      </div>
      <div class="toolbar-group">
        <span class="group-title">添加</span>
        <button @click="openModelLibrary" class="btn-primary">添加模型</button>
      </div>
    </div>
    
    <div class="main-layout">
      <!-- 左侧对象库面板 -->
      <div class="left-panel">
        <!-- 对象库组 -->
        <div class="panel">
          <h3 class="panel-title">
            <span class="panel-icon">📦</span>
            对象库
          </h3>
          <div class="model-categories">
            <div class="category">
              <div class="category-header" @click="toggleCategory('logistics')">
                <span class="category-icon">{{ expandedCategories.logistics ? '▼' : '▶' }}</span>
                <span>物流对象模型</span>
              </div>
              <div class="category-content" v-show="expandedCategories.logistics">
                <div class="model-list">
                  <div 
                    class="model-item draggable"
                    draggable="true"
                    @dragstart="onDragStart($event, 'shelf_with_pallet.glb')"
                  >
                    <span class="model-icon">🏗️</span>
                    <span class="model-name">横梁式重型货架</span>
                    
                    <!-- 悬停提示框 -->
                    <div class="model-tooltip">
                      <div class="tooltip-header">横梁式重型货架</div>
                      <div class="tooltip-content">
                        <div class="tooltip-row">
                          <span class="tooltip-label">尺寸:</span>
                          <span class="tooltip-value">2.7m × 1.0m × 4.5m</span>
                        </div>
                        <div class="tooltip-row">
                          <span class="tooltip-label">承重:</span>
                          <span class="tooltip-value">2000kg/层</span>
                        </div>
                        <div class="tooltip-row">
                          <span class="tooltip-label">层数:</span>
                          <span class="tooltip-value">4层</span>
                        </div>
                        <div class="tooltip-row">
                          <span class="tooltip-label">材质:</span>
                          <span class="tooltip-value">优质冷轧钢</span>
                        </div>
                        <div class="tooltip-description">
                          适用于仓库存放重型货物
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="category">
              <div class="category-header" @click="toggleCategory('scene')">
                <span class="category-icon">{{ expandedCategories.scene ? '▼' : '▶' }}</span>
                <span>仓库场景模型</span>
              </div>
              <div class="category-content" v-show="expandedCategories.scene">
                <p class="empty-hint">暂无场景模型</p>
              </div>
            </div>
          </div>
          <p class="panel-hint">拖动模型到画布中放置</p>
        </div>
        
        <!-- 对象操作组 -->
        <div class="panel" v-if="selectedObject">
          <h3 class="panel-title">
            <span class="panel-icon">🎯</span>
            对象操作
          </h3>
          <div class="selection-info">
            <p class="panel-desc" v-if="selectedObjectCount > 1">已选择 {{ selectedObjectCount }} 个对象</p>
            <p class="panel-desc" v-else>已选择 1 个对象</p>
            <p class="panel-hint">按住 Ctrl 键可多选</p>
          </div>
          
          <div class="operation-section">
            <span class="section-label">变换</span>
            <div class="object-controls">
              <button @click="moveObject" :class="{ active: isMoving }">
                <span class="btn-icon">↔️</span>
                移动
              </button>
              <button @click="startRotate" :class="{ active: isRotating }">
                <span class="btn-icon">🔄</span>
                {{ isRotating ? '拖动旋转' : '旋转' }}
              </button>
            </div>
          </div>
          
          <div class="operation-section">
            <span class="section-label">复制</span>
            <div class="object-controls">
              <button @click="showBatchCopyPanel" v-if="selectedObjectCount === 1">
                <span class="btn-icon">📋</span>
                批量复制
              </button>
            </div>
          </div>
          
          <div class="operation-section">
            <span class="section-label">删除</span>
            <div class="object-controls">
              <button @click="deleteObject" class="delete-btn">
                <span class="btn-icon">🗑️</span>
                删除对象
              </button>
            </div>
          </div>
          
          <p v-if="isRotating" class="rotate-hint">请在场景中拖动来旋转模型</p>
        </div>
        
        <!-- 场景操作组 -->
        <div class="panel">
          <h3 class="panel-title">
            <span class="panel-icon">🎬</span>
            场景操作
          </h3>
          <div class="control-buttons">
            <button @click="clearScene" class="warning-btn">
              <span class="btn-icon">🧹</span>
              清空场景
            </button>
          </div>
        </div>
        
        <!-- 保存项目对话框 -->
        <div class="modal-overlay" v-if="showSaveDialog" @click.self="showSaveDialog = false">
          <div class="modal-dialog">
            <h3 class="modal-title">保存项目</h3>
            <div class="modal-content">
              <div class="form-group">
                <label>项目名称：</label>
                <input 
                  type="text" 
                  v-model="projectName" 
                  placeholder="请输入项目名称"
                  @keyup.enter="confirmSaveProject"
                >
              </div>
            </div>
            <div class="modal-actions">
              <button @click="confirmSaveProject" class="confirm-btn">保存</button>
              <button @click="showSaveDialog = false" class="cancel-btn">取消</button>
            </div>
          </div>
        </div>
        
        <!-- 批量复制面板 -->
        <div class="panel batch-panel" v-if="showBatchPanel">
          <h3 class="panel-title">
            <span class="panel-icon">📋</span>
            批量复制
          </h3>
          <div class="batch-copy-controls">
            <div class="control-group">
              <label>复制模式:</label>
              <div class="direction-buttons">
                <button :class="{ active: batchCopyMode === 'horizontal' }" @click="batchCopyMode = 'horizontal'">横向复制</button>
                <button :class="{ active: batchCopyMode === 'vertical' }" @click="batchCopyMode = 'vertical'">纵向复制</button>
              </div>
            </div>
            
            <div v-if="batchCopyMode === 'horizontal'">
              <div class="control-group">
                <label>总组数: {{ batchCopyTotalGroups }} 组</label>
                <input type="range" v-model.number="batchCopyTotalGroups" min="2" max="20">
                <span class="hint">包含基准货架，共{{ batchCopyTotalGroups }}组横向排列</span>
              </div>
              <div class="control-group">
                <label>方向:</label>
                <div class="direction-buttons">
                  <button :class="{ active: batchCopyHDirection === 'positive' }" @click="batchCopyHDirection = 'positive'">X轴正方向</button>
                  <button :class="{ active: batchCopyHDirection === 'negative' }" @click="batchCopyHDirection = 'negative'">X轴负方向</button>
                </div>
              </div>
              <p class="info-text">横向排列固定10CM间距，共用中间立柱</p>
            </div>
            
            <div v-if="batchCopyMode === 'vertical'">
              <div class="control-group">
                <label>纵向列数: {{ batchCopyColumns }} 列</label>
                <input type="range" v-model.number="batchCopyColumns" min="2" max="10">
              </div>
              <div class="control-group">
                <label>每列组数: {{ batchCopyGroupsPerColumn }} 组</label>
                <input type="range" v-model.number="batchCopyGroupsPerColumn" min="1" max="10">
              </div>
              <div class="control-group">
                <label>列间通道间距: {{ batchCopyColumnSpacing }} 米</label>
                <input type="range" v-model.number="batchCopyColumnSpacing" min="0.5" max="5" step="0.1">
                <span class="hint">列与列之间的通道宽度</span>
              </div>
              <div class="control-group">
                <label>方向:</label>
                <div class="direction-buttons">
                  <button :class="{ active: batchCopyVDirection === 'positive' }" @click="batchCopyVDirection = 'positive'">Z轴正方向</button>
                  <button :class="{ active: batchCopyVDirection === 'negative' }" @click="batchCopyVDirection = 'negative'">Z轴负方向</button>
                </div>
              </div>
            </div>
            
            <div class="batch-actions">
              <button @click="previewBatchCopy" class="preview-btn">预览</button>
              <button @click="confirmBatchCopy" class="confirm-btn">确认放置</button>
              <button @click="cancelBatchCopy" class="cancel-btn">取消</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="canvas-container">
        <ThreeScene 
          ref="threeScene"
          @model-added="onModelAdded"
          @object-selected="onObjectSelected"
          @object-deselected="onObjectDeselected"
          @save-project="saveProject"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ThreeScene from '../components/3d/ThreeScene.vue';

const threeScene = ref(null);
const selectedObject = ref(null);
const selectedObjectCount = ref(0);
const isRotating = ref(false);
const isMoving = ref(false);
const showBatchPanel = ref(false);
const isProjectSaved = ref(false);
const projectReport = ref(null);
const showSaveDialog = ref(false);
const projectName = ref('');

// 对象库分类展开状态
const expandedCategories = ref({
  logistics: true,
  scene: false
});

// 悬停提示状态
const hoveredModel = ref(null);

// 模型属性数据
const modelProperties = {
  'shelf_with_pallet.glb': {
    name: '横梁式重型货架',
    dimensions: { length: 2.7, width: 1.0, height: 4.5 },
    loadCapacity: '2000kg/层',
    layers: 4,
    material: '优质冷轧钢',
    description: '适用于仓库存放重型货物'
  }
};

function showTooltip(modelName) {
  hoveredModel.value = modelName;
}

function hideTooltip() {
  hoveredModel.value = null;
}

// 批量复制参数
const batchCopyMode = ref('horizontal');
const batchCopyTotalGroups = ref(5);
const batchCopyHDirection = ref('positive');
const batchCopyColumns = ref(3);
const batchCopyGroupsPerColumn = ref(2);
const batchCopyColumnSpacing = ref(1.5);
const batchCopyVDirection = ref('positive');

function toggleCategory(category) {
  expandedCategories.value[category] = !expandedCategories.value[category];
}

// 项目操作
function importProject() {
  alert('导入项目功能开发中...');
}

// 打开模型库
function openModelLibrary() {
  // 在新标签页打开模型库
  window.open('/models', '_blank');
}

function saveProject() {
  showSaveDialog.value = true;
  projectName.value = '';
}

function confirmSaveProject() {
  if (!projectName.value.trim()) {
    alert('请输入项目名称！');
    return;
  }
  
  // 生成项目报告数据
  generateProjectData();
  isProjectSaved.value = true;
  showSaveDialog.value = false;
  
  // 导出项目JSON文件
  exportProjectJSON();
  
  alert(`项目"${projectName.value}"已保存！现在可以生成项目报告。`);
}

function exportProjectJSON() {
  const projectData = {
    name: projectName.value,
    date: new Date().toISOString(),
    objects: threeScene.value?.getSceneObjects?.().map(obj => ({
      modelType: obj.userData?.modelType,
      modelId: obj.userData?.modelId,
      position: {
        x: obj.position.x,
        y: obj.position.y,
        z: obj.position.z
      },
      rotation: {
        x: obj.rotation.x,
        y: obj.rotation.y,
        z: obj.rotation.z
      }
    })) || []
  };
  
  const jsonStr = JSON.stringify(projectData, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${projectName.value}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function generateProjectData() {
  // 从场景中统计对象
  const objects = threeScene.value?.getSceneObjects?.() || [];
  
  // 统计各类对象数量
  const stats = {};
  objects.forEach(obj => {
    // 根据对象类型或名称统计
    const type = obj.userData?.modelType || '未知类型';
    if (!stats[type]) {
      stats[type] = {
        name: modelProperties[type]?.name || type,
        model: type,
        count: 0,
        properties: modelProperties[type] || {}
      };
    }
    stats[type].count++;
  });
  
  projectReport.value = {
    name: projectName.value,
    date: new Date().toLocaleString('zh-CN'),
    totalObjects: objects.length,
    items: Object.values(stats)
  };
}

function generateReport() {
  if (!isProjectSaved.value || !projectReport.value) {
    alert('请先保存项目！');
    return;
  }
  
  // 生成Markdown报告
  let mdContent = `# ${projectReport.value.name} - 项目实施清单\n\n`;
  mdContent += `**生成时间：** ${projectReport.value.date}\n\n`;
  mdContent += `**设备总数：** ${projectReport.value.totalObjects} 件\n\n`;
  mdContent += `---\n\n`;
  mdContent += `## 设备清单\n\n`;
  
  projectReport.value.items.forEach((item, index) => {
    mdContent += `### ${index + 1}. ${item.name}\n\n`;
    mdContent += `- **型号：** ${item.model}\n`;
    mdContent += `- **数量：** ${item.count} 件\n`;
    if (item.properties.dimensions) {
      mdContent += `- **尺寸：** ${item.properties.dimensions.length}m × ${item.properties.dimensions.width}m × ${item.properties.dimensions.height}m\n`;
    }
    if (item.properties.loadCapacity) {
      mdContent += `- **承重：** ${item.properties.loadCapacity}\n`;
    }
    if (item.properties.layers) {
      mdContent += `- **层数：** ${item.properties.layers} 层\n`;
    }
    if (item.properties.material) {
      mdContent += `- **材质：** ${item.properties.material}\n`;
    }
    if (item.properties.description) {
      mdContent += `- **说明：** ${item.properties.description}\n`;
    }
    mdContent += `\n`;
  });
  
  mdContent += `---\n\n`;
  mdContent += `## 备注\n\n`;
  mdContent += `请按照以上清单进行实地布置。如有疑问，请联系项目管理员。\n\n`;
  mdContent += `---\n\n`;
  mdContent += `*本报告由仓酷家系统自动生成*\n`;
  
  // 下载Markdown文件
  const blob = new Blob([mdContent], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${projectReport.value.name}_实施清单.md`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  console.log('项目报告已下载');
}

function deleteProject() {
  alert('删除项目功能开发中...');
}

function exportImage() {
  if (threeScene.value) {
    threeScene.value.exportImage();
  }
}

function addModel(modelName) {
  if (threeScene.value) {
    threeScene.value.addModel(modelName);
  }
}

function onDragStart(event, modelName) {
  event.dataTransfer.setData('modelName', modelName);
  event.dataTransfer.effectAllowed = 'copy';
  console.log('开始拖动模型:', modelName);
}

function onModelAdded(model) {
  console.log('模型添加成功:', model);
}

function onObjectSelected(object) {
  selectedObject.value = object;
  if (threeScene.value) {
    selectedObjectCount.value = threeScene.value.getSelectedObjectsCount?.() || 1;
  }
  console.log('对象选中:', selectedObjectCount.value, '个');
}

function onObjectDeselected() {
  selectedObject.value = null;
  selectedObjectCount.value = 0;
  isRotating.value = false;
  isMoving.value = false;
  console.log('对象取消选中');
}

function moveObject() {
  if (threeScene.value) {
    threeScene.value.moveObject(true);
    isMoving.value = true;
  }
}

function startRotate() {
  if (threeScene.value) {
    threeScene.value.startRotate();
    isRotating.value = true;
  }
}

function deleteObject() {
  if (threeScene.value) {
    threeScene.value.deleteObject();
    selectedObject.value = null;
    selectedObjectCount.value = 0;
    isRotating.value = false;
    isMoving.value = false;
  }
}

function clearScene() {
  if (threeScene.value) {
    threeScene.value.clearScene();
    selectedObject.value = null;
    selectedObjectCount.value = 0;
    isRotating.value = false;
    isMoving.value = false;
  }
}

function showBatchCopyPanel() {
  showBatchPanel.value = true;
}

function previewBatchCopy() {
  if (threeScene.value && selectedObject.value) {
    if (batchCopyMode.value === 'horizontal') {
      threeScene.value.previewBatchCopyHorizontal({
        totalGroups: batchCopyTotalGroups.value,
        direction: batchCopyHDirection.value
      });
    } else {
      threeScene.value.previewBatchCopyVertical({
        columns: batchCopyColumns.value,
        groupsPerColumn: batchCopyGroupsPerColumn.value,
        columnSpacing: batchCopyColumnSpacing.value,
        direction: batchCopyVDirection.value
      });
    }
  }
}

function confirmBatchCopy() {
  if (threeScene.value && selectedObject.value) {
    if (batchCopyMode.value === 'horizontal') {
      threeScene.value.confirmBatchCopyHorizontal({
        totalGroups: batchCopyTotalGroups.value,
        direction: batchCopyHDirection.value
      });
    } else {
      threeScene.value.confirmBatchCopyVertical({
        columns: batchCopyColumns.value,
        groupsPerColumn: batchCopyGroupsPerColumn.value,
        columnSpacing: batchCopyColumnSpacing.value,
        direction: batchCopyVDirection.value
      });
    }
    showBatchPanel.value = false;
  }
}

function cancelBatchCopy() {
  if (threeScene.value) {
    threeScene.value.cancelBatchCopy();
  }
  showBatchPanel.value = false;
}
</script>

<style scoped>
.core-function {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

/* 顶部工具栏 */
.top-toolbar {
  background: #fff;
  border-bottom: 1px solid #ddd;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.group-title {
  font-size: 12px;
  font-weight: bold;
  color: #666;
  margin-right: 8px;
  text-transform: uppercase;
}

.top-toolbar button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.top-toolbar button:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.top-toolbar button:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  border-color: #ddd;
}

/* 主布局 */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 300px;
  background: #f9f9f9;
  padding: 12px;
  overflow-y: auto;
  overflow-x: visible;
  border-right: 1px solid #ddd;
  position: relative;
  z-index: 10;
}

.panel {
  background: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.panel-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.panel-icon {
  font-size: 16px;
}

/* 对象库分类 */
.model-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.category-header {
  padding: 8px 10px;
  background: #f5f5f5;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #555;
  transition: background 0.2s;
}

.category-header:hover {
  background: #eeeeee;
}

.category-icon {
  font-size: 10px;
  color: #999;
}

.category-content {
  padding: 8px;
  background: white;
}

.empty-hint {
  font-size: 12px;
  color: #999;
  text-align: center;
  padding: 12px;
  margin: 0;
}

/* 模型列表 */
.model-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.model-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s;
  border: 1px solid transparent;
  position: relative;
}

.model-item:hover {
  background: #e3f2fd;
  border-color: #4fc3f7;
}

.model-icon {
  font-size: 18px;
}

.model-name {
  font-size: 12px;
  color: #333;
}

.model-tooltip {
  position: fixed;
  left: 320px;
  top: auto;
  margin-top: -10px;
  width: 220px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 9999;
  border: 1px solid #e0e0e0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  pointer-events: none;
}

.model-item:hover .model-tooltip {
  opacity: 1;
  visibility: visible;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.tooltip-header {
  background: #4fc3f7;
  color: white;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: bold;
  border-radius: 8px 8px 0 0;
}

.tooltip-content {
  padding: 12px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
}

.tooltip-row:last-child {
  margin-bottom: 0;
}

.tooltip-label {
  color: #666;
  font-weight: 500;
}

.tooltip-value {
  color: #333;
  font-weight: 600;
}

.tooltip-description {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
  font-size: 11px;
  color: #666;
  font-style: italic;
  line-height: 1.4;
}

/* 提示框箭头 */
.model-tooltip::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 15px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 6px solid #4fc3f7;
}

/* 选择信息 */
.selection-info {
  margin-bottom: 12px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.panel-desc {
  font-size: 13px;
  color: #333;
  margin: 0 0 4px 0;
  font-weight: 500;
}

.panel-hint {
  font-size: 11px;
  color: #999;
  margin: 0;
  font-style: italic;
}

/* 操作区域 */
.operation-section {
  margin-bottom: 12px;
}

.operation-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 6px;
  font-weight: 500;
}

/* 按钮样式 */
.object-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.object-controls button {
  flex: 1;
  min-width: 70px;
  padding: 8px 10px;
  border: none;
  border-radius: 4px;
  background: #4fc3f7;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.object-controls button:hover {
  background: #29b6f6;
}

.object-controls button.active {
  background: #ff7043;
}

.btn-icon {
  font-size: 14px;
}

.delete-btn {
  background: #ef5350 !important;
}

.delete-btn:hover {
  background: #e53935 !important;
}

.warning-btn {
  background: #ffa726 !important;
}

.warning-btn:hover {
  background: #fb8c00 !important;
}

/* 控制按钮 */
.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-buttons button {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 4px;
  background: #4fc3f7;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.control-buttons button:hover {
  background: #29b6f6;
}

/* 批量复制面板 */
.batch-panel {
  border: 2px solid #4fc3f7;
}

.batch-copy-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-group label {
  font-size: 12px;
  color: #555;
  font-weight: 500;
}

.control-group input[type="range"] {
  width: 100%;
  margin: 4px 0;
}

.hint {
  font-size: 10px;
  color: #999;
  margin: 0;
}

.direction-buttons {
  display: flex;
  gap: 4px;
}

.direction-buttons button {
  flex: 1;
  padding: 6px 8px;
  font-size: 11px;
  background: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.direction-buttons button.active {
  background: #4fc3f7;
  color: white;
}

.info-text {
  font-size: 11px;
  color: #4caf50;
  font-style: italic;
  margin: 6px 0 0 0;
  padding: 8px;
  background-color: #f0f8f0;
  border-radius: 4px;
}

.batch-actions {
  display: flex;
  gap: 6px;
  margin-top: 10px;
}

.batch-actions button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.preview-btn {
  background: #ffa726 !important;
  color: white;
}

.confirm-btn {
  background: #66bb6a !important;
  color: white;
}

.cancel-btn {
  background: #ef5350 !important;
  color: white;
}

.rotate-hint {
  font-size: 11px;
  color: #ff7043;
  margin: 8px 0 0 0;
  text-align: center;
  padding: 6px;
  background: #fff3e0;
  border-radius: 4px;
}

/* 画布容器 */
.canvas-container {
  flex: 1;
  position: relative;
  background: #f0f0e6;
}

/* 模态对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-dialog {
  background: white;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: modalFadeIn 0.2s ease;
  pointer-events: auto;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-title {
  margin: 0;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #eee;
}

.modal-content {
  padding: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
  pointer-events: auto;
  background: white;
  color: #333;
}

.form-group input:focus {
  outline: none;
  border-color: #4fc3f7;
}

.modal-actions {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
  justify-content: flex-end;
}

.modal-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}
</style>
