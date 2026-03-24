<template>
  <div class="core-function">
    <!-- 顶部项目栏 -->
    <div class="top-project-bar">
      <!-- 左侧：项目操作按钮 -->
      <div class="top-bar-left">
        <button @click="goToUsage" class="top-bar-btn home-btn" title="返回首页">
          <span class="btn-icon">🏠</span>首页
        </button>
        <button @click="importProject" class="top-bar-btn" title="导入项目">
          <span class="btn-icon">📂</span>导入
        </button>
        <button @click="saveProject" class="top-bar-btn" title="保存项目">
          <span class="btn-icon">💾</span>保存
        </button>
        <button @click="exportImage" :disabled="currentView !== '3d'" class="top-bar-btn" title="导出3D效果图">
          <span class="btn-icon">📷</span>效果图
        </button>
        <button @click="exportReport" :disabled="warehouseShape.length < 3" class="top-bar-btn" title="导出项目报告">
          <span class="btn-icon">📄</span>报告
        </button>
        <button @click="closeProject" class="top-bar-btn close-btn" title="关闭项目">
          <span class="btn-icon">❌</span>关闭
        </button>
      </div>
      
      <!-- 中间：项目名称 -->
      <div class="top-bar-center">
        <span class="project-name">{{ projectName || '未命名项目' }}</span>
      </div>
      
      <!-- 右侧：工具按钮 -->
      <div class="top-bar-right">
        <!-- 面板折叠/展开按钮（简化显示） -->
        <button @click="toggleLeftPanel" class="top-bar-btn icon-btn" :title="isLeftPanelExpanded ? '隐藏左侧面板' : '显示左侧面板'">
          <span class="btn-icon">{{ isLeftPanelExpanded ? '◀' : '▶' }}</span>
        </button>
        <button @click="toggleRightPanel" class="top-bar-btn icon-btn" :title="isRightPanelExpanded ? '隐藏右侧面板' : '显示右侧面板'">
          <span class="btn-icon">{{ isRightPanelExpanded ? '▶' : '◀' }}</span>
        </button>
        <div class="top-bar-divider"></div>
        <!-- 选择模式按钮 -->
        <button @click="setSelectMode" :class="{ active: !isAddingText && !isMeasuring && !isAlignLineMode }" class="top-bar-btn" title="选择模式">
          <span class="btn-icon">🖱️</span>选择
        </button>
        <!-- 测量工具按钮（占位） -->
        <button @click="startMeasure" :class="{ active: isMeasuring }" class="top-bar-btn" title="测量工具">
          <span class="btn-icon">📏</span>测量
        </button>
        <!-- 对齐线按钮（占位） -->
        <button @click="addAlignLine" :class="{ active: isAlignLineMode }" class="top-bar-btn" title="添加对齐线">
          <span class="btn-icon">➕</span>对齐线
        </button>
        <!-- 自定义货架按钮 -->
        <button @click="openCustomShelf" class="top-bar-btn" title="创建自定义货架">
          <span class="btn-icon">➕📦</span>
        </button>
        <!-- 对齐工具按钮（MVP禁用） -->
        <button class="top-bar-btn disabled-btn" disabled title="对齐工具（待多选功能上线后启用）">
          <span class="btn-icon">📐</span>对齐工具▼
        </button>
      </div>
    </div>
    
    <div class="main-layout">
      <!-- 左侧导航面板 -->
      <div class="left-panel" :class="{ 'panel-collapsed': !isLeftPanelExpanded }">
        <!-- 流程导航 -->
        <div class="panel process-panel">
          <h3 class="panel-title">
            <span class="panel-icon">📋</span>
            设计流程
          </h3>
          
          <!-- 卡片式步骤导航 -->
          <div class="step-cards">
            <!-- 卡片1: 创建平面仓库 -->
            <div 
              class="step-card" 
              :class="{ active: currentStep === 'create-warehouse', completed: completedSteps.includes('create-warehouse') }"
              @click="toggleStepMenu('create-warehouse')"
            >
              <div class="step-card-icon">📐</div>
              <div class="step-card-title">创建平面仓库</div>
            </div>
            
            <!-- 卡片2: 放置3D对象 -->
            <div 
              class="step-card" 
              :class="{ active: currentStep === 'add-objects', completed: completedSteps.includes('add-objects') }"
              @click="toggleStepMenu('add-objects')"
            >
              <div class="step-card-icon">📦</div>
              <div class="step-card-title">放置3D对象</div>
            </div>
            
            <!-- 卡片3: 对齐线 -->
            <div 
              class="step-card" 
              :class="{ active: currentStep === 'align-lines', completed: completedSteps.includes('align-lines') }"
              @click="toggleStepMenu('align-lines')"
            >
              <div class="step-card-icon">📏</div>
              <div class="step-card-title">对齐线</div>
            </div>
          </div>
          
          <!-- 展开的菜单内容 -->
          <div class="process-steps">
            <!-- 步骤1: 创建平面仓库 -->
            <div class="process-step-wrapper" v-show="expandedStep === 'create-warehouse'">
              <!-- 2级菜单 -->
              <div v-if="expandedStep === 'create-warehouse'" class="sub-menu">
                
                <!-- 下拉菜单1: 绘制平面仓库 -->
                <div class="dropdown-menu">
                  <div class="dropdown-header" @click="toggleDropdown('draw-warehouse')">
                    <span class="dropdown-title">📏 绘制平面仓库</span>
                    <span class="dropdown-icon" :class="{ expanded: expandedDropdowns['draw-warehouse'] }">▼</span>
                  </div>
                  <div v-show="expandedDropdowns['draw-warehouse']" class="dropdown-content">
                    <!-- 仓库参数设置 -->
                    <div class="sub-menu-section">
                      <p class="sub-menu-section-title">仓库参数</p>
                      <div class="sub-menu-config-row">
                        <div class="sub-menu-config-compact">
                          <label>层高(m):</label>
                          <input type="number" v-model.number="warehouseConfig.height" min="1" step="0.1">
                        </div>
                        <div class="sub-menu-config-compact">
                          <label>水平(m):</label>
                          <input type="number" v-model.number="warehouseConfig.baseHeight" step="0.1">
                        </div>
                      </div>
                    </div>
                    
                    <!-- 快捷生成和开始绘制 -->
                    <div class="sub-menu-section">
                      <div class="sub-menu-divider"></div>
                      <div class="sub-menu-row">
                        <button @click="showQuickRectDialog" class="btn-primary">
                          <span class="btn-icon">📐</span>
                          快捷生成
                        </button>
                        <button @click="start2DDrawing" :class="{ active: is2DDrawing }" class="btn-primary">
                          <span class="btn-icon">✏️</span>
                          {{ is2DDrawing ? '绘制中...' : '开始绘制' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 下拉菜单2: 规划功能区 -->
                <div class="dropdown-menu">
                  <div class="dropdown-header" @click="toggleDropdown('plan-zones')">
                    <span class="dropdown-title">📐 规划功能区</span>
                    <span class="dropdown-icon" :class="{ expanded: expandedDropdowns['plan-zones'] }">▼</span>
                  </div>
                  <div v-show="expandedDropdowns['plan-zones']" class="dropdown-content">
                    <!-- 功能区类型平铺显示 -->
                    <div class="sub-menu-section">
                      <div class="zone-type-grid-compact">
                        <div 
                          v-for="type in zoneTypes" 
                          :key="type.value"
                          class="zone-type-item draggable"
                          draggable="true"
                          @dragstart="onZoneDragStart($event, type)"
                          :style="{ backgroundColor: type.color + '20', border: `2px solid ${type.color}` }"
                        >
                          <span class="zone-label">{{ type.label }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 文字标注 -->
                    <div class="sub-menu-section">
                      <div class="sub-menu-divider"></div>
                      <div class="sub-menu-row">
                        <button @click="startAddText" :class="{ active: isAddingText }" class="btn-primary" style="flex: 1;">
                          <span class="btn-icon">📝</span>
                          {{ isAddingText ? '点击画布添加' : '添加文字标注' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
              </div>
            </div>
            
            <!-- 步骤2: 放置3D对象 -->
            <div class="process-step-wrapper" v-show="expandedStep === 'add-objects'">
              <!-- 2级菜单 -->
              <div v-if="expandedStep === 'add-objects'" class="sub-menu">
                
                <!-- 大类菜单单列布局 -->
                <div class="object-category-list">
                  <!-- 第一行：仓库附属设施 + 货架系统 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('facility')">
                      <span>️ 仓库设施</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.facility }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.facility" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDoorDragStart($event)" :class="{ disabled: currentView !== '3d' }">🚪 门 (2.0×2.2m)</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onLiftDoorDragStart($event)" :class="{ disabled: currentView !== '3d' }">🚛 提升门 (3.5×4.2m)</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onLiftDoor27DragStart($event)" :class="{ disabled: currentView !== '3d' }">🚛 提升门 (2.7×3.0m)</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onWindowDragStart($event)" :class="{ disabled: currentView !== '3d' }">🪟 窗 (1.5×1.2m)</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onPillarDragStart($event)" :class="{ disabled: currentView !== '3d' }">🏛️ 立柱 (40×30cm)</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 我的模型 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('my-models')">
                      <span>👤 我的模型({{ myModels.length }})</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories['my-models'] }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories['my-models']" class="category-items-compact">
                      <div v-for="model in myModels" :key="model.id" class="sub-menu-row-compact my-model-item">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onCustomModelDragStart($event, model)" :class="{ disabled: currentView !== '3d' }" :title="model.name">{{ model.shortId || model.id }} {{ model.name }}</div>
                        <button class="delete-my-model-btn" @click="deleteMyModel(model.id)" title="删除此模型">🗑️</button>
                      </div>
                      <div v-if="myModels.length === 0" class="sub-menu-row-compact">
                        <div class="draggable-item-compact disabled">暂无自定义模型，请在P2页创建</div>
                      </div>
                    </div>
                  </div>

                  <!-- 轻型货架 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('light-shelf')">
                      <span>📦 轻型货架(10)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories['light-shelf'] }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories['light-shelf']" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A15-4')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A15-4')">{{ getModelFullName('A15-4') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A15-5')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A15-5')">{{ getModelFullName('A15-5') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A20-4')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A20-4')">{{ getModelFullName('A20-4') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A20-5')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A20-5')">{{ getModelFullName('A20-5') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A20-6')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A20-6')">{{ getModelFullName('A20-6') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A15-4-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A15-4-pair')">{{ getModelFullName('A15-4-pair') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A15-5-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A15-5-pair')">{{ getModelFullName('A15-5-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A20-4-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A20-4-pair')">{{ getModelFullName('A20-4-pair') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A20-5-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A20-5-pair')">{{ getModelFullName('A20-5-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'A20-6-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('A20-6-pair')">{{ getModelFullName('A20-6-pair') }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 中型货架 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('medium-shelf')">
                      <span>📦 中型货架(6)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories['medium-shelf'] }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories['medium-shelf']" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'B20-4')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('B20-4')">{{ getModelFullName('B20-4') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'B20-5')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('B20-5')">{{ getModelFullName('B20-5') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'B20-6')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('B20-6')">{{ getModelFullName('B20-6') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'B20-4-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('B20-4-pair')">{{ getModelFullName('B20-4-pair') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'B20-5-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('B20-5-pair')">{{ getModelFullName('B20-5-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'B20-6-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('B20-6-pair')">{{ getModelFullName('B20-6-pair') }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 高位货架 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('heavy-shelf')">
                      <span>📦 高位货架(24)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories['heavy-shelf'] }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories['heavy-shelf']" class="category-items-compact">
                      <!-- C23系列 -->
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-3')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-3')">{{ getModelFullName('C23-3') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-4')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-4')">{{ getModelFullName('C23-4') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-5')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-5')">{{ getModelFullName('C23-5') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-6')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-6')">{{ getModelFullName('C23-6') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-3-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-3-pair')">{{ getModelFullName('C23-3-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-4-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-4-pair')">{{ getModelFullName('C23-4-pair') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-5-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-5-pair')">{{ getModelFullName('C23-5-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C23-6-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C23-6-pair')">{{ getModelFullName('C23-6-pair') }}</div>
                      </div>
                      <!-- C25系列 -->
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-3')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-3')">{{ getModelFullName('C25-3') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-4')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-4')">{{ getModelFullName('C25-4') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-5')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-5')">{{ getModelFullName('C25-5') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-6')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-6')">{{ getModelFullName('C25-6') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-3-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-3-pair')">{{ getModelFullName('C25-3-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-4-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-4-pair')">{{ getModelFullName('C25-4-pair') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-5-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-5-pair')">{{ getModelFullName('C25-5-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C25-6-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C25-6-pair')">{{ getModelFullName('C25-6-pair') }}</div>
                      </div>
                      <!-- C27系列 -->
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-3')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-3')">{{ getModelFullName('C27-3') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-4')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-4')">{{ getModelFullName('C27-4') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-5')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-5')">{{ getModelFullName('C27-5') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-6')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-6')">{{ getModelFullName('C27-6') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-3-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-3-pair')">{{ getModelFullName('C27-3-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-4-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-4-pair')">{{ getModelFullName('C27-4-pair') }}</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-5-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-5-pair')">{{ getModelFullName('C27-5-pair') }}</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'C27-6-pair')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('C27-6-pair')">{{ getModelFullName('C27-6-pair') }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 其他货架 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('other-shelf')">
                      <span>📦 其他货架(2)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories['other-shelf'] }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories['other-shelf']" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'shelf-drive-in')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('shelf-drive-in')">A103 驶入式货架-重型</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'shelf-flow-4level')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('shelf-flow-4level')">A104 流利式货架-4层拣选</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 第二行：载具容器 + 搬运设备 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('containers')">
                      <span>📋 载具容器(8)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.containers }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.containers" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'pallet-wooden-1200')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('pallet-wooden-1200')">C101 木质托盘 1200×1000</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'pallet-plastic-1200')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('pallet-plastic-1200')">C102 塑料托盘 1200×1000</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'pallet-wood-1200x1000')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('pallet-wood-1200x1000')">C103 木质托盘-标准双向</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'pallet-plastic-1200x1000')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('pallet-plastic-1200x1000')">C104 塑料托盘-网格双面</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'container-foldable')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('container-foldable')">C105 可折叠周转箱</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'container-tote-600x400x300')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('container-tote-600x400x300')">C106 可堆叠周转箱-600×400×300</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'container-tote-600x400x220')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('container-tote-600x400x220')">C107 可堆叠周转箱-600×400×220</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'container-tote-400x300x150')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('container-tote-400x300x150')">C108 可堆叠周转箱-400×300×150</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('handling')">
                      <span>🚛 搬运设备(6)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.handling }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.handling" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'forklift-reach-2t')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('forklift-reach-2t')">B101 前移式叉车-2吨9米</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'forklift-counterbalance-2.5t')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('forklift-counterbalance-2.5t')">B102 平衡重叉车-2.5吨4米</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'forklift-pallet-truck-electric')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('forklift-pallet-truck-electric')">B103 电动搬运车-2吨步行式</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'forklift-pallet-jack-manual')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('forklift-pallet-jack-manual')">B104 手动液压搬运车-2.5吨</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'cart-picking-3tier')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('cart-picking-3tier')">B105 三层拣货车-标准型</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'cart-cage-logistics-2tier')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('cart-cage-logistics-2tier')">B106 物流笼车-2层标准款</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 第三行：输送设备 + 拣选设备 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('conveying')">
                      <span>➡️ 输送设备(3)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.conveying }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.conveying" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'lift-cargo-hydraulic-3floor')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('lift-cargo-hydraulic-3floor')">D101 提升</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'conveyor-curve-90degree-600')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('conveyor-curve-90degree-600')">D102 转弯</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'conveyor-roller-straight-600-red')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('conveyor-roller-straight-600-red')">D103 滚筒</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('picking')">
                      <span>🔲 拣选设备(3)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.picking }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.picking" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'putwall-standard-16cell')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('putwall-standard-16cell')">E101 播种</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'station-packcheck-integrated-red')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('station-packcheck-integrated-red')">E102 打包</div>
                      </div>
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'weigher-automatic-check-600-red')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('weigher-automatic-check-600-red')">E103 称重</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 第四行：分拣设备 + 其他设备 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('sorting')">
                      <span>📦 分拣设备(2)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.sorting }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.sorting" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'sorter-dws-straight-600')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('sorter-dws-straight-600')">H101 DWS</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'sorter-wheel-diverter-600')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('sorter-wheel-diverter-600')">H102 摆轮</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('others')">
                      <span>🚧 其他设备(2)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.others }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.others" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'guard-rack-heavy-redyellow')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('guard-rack-heavy-redyellow')">F101 护栏</div>
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'guard-column-protector-redyellow')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('guard-column-protector-redyellow')">F102 护角</div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 第五行：人员 -->
                  <div class="object-category-compact">
                    <div class="category-title-compact" @click="toggleObjectCategory('personnel')">
                      <span>👷 人员(1)</span>
                      <span class="toggle-icon" :class="{ expanded: expandedObjectCategories.personnel }">▼</span>
                    </div>
                    <div v-show="expandedObjectCategories.personnel" class="category-items-compact">
                      <div class="sub-menu-row-compact">
                        <div class="draggable-item-compact" draggable="true" @dragstart="onDragStart($event, 'person-warehouse-admin-red')" :class="{ disabled: currentView !== '3d' }" :title="getModelFullName('person-warehouse-admin-red')">G101 管理员</div>
                      </div>
                    </div>
                  </div>
                </div>
                
              </div>
            </div>
            
            <!-- 步骤3: 对齐线 -->
            <div class="process-step-wrapper" v-show="expandedStep === 'align-lines'">
              <div v-if="expandedStep === 'align-lines'" class="sub-menu">
                <div class="sub-menu-section">
                  <p class="sub-menu-section-title">对齐线列表</p>
                  <div class="align-line-list">
                    <div v-if="alignLines.length === 0" class="empty-hint">
                      暂无对齐线
                    </div>
                    <div v-for="(line, index) in alignLines" 
                         :key="line.id" 
                         class="align-line-item"
                         :class="{ active: selectedAlignmentLineId === line.id }"
                         @click="selectAlignLine(line.id)">
                      <span class="line-name">{{ line.name }}</span>
                      <button @click.stop="deleteAlignLine(index)" class="delete-btn" title="删除">🗑️</button>
                    </div>
                  </div>
                </div>
                <div class="sub-menu-section">
                  <div class="sub-menu-divider"></div>
                  <button @click="clearAllAlignLines" class="btn-primary warning-btn" style="width: 100%;">
                    <span class="btn-icon">🗑️</span>清空全部
                  </button>
                </div>
              </div>
            </div>
            
          </div>
        </div>
        
      </div>
      
      <!-- 主工作台区域 -->
      <div class="canvas-container">
        <!-- 2D画布 -->
        <div v-show="currentView === '2d'" class="canvas-2d">
          <div 
            class="canvas-2d-area" 
            ref="canvas2D"
            @click="onCanvasClick"
            @mousemove="onCanvasMouseMove"
            @mousedown="onCanvasMouseDown"
            @mouseup="onCanvasMouseUp"
            @wheel="onCanvasWheel"
            @drop="onZoneDrop"
            @dragover="onZoneDragOver"
            :class="{ 'create-mode': isZoneCreateMode, 'edit-mode': isZoneEditMode, 'panning': isPanning }"
          >
            <!-- 坐标标尺 - 左下角，X向右，Y向上 -->
            <div class="canvas-ruler">
              <svg class="ruler-svg" viewBox="0 0 220 220">
                <!-- X轴 (水平向右) -->
                <line x1="20" y1="200" x2="200" y2="200" stroke="#666" stroke-width="1"/>
                <!-- Y轴 (垂直向上) -->
                <line x1="20" y1="200" x2="20" y2="20" stroke="#666" stroke-width="1"/>
                <!-- X轴刻度 (向右) -->
                <g v-for="i in 9" :key="'x'+i">
                  <line :x1="20 + i * 20" y1="200" :x2="20 + i * 20" y2="195" stroke="#666" stroke-width="1"/>
                  <text :x="20 + i * 20" y="215" font-size="8" fill="#666" text-anchor="middle">{{ i * 10 }}</text>
                </g>
                <!-- Y轴刻度 (向上) -->
                <g v-for="i in 9" :key="'y'+i">
                  <line x1="15" :y1="200 - i * 20" x2="20" :y2="200 - i * 20" stroke="#666" stroke-width="1"/>
                  <text x="10" :y="200 - i * 20 + 3" font-size="8" fill="#666" text-anchor="end">{{ i * 10 }}</text>
                </g>
                <!-- 原点 -->
                <circle cx="20" cy="200" r="3" fill="#ff7043"/>
                <text x="5" y="215" font-size="9" fill="#ff7043" font-weight="bold">0</text>
              </svg>
            </div>
            <!-- 鼠标坐标显示 -->
            <div class="mouse-coords">
              X: {{ mouseCanvasPos.x }}px, Y: {{ mouseCanvasPos.y }}px
            </div>
            <!-- 缩放控制 -->
            <div class="zoom-controls">
              <button @click="canvasScale *= 1.2" title="放大">+</button>
              <button @click="resetCanvasView" title="重置">⟲</button>
              <button @click="canvasScale *= 0.8" title="缩小">-</button>
              <span class="zoom-level">{{ Math.round(canvasScale * 100) }}%</span>
            </div>
            <div class="canvas-grid" :style="canvasTransformStyle">
              <!-- 绘制的仓库轮廓 -->
              <svg class="drawing-svg">
                <!-- 已完成的线段 -->
                <line 
                  v-for="(line, index) in getWarehouseLines" 
                  :key="'line-'+index"
                  :x1="line.x1" 
                  :y1="line.y1" 
                  :x2="line.x2" 
                  :y2="line.y2"
                  :stroke="selectedLineIndex === index || editingLineIndex === index ? '#ff7043' : '#4361ee'"
                  :stroke-width="selectedLineIndex === index || editingLineIndex === index ? 3 : 2"
                  class="editable-line"
                  @click.stop="handleLineClick(index)"
                  style="cursor: pointer;"
                />
                <!-- 绘制点 -->
                <circle 
                  v-for="(point, index) in warehouseShape" 
                  :key="'point-'+index"
                  :cx="point.x" 
                  :cy="point.y" 
                  r="5" 
                  fill="#4361ee"
                  stroke="white"
                  stroke-width="2"
                />
                <!-- 虚线预览 -->
                <line 
                  v-if="isPreviewing && previewLine"
                  :x1="previewLine.x1" 
                  :y1="previewLine.y1" 
                  :x2="previewLine.x2" 
                  :y2="previewLine.y2"
                  :stroke="previewLine.isAxisAligned ? '#4361ee' : '#ff7043'"
                  stroke-width="2"
                  stroke-dasharray="8,4"
                  opacity="0.6"
                />
                <!-- 预览点 -->
                <circle 
                  v-if="isPreviewing && previewPoint"
                  :cx="previewPoint.x" 
                  :cy="previewPoint.y" 
                  r="4" 
                  fill="#4361ee"
                  opacity="0.6"
                />
                <!-- 编辑中的线段高亮 -->
                <line 
                  v-if="editingLineIndex !== null && getWarehouseLines[editingLineIndex]"
                  :x1="getWarehouseLines[editingLineIndex].x1" 
                  :y1="getWarehouseLines[editingLineIndex].y1" 
                  :x2="getWarehouseLines[editingLineIndex].x2" 
                  :y2="getWarehouseLines[editingLineIndex].y2"
                  stroke="#ff7043" 
                  stroke-width="3"
                />
                <!-- 长度标注 -->
                <text 
                  v-if="isPreviewing && previewLine && currentSegmentLength"
                  :x="(previewLine.x1 + previewLine.x2) / 2"
                  :y="(previewLine.y1 + previewLine.y2) / 2 - 10"
                  text-anchor="middle"
                  fill="#4361ee"
                  font-size="12"
                  font-weight="bold"
                  class="length-label"
                >
                  {{ currentSegmentLength }}m
                </text>
              </svg>
              <!-- 功能区 -->
              <svg class="zones-svg" @mousemove="onZoneMouseMove" @mouseup="onZoneMouseUp" @mouseleave="onZoneMouseUp">
                <g v-for="zone in zones" :key="zone.id">
                  <!-- 使用矩形渲染 -->
                  <rect
                    v-if="zone.x !== undefined"
                    :x="zone.x"
                    :y="zone.y"
                    :width="zone.width"
                    :height="zone.height"
                    :fill="zone.color + '33'"
                    :stroke="selectedZone === zone.id ? '#ff7043' : zone.color"
                    :stroke-width="selectedZone === zone.id ? 3 : 2"
                    class="zone-rect"
                    @click.stop="onZoneClick(zone.id)"
                    @dblclick.stop="onZoneDoubleClick(zone.id)"
                    @mousedown.stop="onZoneMoveStart($event, zone.id)"
                  />
                  <!-- 使用多边形渲染（兼容旧数据） -->
                  <polygon
                    v-else
                    :points="getZonePoints(zone)"
                    :fill="zone.color + '33'"
                    :stroke="selectedZone === zone.id ? '#ff7043' : zone.color"
                    :stroke-width="selectedZone === zone.id ? 3 : 2"
                    @click.stop="onZoneClick(zone.id)"
                    @dblclick.stop="onZoneDoubleClick(zone.id)"
                  />
                  <!-- 功能区名称 - 中间偏下位置 -->
                  <text
                    :x="zone.x !== undefined ? zone.x + zone.width / 2 : getZoneCenter(zone).x"
                    :y="zone.y !== undefined ? zone.y + zone.height / 2 + 15 : getZoneCenter(zone).y + 15"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    fill="#333"
                    font-size="12"
                    font-weight="bold"
                    class="zone-label"
                    @click.stop="onZoneClick(zone.id)"
                    @dblclick.stop="onZoneDoubleClick(zone.id)"
                    @mousedown.stop="onZoneMoveStart($event, zone.id)"
                  >
                    {{ zone.name }}
                  </text>
                  <!-- 功能区面积显示（右上角） -->
                  <text
                    v-if="zone.x !== undefined"
                    :x="zone.x + zone.width - 5"
                    :y="zone.y + 15"
                    text-anchor="end"
                    dominant-baseline="middle"
                    fill="#666"
                    font-size="10"
                    class="zone-area"
                  >
                    {{ getZoneDimensions(zone) }}
                  </text>
                  <!-- 调整手柄（仅在编辑模式且选中时显示） -->
                  <g v-if="isZoneEditMode && selectedZone === zone.id && zone.x !== undefined">
                    <!-- 四角手柄 -->
                    <rect :x="zone.x - 4" :y="zone.y - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'nw', zone.id)"/>
                    <rect :x="zone.x + zone.width - 4" :y="zone.y - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'ne', zone.id)"/>
                    <rect :x="zone.x - 4" :y="zone.y + zone.height - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'sw', zone.id)"/>
                    <rect :x="zone.x + zone.width - 4" :y="zone.y + zone.height - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'se', zone.id)"/>
                    <!-- 四边中点手柄 -->
                    <rect :x="zone.x + zone.width / 2 - 4" :y="zone.y - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'n', zone.id)"/>
                    <rect :x="zone.x + zone.width / 2 - 4" :y="zone.y + zone.height - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 's', zone.id)"/>
                    <rect :x="zone.x - 4" :y="zone.y + zone.height / 2 - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'w', zone.id)"/>
                    <rect :x="zone.x + zone.width - 4" :y="zone.y + zone.height / 2 - 4" width="8" height="8" fill="#ff7043" class="resize-handle" @mousedown.stop="onZoneResizeStart($event, 'e', zone.id)"/>
                  </g>
                </g>
                <!-- 文字标注 -->
                <g v-for="label in textLabels" :key="label.id">
                  <text
                    :x="label.x"
                    :y="label.y"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    :fill="selectedTextLabel === label.id ? '#ff5722' : label.color"
                    :font-size="label.fontSize"
                    :class="{ 'text-label': true, 'selected': selectedTextLabel === label.id }"
                    @mousedown.stop="onTextLabelMouseDown($event, label.id)"
                    @dblclick.stop="editTextLabel(label.id)"
                    style="cursor: move; user-select: none;"
                  >
                    {{ label.content }}
                  </text>
                  <!-- 选中时的背景框 -->
                  <rect
                    v-if="selectedTextLabel === label.id"
                    :x="label.x - (label.content.length * label.fontSize * 0.3) - 4"
                    :y="label.y - label.fontSize / 2 - 4"
                    :width="label.content.length * label.fontSize * 0.6 + 8"
                    :height="label.fontSize + 8"
                    fill="none"
                    stroke="#ff5722"
                    stroke-width="2"
                    stroke-dasharray="4,2"
                  />
                </g>
              </svg>
            </div>
            <!-- 绘制提示 -->
            <div v-if="is2DDrawing" class="drawing-status">
              <span v-if="!isWaitingForLength && !isPreviewing">点击画布确定起点</span>
              <span v-if="isWaitingForLength">输入线段长度</span>
              <span v-if="isPreviewing">移动鼠标确定方向，点击确定落点</span>
            </div>
          </div>
          <div class="canvas-2d-info">
            <span>绘制点数: {{ warehouseShape.length }}</span>
            <span>功能区数: {{ zones.length }}</span>
            <span v-if="is2DDrawing" class="drawing-hint">按ESC取消当前线段</span>
          </div>
        </div>
        
        <!-- 3D画布 -->
        <div v-show="currentView === '3d'" class="canvas-3d">
          <!-- 3D生成加载遮罩 -->
          <div v-if="isGenerating3D" class="loading-overlay">
            <div class="loading-spinner"></div>
            <p class="loading-text">正在生成3D场景...</p>
          </div>
          <!-- 3D视图控制工具栏 -->
          <div class="canvas-3d-controls">
            <button @click="zoom3DIn" title="放大">+</button>
            <button @click="reset3DView" title="重置视图">⟲</button>
            <button @click="zoom3DOut" title="缩小">-</button>
            <button @click="refresh3DView" title="刷新3D视图">🔄</button>
          </div>
          <ThreeScene
            ref="threeScene"
            :adding-door="isAddingDoor"
            :adding-window="isAddingWindow"
            :model-name-map="modelFullNames"
            :warehouse-config="warehouseConfig"
            @model-added="onModelAdded"
            @object-selected="onObjectSelected"
            @object-deselected="onObjectDeselected"
            @zone-selected="onZoneSelectedIn3D"
            @save-project="saveProject"
            @add-door="onAddDoor"
            @add-window="onAddWindow"
            @alignment-lines-updated="handleAlignmentLinesUpdated"
          />
        </div>
      </div>
      
      <!-- 右侧属性面板 -->
      <div class="right-panel" :class="{ 'panel-collapsed': !isRightPanelExpanded }">
        <!-- 属性面板 -->
        <div class="panel property-panel">
          <h3 class="panel-title">
            <span class="panel-icon">📊</span>
            {{ selectedObject ? '对象属性' : (selectedZone !== null ? '功能区属性' : (selectedTextLabel !== null ? '文字标注属性' : '仓库属性')) }}
          </h3>

          <!-- 仓库属性（未选中对象、功能区和文字标注时） -->
          <div v-if="!selectedObject && selectedZone === null && selectedTextLabel === null" class="property-content">
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">长:</span>
                <span class="property-value">{{ warehouseDimensions.length }}m</span>
              </div>
              <div class="property-item">
                <span class="property-label">宽:</span>
                <span class="property-value">{{ warehouseDimensions.width }}m</span>
              </div>
              <div class="property-item">
                <span class="property-label">高:</span>
                <span class="property-value">{{ warehouseDimensions.height }}m</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">面积:</span>
                <span class="property-value">{{ calculateWarehouseArea() }}㎡</span>
              </div>
              <div class="property-item">
                <span class="property-label">层高:</span>
                <span class="property-value">{{ warehouseConfig.height }}m</span>
              </div>
              <div class="property-item">
                <span class="property-label">水平高度:</span>
                <span class="property-value">{{ warehouseConfig.baseHeight }}m</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">功能区:</span>
                <span class="property-value">{{ zones.length }}个</span>
              </div>
              <div class="property-item">
                <span class="property-label">放置对象:</span>
                <span class="property-value">{{ placedObjectsCount }}个</span>
              </div>
            </div>
          </div>
          
          <!-- 2D功能区属性（选中功能区时） -->
          <div v-else-if="selectedZone !== null" class="property-content">
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">名称:</span>
                <span class="property-value">{{ getSelectedZoneName() }}</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">面积:</span>
                <span class="property-value">{{ getSelectedZoneArea() }}</span>
              </div>
            </div>
          </div>
          
          <!-- 3D对象属性（选中对象时） -->
          <div v-else-if="selectedObject" class="property-content">
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">名称:</span>
                <span class="property-value">{{ selectedObject.name || (selectedObject.type === 'wall' ? '墙体' : selectedObject.type) }}</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">尺寸:</span>
                <span class="property-value">{{ selectedObject.dimensions || '计算中...' }}</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">位置 X:</span>
                <span class="property-value">{{ formatPosition(selectedObject.position?.x) }}m</span>
              </div>
              <div class="property-item">
                <span class="property-label">位置 Y:</span>
                <span class="property-value">{{ formatPosition(selectedObject.position?.y) }}m</span>
              </div>
              <div class="property-item">
                <span class="property-label">位置 Z:</span>
                <span class="property-value">{{ formatPosition(selectedObject.position?.z) }}m</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">旋转:</span>
                <span class="property-value">{{ formatRotation(selectedObject.rotation) }}°</span>
              </div>
            </div>
          </div>
          
          <!-- 文字标注属性（选中文字标注时） -->
          <div v-else-if="selectedTextLabel !== null" class="property-content">
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">内容:</span>
                <span class="property-value">{{ getSelectedTextLabelContent() }}</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">字体大小:</span>
                <span class="property-value">{{ getSelectedTextLabelFontSize() }}px</span>
              </div>
            </div>
            <div class="property-divider"></div>
            <div class="property-group">
              <div class="property-item">
                <span class="property-label">位置 X:</span>
                <span class="property-value">{{ getSelectedTextLabelX() }}px</span>
              </div>
              <div class="property-item">
                <span class="property-label">位置 Y:</span>
                <span class="property-value">{{ getSelectedTextLabelY() }}px</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 2D对象操作面板 -->
        <div class="panel operation-panel" v-if="currentView === '2d' && (selectedLineIndex !== null || selectedZone !== null || selectedTextLabel !== null)">
          <h3 class="panel-title">
            <span class="panel-icon">🛠️</span>
            对象操作
          </h3>
          <div class="operation-content">
            <!-- 线条操作 -->
            <div v-if="selectedLineIndex !== null" class="operation-section">
              <h4 class="operation-subtitle">线条操作</h4>
              <div class="operation-row">
                <button @click="editSelectedLine" class="operation-btn">
                  <span class="btn-icon">✏️</span>编辑线条
                </button>
                <button @click="deleteSelectedLine" class="operation-btn warning-btn">
                  <span class="btn-icon">🗑️</span>删除线条
                </button>
              </div>
            </div>
            
            <!-- 功能区操作 -->
            <div v-if="selectedZone !== null" class="operation-section">
              <h4 class="operation-subtitle">功能区操作</h4>
              <div class="operation-row">
                <button @click="editSelectedZone" class="operation-btn">
                  <span class="btn-icon">✏️</span>编辑功能区
                </button>
                <button @click="deleteSelectedZone" class="operation-btn warning-btn">
                  <span class="btn-icon">🗑️</span>删除功能区
                </button>
              </div>
            </div>
            
            <!-- 文字标注操作 -->
            <div v-if="selectedTextLabel !== null" class="operation-section">
              <h4 class="operation-subtitle">文字标注操作</h4>
              <div class="operation-row">
                <button @click="editSelectedTextLabel" class="operation-btn">
                  <span class="btn-icon">✏️</span>编辑文字
                </button>
                <button @click="deleteSelectedTextLabel" class="operation-btn warning-btn">
                  <span class="btn-icon">🗑️</span>删除文字
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 3D对象操作面板（选中墙体或地面时不显示） -->
        <div class="panel operation-panel" v-if="currentView === '3d' && selectedObject && selectedObject.type !== 'wall' && selectedObject.type !== 'floor'">
          <h3 class="panel-title">
            <span class="panel-icon">🛠️</span>
            对象操作
          </h3>
          <div class="operation-content">
            <!-- 3D对象操作 -->
            <div v-if="selectedObject" class="operation-section">
              <h4 class="operation-subtitle">对象操作</h4>
              <div class="operation-row">
                <button @click="moveSelectedObject" :disabled="!selectedObject" class="operation-btn">
                  <span class="btn-icon">↔️</span>移动
                </button>
                <button @click="toggleRotateMode" :class="{ active: isRotating }" :disabled="!selectedObject" class="operation-btn">
                  <span class="btn-icon">🔄</span>{{ isRotating ? '旋转中' : '旋转' }}
                </button>
              </div>
              <div class="operation-row">
                <button @click="deleteSelectedObject" :disabled="!selectedObject" class="operation-btn warning-btn">
                  <span class="btn-icon">🗑️</span>删除
                </button>
                <button v-if="selectedObject && selectedObject.type === 'pillar'" @click="editPillarHeight" :disabled="!selectedObject" class="operation-btn">
                  <span class="btn-icon">📏</span>编辑高度
                </button>
              </div>
            </div>

            <!-- 批量复制（仅对货架系统对象有效） -->
            <div class="operation-section" v-if="isSelectedObjectShelf">
              <div class="operation-divider"></div>
              <h4 class="operation-subtitle">批量复制</h4>
              <div class="batch-controls-compact">
                <div class="control-row">
                  <label>行:</label>
                  <input type="number" v-model.number="batchRows" min="1" max="10" :disabled="!selectedObject || isBatchPreview">
                </div>
                <div class="control-row">
                  <label>列:</label>
                  <input type="number" v-model.number="batchCols" min="1" max="10" :disabled="!selectedObject || isBatchPreview">
                </div>
                <div class="control-row">
                  <label>行距:</label>
                  <input type="number" v-model.number="batchRowSpacing" min="1" max="10" step="0.5" :disabled="!selectedObject || isBatchPreview">
                  <span>m</span>
                </div>
                <div class="control-row">
                  <label>列距:</label>
                  <input type="number" v-model.number="batchColSpacing" min="0" max="5" step="0.1" :disabled="!selectedObject || isBatchPreview">
                  <span>m</span>
                </div>
                <div class="control-row direction-row">
                  <label>行向:</label>
                  <select v-model="batchRowDirection" :disabled="!selectedObject || isBatchPreview" class="direction-select">
                    <option value="forward">向前</option>
                    <option value="backward">向后</option>
                  </select>
                </div>
                <div class="control-row direction-row">
                  <label>列向:</label>
                  <select v-model="batchColDirection" :disabled="!selectedObject || isBatchPreview" class="direction-select">
                    <option value="left">向左</option>
                    <option value="right">向右</option>
                  </select>
                </div>
              </div>
              <div class="direction-legend">
                <small>白线标记 = 前方（操作侧）</small>
              </div>
              <div class="batch-actions-compact">
                <button @click.stop="startBatchPreview" :disabled="!selectedObject || isBatchPreview" class="batch-btn preview-btn">
                  <span class="btn-icon">👁️</span>预览
                </button>
                <button @click.stop="confirmBatchPlace" :disabled="!selectedObject || !isBatchPreview" class="batch-btn confirm-btn">
                  <span class="btn-icon">✅</span>生成
                </button>
                <button @click.stop="cancelBatchPreview" :disabled="!selectedObject || !isBatchPreview" class="batch-btn cancel-btn">
                  <span class="btn-icon">❌</span>取消
                </button>
              </div>
              <p class="batch-hint-compact" v-if="isBatchPreview">ESC取消预览</p>
            </div>
            
          </div>
        </div>
      </div>
    </div>
    
    <!-- 线段长度输入对话框 -->
    <div class="modal-overlay" v-if="showLengthDialog" @click.self="cancelLengthInput">
      <div class="modal-dialog length-dialog" @mousedown="onModalDragStart($event, 'length')">
        <h3 class="modal-title">{{ isEditingLine ? '编辑线段长度' : '输入线段长度' }}</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>长度 (米)：</label>
            <input 
              type="number" 
              v-model.number="segmentLength" 
              min="0.1" 
              step="0.1"
              placeholder="请输入长度"
              ref="lengthInput"
              @keyup.enter="isEditingLine ? confirmEditLine() : confirmLengthInput()"
            >
          </div>
          <p class="hint-text">
            {{ isEditingLine ? '输入新长度后，移动鼠标确定方向，点击应用修改' : '输入长度后，移动鼠标确定方向，点击确定落点' }}
          </p>
        </div>
        <div class="modal-actions">
          <button 
            @click="isEditingLine ? confirmEditLine() : confirmLengthInput()" 
            class="confirm-btn" 
            :disabled="!segmentLength || segmentLength <= 0"
          >
            {{ isEditingLine ? '应用' : '确定' }}
          </button>
          <button @click="cancelLengthInput" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 保存项目对话框 -->
    <div class="modal-overlay" v-if="showSaveDialog" @click.self="showSaveDialog = false">
      <div class="modal-dialog" @mousedown="onModalDragStart($event, 'save')">
        <h3 class="modal-title">保存项目</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>项目名称：</label>
            <input type="text" v-model="projectName" placeholder="请输入项目名称" @keyup.enter="confirmSaveProject">
          </div>
        </div>
        <div class="modal-actions">
          <button @click="confirmSaveProject" class="confirm-btn">保存</button>
          <button @click="showSaveDialog = false" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 旋转角度输入对话框 -->
    <div class="modal-overlay" v-if="showRotationDialog" @click.self="cancelRotation">
      <div class="modal-dialog rotation-dialog" @mousedown="onModalDragStart($event, 'rotation')">
        <h3 class="modal-title">精确旋转</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>旋转角度（度）：</label>
            <input 
              type="number" 
              v-model.number="rotationAngle" 
              min="-360" 
              max="360"
              step="1"
              placeholder="请输入角度"
              @input="onRotationAngleChange"
              @keyup.enter="confirmRotation"
            >
          </div>
          <p class="hint-text">
            以白线标记方向为0°，顺时针为正方向<br>
            例如：90° = 顺时针旋转90°，-90° = 逆时针旋转90°
          </p>
          <div class="rotation-presets">
            <button @click="rotationAngle = 0; onRotationAngleChange()" class="preset-btn">0°</button>
            <button @click="rotationAngle = 90; onRotationAngleChange()" class="preset-btn">90°</button>
            <button @click="rotationAngle = 180; onRotationAngleChange()" class="preset-btn">180°</button>
            <button @click="rotationAngle = 270; onRotationAngleChange()" class="preset-btn">270°</button>
            <button @click="rotationAngle = -90; onRotationAngleChange()" class="preset-btn">-90°</button>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="confirmRotation" class="confirm-btn">确认</button>
          <button @click="cancelRotation" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 功能区尺寸编辑对话框 -->
    <div class="modal-overlay" v-if="showZoneSizeDialog" @click.self="cancelZoneSizeEdit">
      <div class="modal-dialog zone-size-dialog" @mousedown="onModalDragStart($event, 'zoneSize')">
        <h3 class="modal-title">精确编辑功能区尺寸</h3>
        <div class="modal-content">
          <div class="form-row">
            <div class="form-group">
              <label>长度（米）：</label>
              <input 
                type="number" 
                name="width"
                v-model.number="zoneEditWidth" 
                min="0.1" 
                step="0.1"
                placeholder="0"
                @keyup.enter="confirmZoneSizeEdit"
              >
            </div>
            <div class="form-group">
              <label>宽度（米）：</label>
              <input 
                type="number" 
                v-model.number="zoneEditHeight" 
                min="0.1" 
                step="0.1"
                placeholder="0"
                @keyup.enter="confirmZoneSizeEdit"
              >
            </div>
          </div>
          <p class="hint-text">
            输入长宽尺寸后，功能区将以中心点为基准调整大小
          </p>
        </div>
        <div class="modal-actions">
          <button @click="confirmZoneSizeEdit" class="confirm-btn" :disabled="zoneEditWidth <= 0 || zoneEditHeight <= 0">确认</button>
          <button @click="cancelZoneSizeEdit" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 区域列表对话框 -->
    <div class="modal-overlay" v-if="showZoneListDialog" @click.self="showZoneListDialog = false">
      <div class="modal-dialog zone-list-dialog" @mousedown="onModalDragStart($event, 'zoneList')">
        <h3 class="modal-title">功能区列表</h3>
        <div class="modal-content">
          <div v-if="zones.length === 0" class="empty-hint">
            暂无功能区
          </div>
          <div v-else class="zone-list">
            <div v-for="zone in zones" :key="zone.id" class="zone-item">
              <div class="zone-info">
                <div class="zone-color" :style="{ backgroundColor: zone.color }"></div>
                <div class="zone-details">
                  <div class="zone-name">{{ zone.name }}</div>
                  <div class="zone-type">{{ getZoneTypeLabel(zone.type) }}</div>
                </div>
              </div>
              <div class="zone-actions">
                <button @click="deleteZone(zone.id)" class="delete-btn">
                  <span class="btn-icon">🗑️</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showZoneListDialog = false" class="cancel-btn">关闭</button>
        </div>
      </div>
    </div>

    <!-- 快捷生成矩形仓库弹窗 -->
    <div v-if="showQuickRectWarehouseDialog" class="modal-overlay" @click.self="cancelQuickRectWarehouse">
      <div class="modal-dialog quick-rect-dialog" @mousedown="onModalDragStart($event, 'quickRect')">
        <h3 class="modal-title">快捷生成矩形仓库</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>仓库长度 (米):</label>
            <input type="number" class="quick-rect-input" v-model="quickRectWidth" min="10" max="500" step="1" placeholder="请输入长度" @keyup.enter="generateQuickRectWarehouse">
          </div>
          <div class="form-group">
            <label>仓库宽度 (米):</label>
            <input type="number" v-model="quickRectHeight" min="10" max="500" step="1" placeholder="请输入宽度" @keyup.enter="generateQuickRectWarehouse">
          </div>
          <div class="form-group">
            <label>仓库高度: {{ warehouseConfig.height }} 米</label>
            <span class="hint">（使用已设置的高度参数）</span>
          </div>
          <div class="form-group">
            <label>水平高度: {{ warehouseConfig.baseHeight }} 米</label>
            <span class="hint">（使用已设置的水平高度）</span>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="cancelQuickRectWarehouse" class="cancel-btn">取消</button>
          <button @click="generateQuickRectWarehouse" class="confirm-btn">生成</button>
        </div>
      </div>
    </div>

    <!-- 文字标注输入弹窗 -->
    <div v-if="showTextInputDialog" class="modal-overlay" @click.self="cancelAddText">
      <div class="modal-dialog text-input-dialog" @mousedown="onModalDragStart($event, 'textInput')">
        <h3 class="modal-title">{{ isEditingText ? '编辑文字' : '添加文字' }}</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>文字内容:</label>
            <input type="text" v-model="textInputContent" placeholder="请输入文字" @keyup.enter="isEditingText ? confirmEditText() : confirmAddText()">
          </div>
          <div class="form-group">
            <label>字体大小: {{ textInputSize }}px</label>
            <input type="range" v-model.number="textInputSize" min="10" max="48" step="1">
          </div>
        </div>
        <div class="modal-actions">
          <button @click="cancelAddText" class="cancel-btn">取消</button>
          <button @click="isEditingText ? confirmEditText() : confirmAddText()" class="confirm-btn">{{ isEditingText ? '保存' : '添加' }}</button>
        </div>
      </div>
    </div>

    <!-- 立柱高度编辑弹窗 -->
    <div v-if="showPillarHeightDialog" class="modal-overlay" @click.self="cancelPillarHeightEdit">
      <div class="modal-dialog pillar-height-dialog" @mousedown="onModalDragStart($event, 'pillarHeight')">
        <h3 class="modal-title">编辑立柱高度</h3>
        <div class="modal-content">
          <div class="form-group">
            <label>高度 (米):</label>
            <input 
              type="number" 
              v-model.number="pillarHeightInput" 
              min="3" 
              max="12" 
              step="0.1"
              placeholder="请输入高度"
              @keyup.enter="confirmPillarHeightEdit"
            >
          </div>
          <p class="hint-text">
            高度范围: 3米 - 12米
          </p>
        </div>
        <div class="modal-actions">
          <button @click="cancelPillarHeightEdit" class="cancel-btn">取消</button>
          <button @click="confirmPillarHeightEdit" class="confirm-btn" :disabled="pillarHeightInput < 3 || pillarHeightInput > 12">确认</button>
        </div>
      </div>
    </div>

    <!-- 自定义轻型货架弹窗 -->
    <div v-if="showCustomLightShelfModal" class="modal-overlay" @click.self="closeCustomLightShelfModal">
      <div class="modal-dialog custom-shelf-dialog" @mousedown="onModalDragStart($event, 'customShelf')">
        <h3 class="modal-title">自定义轻型货架</h3>
        <div class="modal-content">
          <!-- 规格选择 -->
          <div class="form-group">
            <label>选择规格:</label>
            <select v-model="selectedLightShelfSpec" class="spec-select">
              <option value="">请选择尺寸规格</option>
              <option value="A15-5">1500x400x2000（5层）- A15-5</option>
              <option value="A20-4">2000x600x2000（4层）- A20-4</option>
              <option value="A20-5">2000x600x2500（5层）- A20-5</option>
              <option value="A20-6">2000x600x3000（6层）- A20-6</option>
            </select>
          </div>
          
          <!-- 规格详情展示 -->
          <div v-if="selectedLightShelfSpec" class="spec-details">
            <div class="detail-item">
              <span class="detail-label">中文名称:</span>
              <span class="detail-value">{{ lightShelfSpecs[selectedLightShelfSpec].name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">层数:</span>
              <span class="detail-value">{{ lightShelfSpecs[selectedLightShelfSpec].levels }}层</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">承重:</span>
              <span class="detail-value">{{ lightShelfSpecs[selectedLightShelfSpec].load }}kg</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">每层空间高度:</span>
              <span class="detail-value">{{ lightShelfSpecs[selectedLightShelfSpec].layerHeight }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最佳适配仓库净高:</span>
              <span class="detail-value">{{ lightShelfSpecs[selectedLightShelfSpec].warehouseHeight }}</span>
            </div>
          </div>
          
          <!-- 空状态提示 -->
          <div v-else class="spec-empty">
            <p>请从上方下拉菜单选择一个规格</p>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="closeCustomLightShelfModal" class="cancel-btn">取消</button>
          <button @click="confirmAddCustomLightShelf" class="confirm-btn" :disabled="!selectedLightShelfSpec">确认添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import * as THREE from 'three';
import ThreeScene from '../components/3d/ThreeScene.vue';

const router = useRouter();

const threeScene = ref(null);
const selectedObject = ref(null);
const selectedObjectCount = ref(0);
const isRotating = ref(false);
const isMoving = ref(false);
const showBatchPanel = ref(false);

// 顶部工具栏工具状态
const isMeasuring = ref(false);
const isAlignLineMode = ref(false);

// 对齐线数据
const alignLines = ref([]);
const selectedAlignmentLineId = ref(null); // 当前选中的对齐线ID

// 精确旋转角度输入对话框状态
const showRotationDialog = ref(false);
const rotationAngle = ref(0);
const rotationOriginalAngle = ref(0);

// 立柱高度编辑对话框状态
const showPillarHeightDialog = ref(false);
const pillarHeightInput = ref(5);
const isRotationPreview = ref(false);
const isProjectSaved = ref(false);
const projectReport = ref(null);
const showSaveDialog = ref(false);
const projectName = ref('');

// 视图状态
const currentView = ref('2d');
const is3DGenerated = ref(false);

// 3D对象添加状态
const isAddingDoor = ref(false);
const isAddingWindow = ref(false);
const doorConfig = ref({ width: 2, height: 2.2 });
const liftDoorConfig = ref({ width: 3.5, height: 4.2 });
const liftDoor27Config = ref({ width: 2.7, height: 3.0 });
const windowConfig = ref({ width: 1.5, height: 1.2, sillHeight: 1 });

// 3D生成加载状态
const isGenerating3D = ref(false);

// 我的模型列表（从 localStorage 加载）
const myModels = ref([]);

// 从 localStorage 加载我的模型
const loadMyModels = () => {
  const saved = localStorage.getItem('myModels');
  if (saved) {
    const allModels = JSON.parse(saved);
    // 过滤掉与预设模型重复的条目（如C27-5-pair等已存在于高位货架的模型）
    const presetModelIds = Object.keys(modelFullNames);
    myModels.value = allModels.filter(model => {
      const isDuplicate = presetModelIds.includes(model.id) || presetModelIds.includes(model.shortId);
      if (isDuplicate) {
        console.log(`过滤重复的我的模型: ${model.name} (${model.id || model.shortId})`);
      }
      return !isDuplicate;
    });
    console.log('从 localStorage 加载我的模型:', myModels.value.length, '个（已过滤重复）');
  }
};

// 删除我的模型
const deleteMyModel = (modelId) => {
  const model = myModels.value.find(m => m.id === modelId || m.shortId === modelId);
  if (!model) return;

  // 确认对话框
  if (!confirm(`确定要删除模型 "${model.name}" 吗？`)) {
    return;
  }

  // 从数组中移除
  myModels.value = myModels.value.filter(m => m.id !== modelId && m.shortId !== modelId);

  // 更新 localStorage
  localStorage.setItem('myModels', JSON.stringify(myModels.value));

  console.log(`已删除模型: ${model.name}`);
};

// 对象分类展开状态
const expandedObjectCategories = ref({
  facility: true,
  'my-models': false,
  'light-shelf': false,
  'medium-shelf': false,
  'heavy-shelf': false,
  'other-shelf': false,
  containers: false,
  handling: false,
  conveying: false,
  picking: false,
  sorting: false,
  others: false,
  personnel: false
});

// 批量放置状态（旧版，保留兼容）
const batchCount = ref(3);
const batchSpacing = ref(2);
const batchDirection = ref('horizontal');
const isBatchPlacing = ref(false);

// 批量复制状态
const batchRows = ref(2);
const batchCols = ref(3);
const batchRowSpacing = ref(3);
const batchColSpacing = ref(0);
const batchRotation = ref(0);
const batchRowDirection = ref('forward'); // 行延伸方向：forward/backward（向前/向后）
const batchColDirection = ref('left');    // 列延伸方向：left/right（向左/向右）
const isBatchPreview = ref(false);
// isRotating 已在前面定义

// 切换对象分类展开/收起
function toggleObjectCategory(category) {
  expandedObjectCategories.value[category] = !expandedObjectCategories.value[category];
}

// 流程导航状态
const currentStep = ref('create-warehouse');
const completedSteps = ref([]);
const expandedStep = ref('create-warehouse'); // 默认展开第一步

// 左右面板展开状态（默认展开）
const isLeftPanelExpanded = ref(true);
const isRightPanelExpanded = ref(true);

// 切换左侧面板展开/收起
function toggleLeftPanel() {
  isLeftPanelExpanded.value = !isLeftPanelExpanded.value;
  // 面板折叠/展开后，通知3D场景更新大小
  nextTick(() => {
    setTimeout(() => {
      if (threeScene.value && threeScene.value.handleResize) {
        threeScene.value.handleResize();
      }
    }, 350); // 等待CSS过渡动画完成(300ms)后再更新
  });
}

// 切换右侧面板展开/收起
function toggleRightPanel() {
  isRightPanelExpanded.value = !isRightPanelExpanded.value;
  // 面板折叠/展开后，通知3D场景更新大小
  nextTick(() => {
    setTimeout(() => {
      if (threeScene.value && threeScene.value.handleResize) {
        threeScene.value.handleResize();
      }
    }, 350); // 等待CSS过渡动画完成(300ms)后再更新
  });
}

// 下拉菜单展开状态
const expandedDropdowns = ref({
  'draw-warehouse': false,
  'plan-zones': false
});

// 3D对象完整名称映射表（用于悬停提示）
const modelFullNames = {
  // 仓库设施
  'door': '仓库门-标准双开门 3000×3000mm',
  'window': '仓库窗-标准采光窗 2000×1500mm',
  // 货架系统（旧版长ID，保留兼容）
  'shelf-beam-heavy': 'A101 重型横梁式货架-5层重型 承重3000kg/层',
  'shelf-beam-medium': 'A102 横梁式货架-中型4层 承重2000kg/层',
  'shelf-drive-in': 'A103 驶入式货架-重型 适合大批量存储',
  'shelf-flow-4level': 'A104 流利式货架-4层拣选 先进先出',
  'light-duty-A15-4': 'A104 4层轻型货架-L1.5xD0.4xH2.0 适合3米以下仓库',
  'light-duty-A15-5': 'A105 5层轻型货架-L1.5xD0.4xH2.0 空间利用率高',
  'light-duty-A20-4': 'A106 4层轻型货架-L2.0xD0.6xH2.0 加宽型适合大周转箱',
  'light-duty-A20-5': 'A107 5层轻型货架-L2.0xD0.6xH2.5 加高加宽型',
  'light-duty-A20-6': 'A108 6层轻型货架-L2.0xD0.6xH3.0 超高密度存储',
  'shelf-beam-heavy-3level': 'A106 横梁式货架-重型3层 承重3000kg/层',
  'shelf-beam-heavy-4level': 'A107 横梁式货架-重型4层 承重3000kg/层',
  'shelf-beam-heavy-5level': 'A108 横梁式货架-重型5层 承重3000kg/层',
  'shelf-beam-medium-4level-2m': 'A109 横梁式货架-中型4层 2米层高',
  'shelf-beam-medium-5level-2m': 'A110 横梁式货架-中型5层 2米层高',
  
  // ========== 轻型货架（10个）- 短ID格式 ==========
  'A15-4': '4层轻型货架-L1.5xD0.4xH2.0',
  'A15-5': '5层轻型货架-L1.5xD0.4xH2.0',
  'A20-4': '4层轻型货架-L2.0xD0.4xH2.0',
  'A20-5': '5层轻型货架-L2.0xD0.4xH2.0',
  'A20-6': '6层轻型货架-L2.0xD0.4xH2.0',
  'A15-4-pair': '4层轻型货架-L1.5xD0.4xH2.0-配组',
  'A15-5-pair': '5层轻型货架-L1.5xD0.4xH2.0-配组',
  'A20-4-pair': '4层轻型货架-L2.0xD0.4xH2.0-配组',
  'A20-5-pair': '5层轻型货架-L2.0xD0.4xH2.0-配组',
  'A20-6-pair': '6层轻型货架-L2.0xD0.4xH2.0-配组',
  
  // ========== 中型货架（6个）- 短ID格式 ==========
  'B20-4': '4层中型货架-L2.0xD0.6xH2.0',
  'B20-5': '5层中型货架-L2.0xD0.6xH2.5',
  'B20-6': '6层中型货架-L2.0xD0.6xH3.0',
  'B20-4-pair': '4层中型货架-L2.0xD0.6xH2.0-配组',
  'B20-5-pair': '5层中型货架-L2.0xD0.6xH2.5-配组',
  'B20-6-pair': '6层中型货架-L2.0xD0.6xH3.0-配组',
  
  // ========== 高位货架（24个）- 短ID格式 ==========
  // C23系列
  'C23-3': '3层高位货架-L2.3xD1.0xH3.0',
  'C23-4': '4层高位货架-L2.3xD1.0xH4.5',
  'C23-5': '5层高位货架-L2.3xD1.0xH6.0',
  'C23-6': '6层高位货架-L2.3xD1.0xH7.0',
  'C23-3-pair': '3层高位货架-L2.3xD1.0xH3.0-配组',
  'C23-4-pair': '4层高位货架-L2.3xD1.0xH4.5-配组',
  'C23-5-pair': '5层高位货架-L2.3xD1.0xH6.0-配组',
  'C23-6-pair': '6层高位货架-L2.3xD1.0xH7.0-配组',
  // C25系列
  'C25-3': '3层高位货架-L2.5xD1.0xH3.0',
  'C25-4': '4层高位货架-L2.5xD1.0xH4.5',
  'C25-5': '5层高位货架-L2.5xD1.0xH6.0',
  'C25-6': '6层高位货架-L2.5xD1.0xH7.0',
  'C25-3-pair': '3层高位货架-L2.5xD1.0xH3.0-配组',
  'C25-4-pair': '4层高位货架-L2.5xD1.0xH4.5-配组',
  'C25-5-pair': '5层高位货架-L2.5xD1.0xH6.0-配组',
  'C25-6-pair': '6层高位货架-L2.5xD1.0xH7.0-配组',
  // C27系列
  'C27-3': '3层高位货架-L2.7xD1.0xH3.0',
  'C27-4': '4层高位货架-L2.7xD1.0xH4.5',
  'C27-5': '5层高位货架-L2.7xD1.0xH6.0',
  'C27-6': '6层高位货架-L2.7xD1.0xH7.0',
  'C27-3-pair': '3层高位货架-L2.7xD1.0xH3.0-配组',
  'C27-4-pair': '4层高位货架-L2.7xD1.0xH4.5-配组',
  'C27-5-pair': '5层高位货架-L2.7xD1.0xH6.0-配组',
  'C27-6-pair': '6层高位货架-L2.7xD1.0xH7.0-配组',
  // 载具容器
  'pallet-wooden-1200': 'C101 木质托盘 1200×1000mm 标准四向进叉',
  'pallet-plastic-1200': 'C102 塑料托盘 1200×1000mm 网格双面',
  'pallet-wood-1200x1000': 'C103 木质托盘-标准双向进叉 1200×1000mm',
  'pallet-plastic-1200x1000': 'C104 塑料托盘-网格双面 1200×1000mm',
  'container-foldable': 'C105 可折叠周转箱-塑料折叠箱 600×400×340mm',
  'container-tote-600x400x300': 'C106 可堆叠周转箱-600×400×300mm 标准EU箱',
  'container-tote-600x400x220': 'C107 可堆叠周转箱-600×400×220mm 矮款EU箱',
  'container-tote-400x300x150': 'C108 可堆叠周转箱-400×300×150mm 小型EU箱',
  // 搬运设备
  'forklift-reach-2t': 'B101 前移式叉车-2吨9米 高位货架专用',
  'forklift-counterbalance-2.5t': 'B102 平衡重叉车-2.5吨4米 标准叉车',
  'forklift-pallet-truck-electric': 'B103 电动搬运车-2吨步行式 电动托盘车',
  'forklift-pallet-jack-manual': 'B104 手动液压搬运车-2.5吨 地牛',
  'cart-picking-3tier': 'B105 三层拣货车-标准型 订单拣选专用',
  'cart-cage-logistics-2tier': 'B106 物流笼车-2层标准款 配送周转',
  // 输送设备
  'lift-cargo-hydraulic-3floor': 'D101 液压升降平台-3层货物提升 解决高度差',
  'conveyor-curve-90degree-600': 'D102 90度转弯输送机-滚筒转弯 600mm宽',
  'conveyor-roller-straight-600-red': 'D103 动力滚筒输送机-标准直线型 600mm宽',
  // 拣选设备
  'putwall-standard-16cell': 'E101 播种墙-16格位标准型 批量拣选分拨',
  'station-packcheck-integrated-red': 'E102 打包工作站-人体工学设计 包装作业',
  'weigher-automatic-check-600-red': 'E103 自动称重机-600mm宽 动态称重',
  // 分拣设备
  'sorter-dws-straight-600': 'H101 DWS系统-自动称重扫码 信息采集',
  'sorter-wheel-diverter-600': 'H102 摆轮分拣机-高速分拣 自动分流',
  // 其他设备
  'guard-rack-heavy-redyellow': 'F101 货架防撞护栏-重型红黄警示 安全防护',
  'guard-column-protector-redyellow': 'F102 立柱防撞护角-红黄警示 货架保护',
  // 人员
  'person-warehouse-admin-red': 'G101 仓库管理员-标准工作人员 操作岗位'
};

// 获取对象完整名称（用于悬停提示）
function getModelFullName(modelId) {
  return modelFullNames[modelId] || modelId;
}

// 切换下拉菜单展开/收起
function toggleDropdown(dropdownName) {
  expandedDropdowns.value[dropdownName] = !expandedDropdowns.value[dropdownName];
}

// 切换步骤菜单展开/收起
async function toggleStepMenu(step) {
  if (expandedStep.value === step) {
    expandedStep.value = null;
  } else {
    expandedStep.value = step;
    currentStep.value = step;
    
    // 根据步骤自动切换视图
    if (step === 'create-warehouse') {
      // 创建平面仓库步骤，切换到2D视图
      if (currentView.value !== '2d') {
        currentView.value = '2d';
        console.log('自动切换到2D视图');
      }
      
      // 自动展开对应下拉菜单
      if (warehouseShape.value.length === 0) {
        // 未绘制仓库，展开"绘制平面仓库"
        expandedDropdowns.value['draw-warehouse'] = true;
        expandedDropdowns.value['plan-zones'] = false;
      } else {
        // 已绘制仓库，展开"规划功能区"
        expandedDropdowns.value['draw-warehouse'] = false;
        expandedDropdowns.value['plan-zones'] = true;
      }
    } else if (step === 'add-objects') {
      // 添加物流对象步骤，检查并自动生成3D仓库
      if (warehouseShape.value.length < 3) {
        alert('请先创建仓库！');
        // 自动跳转到创建仓库步骤
        expandedStep.value = 'create-warehouse';
        currentStep.value = 'create-warehouse';
        if (currentView.value !== '2d') {
          currentView.value = '2d';
        }
        return;
      }
      
      // 切换到3D视图（先切换，确保threeScene准备好）
      if (currentView.value !== '3d') {
        currentView.value = '3d';
        console.log('自动切换到3D视图');
      }
      
      // 等待3D场景初始化
      await nextTick();
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 如果3D仓库未生成，自动生成
      if (!is3DGenerated.value) {
        console.log('3D仓库未生成，正在自动生成...');
        await autoGenerate3DWarehouse();
      }
    }
  }
}

// 仓库配置
const warehouseConfig = ref({
  height: 5,
  baseHeight: 0,
  wallThickness: 20,
  wallOpacity: 0.15 // 围墙透明度15%，与地面网格、功能区保持一致，提升内部视野通透度
});

// 仓库尺寸（计算属性）
const warehouseDimensions = computed(() => {
  if (warehouseShape.value.length < 3) {
    return { length: 0, width: 0, height: warehouseConfig.value.height };
  }
  
  // 计算仓库边界框
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;
  
  warehouseShape.value.forEach(point => {
    minX = Math.min(minX, point.x);
    maxX = Math.max(maxX, point.x);
    minY = Math.min(minY, point.y);
    maxY = Math.max(maxY, point.y);
  });
  
  // 转换为米（画布坐标：10像素 = 1米）
  const length = Math.round((maxX - minX) / 10 * 10) / 10;
  const width = Math.round((maxY - minY) / 10 * 10) / 10;
  
  return {
    length: length > 0 ? length : 0,
    width: width > 0 ? width : 0,
    height: warehouseConfig.value.height
  };
});

// 放置对象数量
const placedObjectsCount = computed(() => {
  return threeScene.value?.getObjectsCount?.() || 0;
});

// 判断选中的对象是否是货架、托盘或拣货车（批量复制对这些对象有效）
const isSelectedObjectShelf = computed(() => {
  if (!selectedObject.value) return false;
  const type = selectedObject.value.type || '';
  const modelType = selectedObject.value.modelType || '';
  const category = selectedObject.value.category || '';
  // 检查是否为货架
  const isShelf = type === 'shelf' ||
         modelType.includes('shelf') ||
         modelType.includes('light-duty') ||
         modelType.includes('medium-duty') ||
         modelType.includes('high-duty') ||
         category.includes('shelf');
  // 检查是否为托盘
  const isPallet = type === 'pallet' ||
         modelType.includes('pallet');
  // 检查是否为拣货车
  const isCart = type === 'cart' ||
         modelType.includes('cart') ||
         modelType.includes('picking');
  // 检查是否为立柱
  const isPillar = type === 'pillar' ||
         modelType === 'pillar';
  return isShelf || isPallet || isCart || isPillar;
});

// 判断选中的对象是否是人员模型（人员模型不显示复制按钮）
const isSelectedObjectPersonnel = computed(() => {
  if (!selectedObject.value) return false;
  const type = selectedObject.value.type || '';
  const modelType = selectedObject.value.modelType || '';
  const category = selectedObject.value.category || '';
  // 检查 type、modelType 或 category 是否包含人员相关关键词
  return type === 'person' ||
         modelType.includes('person') || 
         category.includes('person') ||
         modelType.includes('admin') ||
         modelType.includes('worker');
});

// 判断选中的对象是否是搬运设备（搬运设备不显示复制按钮）
const isSelectedObjectEquipment = computed(() => {
  if (!selectedObject.value) return false;
  const type = selectedObject.value.type || '';
  const modelType = selectedObject.value.modelType || '';
  // 检查 type 或 modelType 是否包含搬运设备相关关键词
  return type === 'forklift' ||
         type === 'conveyor' ||
         modelType.includes('forklift') ||
         modelType.includes('conveyor') ||
         modelType.includes('truck') ||
         modelType.includes('jack');
});

// 2D仓库绘制
const is2DDrawing = ref(false);
const warehouseShape = ref([]);
const canvas2D = ref(null);

// 精确绘制相关状态
const showLengthDialog = ref(false);
const segmentLength = ref(null);
const currentSegmentLength = ref(0);
const isWaitingForLength = ref(false);
const isPreviewing = ref(false);
const previewLine = ref(null);
const previewPoint = ref(null);
let tempStartPoint = null;
let mousePosition = { x: 0, y: 0 };

// 线段编辑状态
const editingLineIndex = ref(null);
const selectedLineIndex = ref(null); // 选中的线条索引
const isEditingLine = ref(false);
const isEditMode = ref(false);

// 忽略下一次画布点击标志（用于文字标注点击后阻止画布清空选中）
const ignoreNextCanvasClick = ref(false);

// 功能区规划
const currentDrawTool = ref(null);
const selectedZoneType = ref('storage');
const zones = ref([]);
const showZoneListDialog = ref(false);

// 快捷生成矩形仓库弹窗
const showQuickRectWarehouseDialog = ref(false);
const quickRectWidth = ref(''); // 不预填
const quickRectHeight = ref(''); // 不预填

// 功能区创建和编辑模式
const isZoneCreateMode = ref(false);
const isZoneEditMode = ref(false);
const draggedZoneType = ref(null);
const selectedZone = ref(null);
const isDraggingZone = ref(false);
const dragStartPos = ref({ x: 0, y: 0 });

// 功能区精确尺寸编辑对话框
const showZoneSizeDialog = ref(false);
const zoneEditWidth = ref(0);
const zoneEditHeight = ref(0);

// 文字标注功能
const textLabels = ref([]);
const isAddingText = ref(false);
const showTextInputDialog = ref(false);
const textInputContent = ref('');
const textInputSize = ref(14);
const tempTextPosition = ref({ x: 0, y: 0 });
const selectedTextLabel = ref(null);
const isEditingText = ref(false);

// 自定义轻型货架功能
const showCustomLightShelfModal = ref(false);
const selectedLightShelfSpec = ref('');

// 弹窗拖动功能
const isDraggingModal = ref(false);
const dragModalTarget = ref(null);
const dragModalStartX = ref(0);
const dragModalStartY = ref(0);
const dragModalOffsetX = ref(0);
const dragModalOffsetY = ref(0);

// 轻型货架规格定义
const lightShelfSpecs = {
  'A15-5': {
    id: 'light-duty-A15-5',
    name: '5层轻型货架-L1.5xD0.4xH2.0',
    levels: 5,
    load: '300-800',
    layerHeight: '1-4层每层0.6米，顶层5CM',
    warehouseHeight: '3米以下',
    length: 1500,
    width: 400,
    height: 2000
  },
  'A20-4': {
    id: 'light-duty-A20-4',
    name: '4层轻型货架-L2.0xD0.6xH2.0',
    levels: 4,
    load: '300-800',
    layerHeight: '1-3层每层0.6米，顶层5CM',
    warehouseHeight: '3米以下',
    length: 2000,
    width: 600,
    height: 2000
  },
  'A20-5': {
    id: 'light-duty-A20-5',
    name: '5层轻型货架-L2.0xD0.6xH2.5',
    levels: 5,
    load: '300-800',
    layerHeight: '1-4层每层0.6米，顶层5CM',
    warehouseHeight: '3米以下',
    length: 2000,
    width: 600,
    height: 2500
  },
  'A20-6': {
    id: 'light-duty-A20-6',
    name: '6层轻型货架-L2.0xD0.6xH3.0',
    levels: 6,
    load: '300-800',
    layerHeight: '1-5层每层0.6米，顶层5CM',
    warehouseHeight: '4米以下',
    length: 2000,
    width: 600,
    height: 3000
  }
};

// 区域类型定义
const zoneTypes = [
  { label: '收货区', value: 'receiving', color: '#4CAF50' },
  { label: '收货暂存区', value: 'receiving_temp', color: '#81C784' },
  { label: '存储区', value: 'storage', color: '#2196F3' },
  { label: '生产区', value: 'production', color: '#9C27B0' },
  { label: '发货暂存区', value: 'shipping_temp', color: '#FFB74D' },
  { label: '发货区', value: 'shipping', color: '#FF9800' },
  { label: '办公区', value: 'office', color: '#607D8B' },
  { label: '厕所', value: 'restroom', color: '#00BCD4' },
  { label: '行政仓', value: 'admin_storage', color: '#795548' },
  { label: '叉车充电区', value: 'charging', color: '#FFC107' },
  { label: '其他区域', value: 'other', color: '#9E9E9E' }
];

// 对象库分类展开状态
const expandedCategories = ref({
  logistics: true,
  warehouse: true
});

// 计算仓库点坐标
const getWarehousePoints = computed(() => {
  return warehouseShape.value.map(p => `${p.x},${p.y}`).join(' ');
});

// 画布缩放和平移状态
const canvasScale = ref(1);
const canvasOffset = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });
const mouseCanvasPos = ref({ x: 0, y: 0 });

// 功能区编辑状态
const isResizingZone = ref(false);
const resizeHandle = ref(null); // 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'
const resizeStart = ref({ x: 0, y: 0, zone: null });

// 功能区平移状态
const isMovingZone = ref(false);
const moveStart = ref({ x: 0, y: 0, zone: null, originalX: 0, originalY: 0 });

// 画布变换样式
const canvasTransformStyle = computed(() => {
  return {
    transform: `translate(${canvasOffset.value.x}px, ${canvasOffset.value.y}px) scale(${canvasScale.value})`,
    transformOrigin: '0 0'
  };
});

// 计算仓库线段（考虑缩放和平移）
const getWarehouseLines = computed(() => {
  const lines = [];
  for (let i = 0; i < warehouseShape.value.length - 1; i++) {
    lines.push({
      x1: warehouseShape.value[i].x,
      y1: warehouseShape.value[i].y,
      x2: warehouseShape.value[i + 1].x,
      y2: warehouseShape.value[i + 1].y
    });
  }
  return lines;
});

// 获取区域点坐标
function getZonePoints(zone) {
  return zone.points.map(p => `${p.x},${p.y}`).join(' ');
}

// 获取区域中心
function getZoneCenter(zone) {
  const sumX = zone.points.reduce((sum, p) => sum + p.x, 0);
  const sumY = zone.points.reduce((sum, p) => sum + p.y, 0);
  return {
    x: sumX / zone.points.length,
    y: sumY / zone.points.length
  };
}

// 统一清空所有选中状态
function clearAllSelection() {
  selectedLineIndex.value = null;
  selectedZone.value = null;
  selectedObject.value = null;
  selectedTextLabel.value = null;
  console.log('清空所有选中状态');
}

// 切换视图
function switchTo2D() {
  currentView.value = '2d';
  console.log('切换到2D视图');
}

// 切换流程步骤
function switchStep(step) {
  currentStep.value = step;
  // 根据步骤自动切换视图
  if (step === 'create-warehouse') {
    currentView.value = '2d';
  } else if (step === 'add-objects' || step === 'finalize') {
    currentView.value = '3d';
  }
}

// 标记步骤完成并进入下一步
function completeStepAndNext(current, next) {
  if (!completedSteps.value.includes(current)) {
    completedSteps.value.push(current);
  }
  switchStep(next);
}

// 2D绘制功能 - 方案B：精确长度绘制
function start2DDrawing() {
  // 如果快捷生成弹窗打开，先关闭
  if (showQuickRectWarehouseDialog.value) {
    showQuickRectWarehouseDialog.value = false;
  }
  
  // 如果已经在绘制中，点击按钮表示继续下一段
  // 如果不在绘制中，开始新的绘制
  if (!is2DDrawing.value) {
    is2DDrawing.value = true;
    console.log('开始2D绘制，等待确定起点');
  } else if (warehouseShape.value.length > 0) {
    // 已经在绘制中，且有起点，继续绘制下一段
    continueDrawing();
  }
}

function continueDrawing() {
  if (warehouseShape.value.length === 0) return;

  // 设置起点为最后一个点
  const lastPoint = warehouseShape.value[warehouseShape.value.length - 1];
  tempStartPoint = { ...lastPoint };

  // 显示长度输入对话框
  showLengthDialog.value = true;
  isWaitingForLength.value = true;
  segmentLength.value = null; // 不预设值，让用户输入

  // 自动聚焦输入框
  setTimeout(() => {
    const input = document.querySelector('.length-dialog input');
    if (input) {
      input.focus();
      input.placeholder = '请输入长度';
    }
  }, 100);

  console.log('等待输入线段长度，起点:', tempStartPoint);
}

function confirmLengthInput() {
  if (!segmentLength.value || segmentLength.value <= 0) return;
  
  currentSegmentLength.value = segmentLength.value;
  showLengthDialog.value = false;
  isWaitingForLength.value = false;
  isPreviewing.value = true;
  
  console.log('长度输入完成:', currentSegmentLength.value, '米');
}

function cancelLengthInput() {
  showLengthDialog.value = false;
  isWaitingForLength.value = false;
  tempStartPoint = null;
  
  // 如果是编辑线条模式，取消编辑并恢复线条状态
  if (isEditingLine.value) {
    isEditingLine.value = false;
    editingLineIndex.value = null;
    selectedLineIndex.value = null; // 同时取消线条选中状态
    console.log('取消编辑线条，恢复线条状态');
  }
  
  console.log('取消长度输入');
}

function on2DCanvasMouseMove(event) {
  if (!isPreviewing.value || !tempStartPoint) return;

  const rect = event.currentTarget.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  // 计算从起点到鼠标位置的角度
  const dx = mouseX - tempStartPoint.x;
  const dy = mouseY - tempStartPoint.y;
  const angle = Math.atan2(dy, dx);

  // 根据输入的长度和角度计算终点
  // 将米转换为像素（假设1米 = 10像素）
  const pixelLength = currentSegmentLength.value * 10;
  const endX = tempStartPoint.x + Math.cos(angle) * pixelLength;
  const endY = tempStartPoint.y + Math.sin(angle) * pixelLength;

  // 检测是否为水平或垂直方向（严格对齐，仅允许0.1度误差）
  const angleDegrees = Math.abs(angle * 180 / Math.PI);
  const isHorizontal = angleDegrees < 0.1 || angleDegrees > 179.9;
  const isVertical = Math.abs(angleDegrees - 90) < 0.1;
  const isAxisAligned = isHorizontal || isVertical;

  // 更新预览线
  previewLine.value = {
    x1: tempStartPoint.x,
    y1: tempStartPoint.y,
    x2: endX,
    y2: endY,
    isAxisAligned: isAxisAligned
  };

  // 更新预览点
  previewPoint.value = {
    x: endX,
    y: endY
  };

  mousePosition = { x: mouseX, y: mouseY };
}

// 画布点击处理 - 统一处理绘制和编辑
function onCanvasClick(event) {
  // 如果标志位为true，说明是文字标注触发的点击，忽略本次点击不清空选中状态
  if (ignoreNextCanvasClick.value) {
    ignoreNextCanvasClick.value = false; // 重置标志
    console.log('忽略本次画布点击（文字标注触发）');
    return;
  }

  const rect = event.currentTarget.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  // 如果在文字添加模式下，添加文字标注
  if (isAddingText.value) {
    addTextLabel(x, y);
    return;
  }

  // 如果正在编辑线段，应用编辑
  if (isEditingLine.value && isPreviewing.value && previewPoint.value) {
    applyLineEdit();
    return;
  }

  // 如果在功能区编辑模式下，检查是否点击了功能区
  if (isZoneEditMode.value) {
    const clickedZone = findClickedZone(x, y);
    if (clickedZone) {
      console.log('点击了功能区:', clickedZone.id);
      selectedZone.value = clickedZone.id;
      return;
    }
  }

  // 如果在仓库编辑模式下，检查是否点击了线段
  if (isEditMode.value && !is2DDrawing.value) {
    const clickedLineIndex = findClickedLine(x, y);
    if (clickedLineIndex !== -1) {
      console.log('点击了线段:', clickedLineIndex);
      editLine(clickedLineIndex);
      return;
    }
  }

  // 检查是否点击了线段（非编辑模式下，用于选中）
  if (!is2DDrawing.value && !isEditMode.value) {
    const clickedLineIndex = findClickedLine(x, y);
    if (clickedLineIndex !== -1) {
      console.log('选中线条:', clickedLineIndex);
      selectedLineIndex.value = clickedLineIndex;
      // 取消功能区选中
      selectedZone.value = null;
      return;
    } else {
      // 点击空白处，使用统一清空函数
      clearAllSelection();
    }
  }

  // 绘制模式处理
  if (!is2DDrawing.value && !currentDrawTool.value) return;

  if (is2DDrawing.value) {
    if (warehouseShape.value.length === 0) {
      // 确定起点
      warehouseShape.value.push({ x, y });
      console.log('确定起点:', { x, y });
      continueDrawing();
    } else if (isPreviewing.value && previewPoint.value) {
      // 确定落点（继续绘制）
      warehouseShape.value.push({
        x: previewPoint.value.x,
        y: previewPoint.value.y
      });
      console.log('确定落点:', previewPoint.value, '长度:', currentSegmentLength.value, '米');
      isPreviewing.value = false;
      previewLine.value = null;
      previewPoint.value = null;
      continueDrawing();
    } else if (!isPreviewing.value && !isWaitingForLength.value) {
      // 重新开始绘制新线段（从当前点开始）
      warehouseShape.value.push({ x, y });
      console.log('确定新起点:', { x, y });
      continueDrawing();
    }
  } else if (currentDrawTool.value) {
    handleZoneDrawing(x, y);
  }
}

// 查找点击的功能区
function findClickedZone(x, y) {
  // 从后向前查找，优先选中上层的功能区
  for (let i = zones.value.length - 1; i >= 0; i--) {
    const zone = zones.value[i];
    if (zone.x !== undefined && zone.y !== undefined && zone.width !== undefined && zone.height !== undefined) {
      // 矩形区域检测
      if (x >= zone.x && x <= zone.x + zone.width && y >= zone.y && y <= zone.y + zone.height) {
        return zone;
      }
    } else if (zone.points && zone.points.length > 0) {
      // 多边形区域检测（使用射线法）
      if (isPointInPolygon(x, y, zone.points)) {
        return zone;
      }
    }
  }
  return null;
}

// 计算功能区尺寸和面积（格式：长X宽=面积平米）
function getZoneDimensions(zone) {
  if (zone.x === undefined || zone.y === undefined || zone.width === undefined || zone.height === undefined) {
    return '';
  }
  // 转换为米（1像素 = 0.1米）
  const length = Math.round(zone.width / 10);
  const width = Math.round(zone.height / 10);
  const area = length * width;
  return `${length}X${width}=${area}㎡`;
}

// 射线法判断点是否在多边形内
function isPointInPolygon(x, y, points) {
  let inside = false;
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    const xi = points[i].x, yi = points[i].y;
    const xj = points[j].x, yj = points[j].y;

    const intersect = ((yi > y) !== (yj > y)) &&
      (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

// 查找点击的线段
function findClickedLine(x, y) {
  const threshold = 10; // 点击容差10像素
  
  for (let i = 0; i < getWarehouseLines.value.length; i++) {
    const line = getWarehouseLines.value[i];
    const dist = pointToLineDistance(x, y, line.x1, line.y1, line.x2, line.y2);
    if (dist < threshold) {
      return i;
    }
  }
  return -1;
}

// 计算点到线段的距离
function pointToLineDistance(px, py, x1, y1, x2, y2) {
  const A = px - x1;
  const B = py - y1;
  const C = x2 - x1;
  const D = y2 - y1;
  
  const dot = A * C + B * D;
  const lenSq = C * C + D * D;
  let param = -1;
  
  if (lenSq !== 0) {
    param = dot / lenSq;
  }
  
  let xx, yy;
  
  if (param < 0) {
    xx = x1;
    yy = y1;
  } else if (param > 1) {
    xx = x2;
    yy = y2;
  } else {
    xx = x1 + param * C;
    yy = y1 + param * D;
  }
  
  const dx = px - xx;
  const dy = py - yy;
  return Math.sqrt(dx * dx + dy * dy);
}

// 画布缩放控制
function onCanvasWheel(event) {
  event.preventDefault();
  const delta = event.deltaY > 0 ? 0.9 : 1.1;
  const newScale = canvasScale.value * delta;
  // 限制缩放范围
  if (newScale >= 0.1 && newScale <= 5) {
    canvasScale.value = newScale;
  }
}

// 开始平移
function onCanvasMouseDown(event) {
  // 按住空格键或中键开始平移
  if (event.button === 1 || (event.button === 0 && event.shiftKey)) {
    isPanning.value = true;
    panStart.value = { x: event.clientX, y: event.clientY };
    event.preventDefault();
  }
}

// 平移中
function onCanvasMouseMove(event) {
  // 更新鼠标坐标显示
  const rect = event.currentTarget.getBoundingClientRect();
  const x = (event.clientX - rect.left - canvasOffset.value.x) / canvasScale.value;
  const y = (event.clientY - rect.top - canvasOffset.value.y) / canvasScale.value;
  mouseCanvasPos.value = { x: Math.round(x), y: Math.round(y) };
  
  // 处理平移
  if (isPanning.value) {
    const dx = event.clientX - panStart.value.x;
    const dy = event.clientY - panStart.value.y;
    canvasOffset.value.x += dx;
    canvasOffset.value.y += dy;
    panStart.value = { x: event.clientX, y: event.clientY };
  }
  
  // 原有的鼠标移动处理
  on2DCanvasMouseMove(event);
}

// 结束平移
function onCanvasMouseUp() {
  isPanning.value = false;
}

// 重置画布视图
function resetCanvasView() {
  canvasScale.value = 1;
  canvasOffset.value = { x: 0, y: 0 };
}

// 3D视图控制方法
function zoom3DIn() {
  if (threeScene.value && threeScene.value.zoomIn) {
    threeScene.value.zoomIn();
  }
}

function zoom3DOut() {
  if (threeScene.value && threeScene.value.zoomOut) {
    threeScene.value.zoomOut();
  }
}

function reset3DView() {
  if (threeScene.value && threeScene.value.resetView) {
    threeScene.value.resetView();
  }
}

// 刷新3D视图（手动触发渲染，解决v-show切换后的渲染问题）
function refresh3DView() {
  console.log('手动刷新3D视图...');

  // 1. 强制渲染
  if (threeScene.value && threeScene.value.forceRender) {
    threeScene.value.forceRender();
  }

  // 2. 触发resize事件
  window.dispatchEvent(new Event('resize'));

  // 3. 延迟再次触发
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
    if (threeScene.value && threeScene.value.forceRender) {
      threeScene.value.forceRender();
    }
    console.log('3D视图刷新完成');
  }, 100);
}

// 兼容旧代码
function on2DCanvasClick(event) {
  onCanvasClick(event);
}

function clear2DDrawing() {
  warehouseShape.value = [];
  is2DDrawing.value = false;
  isPreviewing.value = false;
  isWaitingForLength.value = false;
  isEditingLine.value = false;
  isEditMode.value = false;
  editingLineIndex.value = null;
  previewLine.value = null;
  previewPoint.value = null;
  tempStartPoint = null;
  showLengthDialog.value = false;
  currentSegmentLength.value = 0;
  console.log('清空2D绘制');
}

// 显示快捷生成矩形仓库弹窗
function showQuickRectDialog() {
  // 如果正在手动绘制，先清空绘制模式
  if (is2DDrawing.value) {
    clear2DDrawing();
  }
  
  showQuickRectWarehouseDialog.value = true;
  // 弹窗显示后，自动聚焦第一个输入框
  setTimeout(() => {
    const firstInput = document.querySelector('.quick-rect-input');
    if (firstInput) {
      firstInput.focus();
    }
  }, 100);
}

// 快捷生成矩形仓库
function generateQuickRectWarehouse() {
  const width = parseFloat(quickRectWidth.value) * 10; // 转换为像素（1米=10像素）
  const height = parseFloat(quickRectHeight.value) * 10;

  // 验证输入
  if (!width || !height || width <= 0 || height <= 0) {
    alert('请输入有效的长度和宽度！');
    return;
  }

  // 获取画布实际尺寸
  const canvas2DElement = document.querySelector('.canvas-2d-area');
  const canvasWidth = canvas2DElement ? canvas2DElement.clientWidth : 800;
  const canvasHeight = canvas2DElement ? canvas2DElement.clientHeight : 600;
  
  // 计算画布中心位置（考虑缩放和平移偏移）
  const centerX = (canvasWidth / 2 - canvasOffset.value.x) / canvasScale.value;
  const centerY = (canvasHeight / 2 - canvasOffset.value.y) / canvasScale.value;

  // 计算矩形四个顶点（从中心点计算）
  const halfWidth = width / 2;
  const halfHeight = height / 2;

  // 清空现有绘制
  warehouseShape.value = [];

  // 添加四个顶点（顺时针）
  warehouseShape.value.push({ x: centerX - halfWidth, y: centerY - halfHeight }); // 左上
  warehouseShape.value.push({ x: centerX + halfWidth, y: centerY - halfHeight }); // 右上
  warehouseShape.value.push({ x: centerX + halfWidth, y: centerY + halfHeight }); // 右下
  warehouseShape.value.push({ x: centerX - halfWidth, y: centerY + halfHeight }); // 左下
  // 添加第一个点到最后，闭合矩形
  warehouseShape.value.push({ x: centerX - halfWidth, y: centerY - halfHeight }); // 回到左上

  // 关闭弹窗
  showQuickRectWarehouseDialog.value = false;

  console.log('快捷生成矩形仓库:', quickRectWidth.value + 'm x ' + quickRectHeight.value + 'm');
}

// 取消快捷生成
function cancelQuickRectWarehouse() {
  showQuickRectWarehouseDialog.value = false;
}

function finish2DDrawing() {
  if (warehouseShape.value.length < 3) {
    alert('请至少绘制3个点！');
    return;
  }
  // 完全重置所有绘制状态
  is2DDrawing.value = false;
  isPreviewing.value = false;
  isWaitingForLength.value = false;
  isEditingLine.value = false;
  isEditMode.value = false;
  editingLineIndex.value = null;
  previewLine.value = null;
  previewPoint.value = null;
  tempStartPoint = null;
  showLengthDialog.value = false;
  currentSegmentLength.value = 0;
  console.log('完成2D绘制，共', warehouseShape.value.length, '个点');
}

// 进入编辑模式
function enterEditMode() {
  if (warehouseShape.value.length === 0) return;
  
  // 如果正在绘制中，先完成绘制
  if (is2DDrawing.value) {
    is2DDrawing.value = false;
    isPreviewing.value = false;
    isWaitingForLength.value = false;
    showLengthDialog.value = false;
    previewLine.value = null;
    previewPoint.value = null;
    tempStartPoint = null;
    console.log('自动完成绘制，进入编辑模式');
  }
  
  isEditMode.value = true;
  console.log('进入编辑模式');
}

// 切换编辑模式（开始编辑/完成编辑）
function toggleEditMode() {
  if (warehouseShape.value.length === 0) return;
  
  if (isEditMode.value) {
    // 当前在编辑模式，点击后完成编辑
    isEditMode.value = false;
    editingLineIndex.value = null;
    selectedLineIndex.value = null;
    isEditingLine.value = false;
    console.log('完成编辑');
  } else {
    // 当前不在编辑模式，点击后开始编辑
    enterEditMode();
  }
}

// 编辑选中的线条
function editSelectedLine() {
  if (selectedLineIndex.value === null) return;
  editLine(selectedLineIndex.value);
}

// 编辑立柱高度
function editPillarHeight() {
  if (!selectedObject.value || selectedObject.value.type !== 'pillar') return;
  
  // 获取当前高度（转换为米）
  const currentHeight = selectedObject.value.height || 500;
  pillarHeightInput.value = currentHeight / 100; // 转换为米
  
  showPillarHeightDialog.value = true;
}

// 确认立柱高度编辑
function confirmPillarHeightEdit() {
  if (!selectedObject.value || selectedObject.value.type !== 'pillar') return;
  
  const newHeightCm = pillarHeightInput.value * 100; // 转换为厘米
  
  // 调用 ThreeScene 的 updatePillarHeight 函数
  if (threeScene.value && threeScene.value.updatePillarHeight) {
    const result = threeScene.value.updatePillarHeight(selectedObject.value, newHeightCm);
    if (result) {
      // 更新选中对象的高度值
      selectedObject.value.height = newHeightCm;
      console.log('立柱高度已更新为:', pillarHeightInput.value, '米');
    }
  }
  
  showPillarHeightDialog.value = false;
}

// 取消立柱高度编辑
function cancelPillarHeightEdit() {
  showPillarHeightDialog.value = false;
}

// 删除选中的线条
function deleteSelectedLine() {
  if (selectedLineIndex.value === null) return;
  
  // 删除选中的线条
  const index = selectedLineIndex.value;
  if (index >= 0 && index < warehouseShape.value.length) {
    warehouseShape.value.splice(index, 1);
    selectedLineIndex.value = null;
    editingLineIndex.value = null;
    console.log('删除线条，索引:', index);
  }
}

// 线段点击处理 - 使用原生事件
function handleLineClick(lineIndex) {
  console.log('handleLineClick 被调用，索引:', lineIndex);
  
  // 设置选中的线条索引
  selectedLineIndex.value = lineIndex;
  
  if (!isEditMode.value) {
    console.log('不在编辑模式，仅选中线条');
    return;
  }
  
  // 进入编辑状态
  editLine(lineIndex);
}

// 线段点击处理 - 兼容旧代码
function onLineClick(lineIndex) {
  console.log('onLineClick 被调用，索引:', lineIndex);
  handleLineClick(lineIndex);
}

// 线段编辑功能
function editLine(lineIndex) {
  console.log('开始编辑线段，索引:', lineIndex);
  
  // 如果正在绘制中，先完成当前绘制
  if (is2DDrawing.value) {
    // 自动完成当前绘制，进入编辑模式
    is2DDrawing.value = false;
    isPreviewing.value = false;
    isWaitingForLength.value = false;
    showLengthDialog.value = false;
    previewLine.value = null;
    previewPoint.value = null;
    tempStartPoint = null;
    console.log('自动完成当前绘制，进入编辑模式');
  }
  
  editingLineIndex.value = lineIndex;
  isEditingLine.value = true;
  
  // 获取线段的起点
  const line = getWarehouseLines.value[lineIndex];
  tempStartPoint = { x: line.x1, y: line.y1 };
  
  // 计算当前线段长度
  const dx = line.x2 - line.x1;
  const dy = line.y2 - line.y1;
  const currentLength = Math.sqrt(dx * dx + dy * dy) / 10; // 像素转米

  // 不预设值，让用户输入新长度
  segmentLength.value = null;
  currentSegmentLength.value = currentLength;

  // 显示长度输入对话框
  showLengthDialog.value = true;
  isWaitingForLength.value = true;

  // 自动聚焦输入框
  setTimeout(() => {
    const input = document.querySelector('.length-dialog input');
    if (input) {
      input.focus();
      input.placeholder = `当前长度: ${Math.round(currentLength * 10) / 10}米，输入新长度`;
    }
  }, 100);

  console.log('编辑线段:', lineIndex, '当前长度:', currentLength, '米');
}

function confirmEditLine() {
  if (!segmentLength.value || segmentLength.value <= 0) return;
  
  // 将用户输入的长度赋值给currentSegmentLength
  currentSegmentLength.value = segmentLength.value;
  
  showLengthDialog.value = false;
  isWaitingForLength.value = false;
  isPreviewing.value = true;
  
  console.log('编辑线段长度:', currentSegmentLength.value, '米');
}

function applyLineEdit() {
  if (editingLineIndex.value === null || !previewPoint.value) return;
  
  // 更新终点位置
  const lineIndex = editingLineIndex.value;
  warehouseShape.value[lineIndex + 1] = {
    x: previewPoint.value.x,
    y: previewPoint.value.y
  };
  
  // 重置编辑状态
  editingLineIndex.value = null;
  isEditingLine.value = false;
  isPreviewing.value = false;
  previewLine.value = null;
  previewPoint.value = null;
  tempStartPoint = null;
  
  console.log('线段编辑完成');
}

// 键盘事件处理 - ESC取消当前线段
function handleKeyDown(event) {
  if (event.key === 'Escape') {
    // 优先处理批量复制预览取消
    if (isBatchPreview.value) {
      cancelBatchPreview();
      console.log('ESC：取消批量复制预览');
      return;
    }
    
    if (isEditingLine.value) {
      // 取消线段编辑
      editingLineIndex.value = null;
      isEditingLine.value = false;
      isPreviewing.value = false;
      previewLine.value = null;
      previewPoint.value = null;
      tempStartPoint = null;
      showLengthDialog.value = false;
      isWaitingForLength.value = false;
      console.log('ESC：取消线段编辑');
    } else if (isPreviewing.value) {
      // 取消当前预览，回到长度输入
      isPreviewing.value = false;
      previewLine.value = null;
      previewPoint.value = null;
      showLengthDialog.value = true;
      isWaitingForLength.value = true;
      console.log('ESC：取消预览，重新输入长度');
    } else if (isWaitingForLength.value) {
      // 取消长度输入，结束绘制
      cancelLengthInput();
      // 重置绘制状态
      is2DDrawing.value = false;
      currentDrawTool.value = null;
      console.log('ESC：结束绘制');
    } else if (is2DDrawing.value) {
      // 直接取消绘制模式
      is2DDrawing.value = false;
      currentDrawTool.value = null;
      console.log('ESC：取消绘制模式');
    } else if (isAlignLineMode.value) {
      // 退出对齐线绘制模式
      isAlignLineMode.value = false;
      if (threeScene.value) {
        threeScene.value.cancelDrawingAlignmentLine();
      }
      // 自动切换到选择模式
      setSelectMode();
      console.log('ESC：退出对齐线绘制模式，切换到选择模式');
    } else if (isMeasuring.value) {
      // 退出测量模式
      isMeasuring.value = false;
      if (threeScene.value) {
        threeScene.value.stopMeasuring();
      }
      // 自动切换到选择模式
      setSelectMode();
      console.log('ESC：退出测量模式，切换到选择模式');
    }
  }
  
  // Delete键删除选中的功能区
  if (event.key === 'Delete' || event.key === 'Backspace') {
    if (isZoneEditMode.value && selectedZone.value) {
      const zoneIndex = zones.value.findIndex(z => z.id === selectedZone.value);
      if (zoneIndex !== -1) {
        const zoneName = zones.value[zoneIndex].name;
        zones.value.splice(zoneIndex, 1);
        selectedZone.value = null;
        console.log('删除功能区:', zoneName);
      }
    }
  }
}

// 添加键盘监听
window.addEventListener('keydown', handleKeyDown);

// 文字标注功能
function startAddText() {
  isAddingText.value = !isAddingText.value;
  if (isAddingText.value) {
    // 退出其他模式
    isZoneCreateMode.value = false;
    isZoneEditMode.value = false;
    console.log('进入文字添加模式，请点击画布位置');
  } else {
    console.log('退出文字添加模式');
  }
}

// 在指定位置添加文字
function addTextLabel(x, y) {
  tempTextPosition.value = { x, y };
  textInputContent.value = '';
  textInputSize.value = 14;
  showTextInputDialog.value = true;
  isAddingText.value = false;
  console.log('准备添加文字，位置:', x, y);
}

// 确认添加文字
function confirmAddText() {
  if (!textInputContent.value.trim()) {
    alert('请输入文字内容！');
    return;
  }
  
  const newLabel = {
    id: 'text_' + Date.now(),
    content: textInputContent.value,
    x: tempTextPosition.value.x,
    y: tempTextPosition.value.y,
    fontSize: textInputSize.value,
    color: '#333'
  };
  
  textLabels.value.push(newLabel);
  showTextInputDialog.value = false;
  textInputContent.value = '';
  console.log('添加文字标注:', newLabel);
}

// 取消添加文字
function cancelAddText() {
  showTextInputDialog.value = false;
  textInputContent.value = '';
  console.log('取消添加文字');
}

// 自定义轻型货架功能
function openCustomLightShelfModal() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  selectedLightShelfSpec.value = '';
  showCustomLightShelfModal.value = true;
  console.log('打开自定义轻型货架弹窗');
}

function closeCustomLightShelfModal() {
  showCustomLightShelfModal.value = false;
  selectedLightShelfSpec.value = '';
  console.log('关闭自定义轻型货架弹窗');
}

function confirmAddCustomLightShelf() {
  if (!selectedLightShelfSpec.value) {
    alert('请选择一个规格！');
    return;
  }
  
  const spec = lightShelfSpecs[selectedLightShelfSpec.value];
  console.log('添加自定义轻型货架:', spec);
  
  // 添加到3D场景 - 使用addModel方法（与预置货架相同）
  if (threeScene.value) {
    console.log('使用addModel方法添加模型:', spec.id);
    
    // 直接调用addModel，让ThreeScene处理位置
    threeScene.value.addModel(spec.id);
    
    console.log('addModel调用完成');
  } else {
    console.log('threeScene不存在！');
  }
  
  // 关闭弹窗
  closeCustomLightShelfModal();
}

// 弹窗拖动功能 - 开始拖动
function onModalDragStart(event, modalRef) {
  // 只有点击标题栏才能拖动
  if (!event.target.closest('.modal-title')) return;

  isDraggingModal.value = true;
  dragModalTarget.value = modalRef;
  dragModalStartX.value = event.clientX;
  dragModalStartY.value = event.clientY;

  // 获取当前偏移量
  const dialog = event.target.closest('.modal-dialog');
  if (dialog) {
    const rect = dialog.getBoundingClientRect();
    const parentRect = dialog.parentElement.getBoundingClientRect();
    dragModalOffsetX.value = rect.left - parentRect.left;
    dragModalOffsetY.value = rect.top - parentRect.top;
  }

  // 添加全局事件监听
  document.addEventListener('mousemove', onModalDragMove);
  document.addEventListener('mouseup', onModalDragEnd);

  event.preventDefault();
  console.log('开始拖动弹窗:', modalRef);
}

// 弹窗拖动功能 - 拖动中
function onModalDragMove(event) {
  if (!isDraggingModal.value) return;

  const deltaX = event.clientX - dragModalStartX.value;
  const deltaY = event.clientY - dragModalStartY.value;

  // 更新弹窗位置
  const dialogs = document.querySelectorAll('.modal-dialog');
  dialogs.forEach(dialog => {
    if (dialog.style.position !== 'fixed') {
      dialog.style.position = 'fixed';
    }
    dialog.style.left = (dragModalOffsetX.value + deltaX) + 'px';
    dialog.style.top = (dragModalOffsetY.value + deltaY) + 'px';
    dialog.style.transform = 'none';
  });
}

// 弹窗拖动功能 - 结束拖动
function onModalDragEnd() {
  isDraggingModal.value = false;
  dragModalTarget.value = null;

  // 移除全局事件监听
  document.removeEventListener('mousemove', onModalDragMove);
  document.removeEventListener('mouseup', onModalDragEnd);

  console.log('结束拖动弹窗');
}

// 编辑文字标注
function editTextLabel(labelId) {
  const label = textLabels.value.find(l => l.id === labelId);
  if (!label) return;
  
  selectedTextLabel.value = labelId;
  isEditingText.value = true;
  textInputContent.value = label.content;
  textInputSize.value = label.fontSize;
  showTextInputDialog.value = true;
  console.log('编辑文字标注:', labelId);
}

// 确认编辑文字
function confirmEditText() {
  if (!textInputContent.value.trim()) {
    alert('请输入文字内容！');
    return;
  }
  
  const label = textLabels.value.find(l => l.id === selectedTextLabel.value);
  if (label) {
    label.content = textInputContent.value;
    label.fontSize = textInputSize.value;
    console.log('更新文字标注:', selectedTextLabel.value);
  }
  
  showTextInputDialog.value = false;
  selectedTextLabel.value = null;
  isEditingText.value = false;
  textInputContent.value = '';
}

// 删除文字标注
function deleteTextLabel(labelId) {
  const index = textLabels.value.findIndex(l => l.id === labelId);
  if (index !== -1) {
    textLabels.value.splice(index, 1);
    console.log('删除文字标注:', labelId);
  }
}

// 开始拖拽文字标注
// 文字标注鼠标按下处理（点击选中或开始拖动）
function onTextLabelMouseDown(event, labelId) {
  // 设置标志：接下来忽略一次画布点击（防止click事件清空选中状态）
  ignoreNextCanvasClick.value = true;
  
  // 选中文字标注
  selectedTextLabel.value = labelId;
  // 取消其他选中状态
  selectedZone.value = null;
  selectedLineIndex.value = null;
  console.log('选中文字标注:', labelId);
  
  // 开始拖动
  onTextLabelDragStart(event, labelId);
}

function onTextLabelDragStart(event, labelId) {
  const label = textLabels.value.find(l => l.id === labelId);
  if (!label) return;
  
  const startX = event.clientX;
  const startY = event.clientY;
  const originalX = label.x;
  const originalY = label.y;
  
  function onMouseMove(e) {
    const dx = (e.clientX - startX) / canvasScale.value;
    const dy = (e.clientY - startY) / canvasScale.value;
    label.x = originalX + dx;
    label.y = originalY + dy;
  }
  
  function onMouseUp(e) {
    e.stopPropagation(); // 阻止事件冒泡到画布，防止清空选中状态
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
    console.log('文字标注移动完成:', labelId);
  }
  
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
  
  event.preventDefault();
  event.stopPropagation();
}

// 功能区创建和编辑模式
function enterZoneCreateMode() {
  isZoneCreateMode.value = true;
  isZoneEditMode.value = false;
  selectedZone.value = null;
  console.log('进入功能区创建模式');
}

// 切换功能区编辑模式（点击编辑按钮进入/退出）
function toggleZoneEditMode() {
  if (isZoneEditMode.value) {
    // 当前在编辑模式，退出
    isZoneEditMode.value = false;
    selectedZone.value = null;
    console.log('退出功能区编辑模式');
  } else {
    // 当前不在编辑模式，进入
    isZoneCreateMode.value = false;
    isZoneEditMode.value = true;
    console.log('进入功能区编辑模式');
  }
}

// 退出功能区编辑模式
function exitZoneEditMode() {
  isZoneEditMode.value = false;
  selectedZone.value = null;
  console.log('退出功能区编辑模式');
}

// 功能区拖拽创建
function onZoneDragStart(event, zoneType) {
  draggedZoneType.value = zoneType;
  event.dataTransfer.setData('zoneType', JSON.stringify(zoneType));
  event.dataTransfer.effectAllowed = 'copy';
  
  // 【优化】创建简单的拖拽图像，提高性能
  const dragImage = document.createElement('div');
  dragImage.style.width = '60px';
  dragImage.style.height = '40px';
  dragImage.style.backgroundColor = zoneType.color;
  dragImage.style.opacity = '0.8';
  dragImage.style.position = 'fixed';
  dragImage.style.top = '-100px';
  dragImage.style.left = '-100px';
  document.body.appendChild(dragImage);
  event.dataTransfer.setDragImage(dragImage, 30, 20);
  
  // 拖拽结束后清理
  setTimeout(() => {
    document.body.removeChild(dragImage);
  }, 0);
  
  console.log('开始拖拽功能区:', zoneType.label);
}

function onZoneDrop(event) {
  event.preventDefault();

  if (!draggedZoneType.value) return;

  // 使用canvas2D ref获取画布位置
  const canvas = canvas2D.value;
  if (!canvas) return;

  const rect = canvas.getBoundingClientRect();
  // 【修复】考虑画布缩放和平移，将鼠标坐标转换为实际画布坐标
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;
  const x = (mouseX - canvasOffset.value.x) / canvasScale.value;
  const y = (mouseY - canvasOffset.value.y) / canvasScale.value;

  // 创建默认大小的矩形功能区（100x60像素，对应10x6米）
  const width = 100;
  const height = 60;

  const newZone = {
    id: `zone_${Date.now()}`,
    name: draggedZoneType.value.label,
    type: draggedZoneType.value.value,
    color: draggedZoneType.value.color,
    x: x - width / 2,
    y: y - height / 2,
    width: width,
    height: height,
    points: [
      { x: x - width / 2, y: y - height / 2 },
      { x: x + width / 2, y: y - height / 2 },
      { x: x + width / 2, y: y + height / 2 },
      { x: x - width / 2, y: y + height / 2 }
    ]
  };

  zones.value.push(newZone);
  draggedZoneType.value = null;
  console.log('创建功能区:', newZone.name, '位置:', { x, y });
}

function onZoneDragOver(event) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'copy';
}

// 功能区点击选择
function onZoneClick(zoneId) {
  // 随时可选中功能区，不限于编辑模式
  selectedZone.value = zoneId;
  // 进入功能区编辑模式，显示8个手柄
  isZoneEditMode.value = true;
  // 取消线条选中
  selectedLineIndex.value = null;
  console.log('选中功能区:', zoneId);
}

// 开始调整功能区大小
function onZoneResizeStart(event, handle, zoneId) {
  if (!isZoneEditMode.value) return;
  event.stopPropagation();

  const zone = zones.value.find(z => z.id === zoneId);
  if (!zone) return;

  isResizingZone.value = true;
  resizeHandle.value = handle;
  resizeStart.value = {
    x: event.clientX,
    y: event.clientY,
    zone: zone,
    originalX: zone.x,
    originalY: zone.y,
    originalWidth: zone.width,
    originalHeight: zone.height
  };

  console.log('开始调整功能区大小:', zoneId, '手柄:', handle);
}

// 调整功能区大小中
function onZoneResizeMove(event) {
  if (!isResizingZone.value || !resizeStart.value.zone) return;

  const dx = (event.clientX - resizeStart.value.x) / canvasScale.value;
  const dy = (event.clientY - resizeStart.value.y) / canvasScale.value;
  const zone = resizeStart.value.zone;

  switch (resizeHandle.value) {
    case 'se': // 东南角 - 调整宽高
      zone.width = Math.max(20, resizeStart.value.originalWidth + dx);
      zone.height = Math.max(20, resizeStart.value.originalHeight + dy);
      break;
    case 'nw': // 西北角 - 调整位置和宽高
      const newWidthNW = Math.max(20, resizeStart.value.originalWidth - dx);
      const newHeightNW = Math.max(20, resizeStart.value.originalHeight - dy);
      zone.x = resizeStart.value.originalX + resizeStart.value.originalWidth - newWidthNW;
      zone.y = resizeStart.value.originalY + resizeStart.value.originalHeight - newHeightNW;
      zone.width = newWidthNW;
      zone.height = newHeightNW;
      break;
    case 'ne': // 东北角
      const newHeightNE = Math.max(20, resizeStart.value.originalHeight - dy);
      zone.y = resizeStart.value.originalY + resizeStart.value.originalHeight - newHeightNE;
      zone.width = Math.max(20, resizeStart.value.originalWidth + dx);
      zone.height = newHeightNE;
      break;
    case 'sw': // 西南角
      const newWidthSW = Math.max(20, resizeStart.value.originalWidth - dx);
      zone.x = resizeStart.value.originalX + resizeStart.value.originalWidth - newWidthSW;
      zone.width = newWidthSW;
      zone.height = Math.max(20, resizeStart.value.originalHeight + dy);
      break;
    case 'e': // 东 - 只调整宽度
      zone.width = Math.max(20, resizeStart.value.originalWidth + dx);
      break;
    case 'w': // 西 - 调整位置和宽度
      const newWidthW = Math.max(20, resizeStart.value.originalWidth - dx);
      zone.x = resizeStart.value.originalX + resizeStart.value.originalWidth - newWidthW;
      zone.width = newWidthW;
      break;
    case 'n': // 北 - 调整位置和高度
      const newHeightN = Math.max(20, resizeStart.value.originalHeight - dy);
      zone.y = resizeStart.value.originalY + resizeStart.value.originalHeight - newHeightN;
      zone.height = newHeightN;
      break;
    case 's': // 南 - 只调整高度
      zone.height = Math.max(20, resizeStart.value.originalHeight + dy);
      break;
  }

  // 更新points数组
  updateZonePoints(zone);
}

// 结束调整功能区大小
function onZoneResizeEnd() {
  if (isResizingZone.value) {
    console.log('功能区大小调整完成');
  }
  isResizingZone.value = false;
  resizeHandle.value = null;
  resizeStart.value = { x: 0, y: 0, zone: null };
}

// 更新功能区points数组
function updateZonePoints(zone) {
  if (zone.x !== undefined && zone.y !== undefined && zone.width !== undefined && zone.height !== undefined) {
    zone.points = [
      { x: zone.x, y: zone.y },
      { x: zone.x + zone.width, y: zone.y },
      { x: zone.x + zone.width, y: zone.y + zone.height },
      { x: zone.x, y: zone.y + zone.height }
    ];
  }
}

// 双击功能区进行精确编辑
function onZoneDoubleClick(zoneId) {
  if (!isZoneEditMode.value) return;

  const zone = zones.value.find(z => z.id === zoneId);
  if (!zone) return;

  // 提示用户输入新尺寸
  const newWidth = prompt(`请输入新宽度 (米):`, Math.round(zone.width / 10));
  if (newWidth === null) return;

  const newHeight = prompt(`请输入新高度 (米):`, Math.round(zone.height / 10));
  if (newHeight === null) return;

  const width = parseFloat(newWidth) * 10; // 转换为像素
  const height = parseFloat(newHeight) * 10;

  if (width > 0 && height > 0) {
    zone.width = width;
    zone.height = height;
    updateZonePoints(zone);
    console.log('功能区尺寸更新:', zone.name, '宽:', width, '高:', height);
  }
}

// 开始平移功能区
function onZoneMoveStart(event, zoneId) {
  if (!isZoneEditMode.value) return;
  // 如果点击的是调整手柄，不启动平移
  if (event.target.classList.contains('resize-handle')) return;

  const zone = zones.value.find(z => z.id === zoneId);
  if (!zone) return;

  isMovingZone.value = true;
  moveStart.value = {
    x: event.clientX,
    y: event.clientY,
    zone: zone,
    originalX: zone.x,
    originalY: zone.y
  };

  console.log('开始平移功能区:', zoneId);
}

// 平移功能区中
function onZoneMove(event) {
  if (!isMovingZone.value || !moveStart.value.zone) return;

  const dx = (event.clientX - moveStart.value.x) / canvasScale.value;
  const dy = (event.clientY - moveStart.value.y) / canvasScale.value;
  const zone = moveStart.value.zone;

  zone.x = moveStart.value.originalX + dx;
  zone.y = moveStart.value.originalY + dy;

  // 更新points数组
  updateZonePoints(zone);
}

// 结束平移功能区
function onZoneMoveEnd() {
  if (isMovingZone.value) {
    console.log('功能区平移完成');
  }
  isMovingZone.value = false;
  moveStart.value = { x: 0, y: 0, zone: null, originalX: 0, originalY: 0 };
}

// 统一的鼠标移动处理
function onZoneMouseMove(event) {
  onZoneResizeMove(event);
  onZoneMove(event);
}

// 统一的鼠标释放处理
function onZoneMouseUp() {
  onZoneResizeEnd();
  onZoneMoveEnd();
}

// 功能区绘制
let currentZonePoints = [];

function startDrawZone(toolType) {
  currentDrawTool.value = toolType;
  currentZonePoints = [];
  console.log('开始绘制功能区:', toolType);
}

function cancelDrawZone() {
  currentDrawTool.value = null;
  currentZonePoints = [];
  console.log('取消绘制功能区');
}

function handleZoneDrawing(x, y) {
  currentZonePoints.push({ x, y });
  
  if (currentDrawTool.value === 'rectangle' && currentZonePoints.length === 2) {
    finishZoneDrawing();
  } else if (currentDrawTool.value === 'polygon' && currentZonePoints.length >= 3) {
    // 多边形需要双击或点击完成按钮来完成
  }
}

function finishZoneDrawing() {
  if (currentZonePoints.length < 2) return;
  
  const zoneType = zoneTypes.find(t => t.value === selectedZoneType.value);
  const newZone = {
    id: `zone_${Date.now()}`,
    name: zoneType.label,
    type: selectedZoneType.value,
    color: zoneType.color,
    points: [...currentZonePoints]
  };
  
  zones.value.push(newZone);
  currentZonePoints = [];
  currentDrawTool.value = null;
  console.log('添加功能区:', newZone.name);
}

function showZoneList() {
  showZoneListDialog.value = true;
}

function clearAllZones() {
  if (confirm('确定要清空所有功能区吗？')) {
    zones.value = [];
    selectedZone.value = null;
    console.log('清空所有功能区');
  }
}

function deleteZone(zoneId) {
  console.log('开始删除功能区:', zoneId, '当前视图:', currentView.value);
  
  // 从数据中删除
  zones.value = zones.value.filter(z => z.id !== zoneId);
  if (selectedZone.value === zoneId) {
    selectedZone.value = null;
  }
  
  // 从3D场景中删除
  if (threeScene.value && threeScene.value.deleteZone) {
    console.log('调用 threeScene.deleteZone:', zoneId);
    threeScene.value.deleteZone(zoneId);
  } else {
    console.warn('无法删除3D场景中的功能区:', 'threeScene=', !!threeScene.value, 'deleteZone=', !!(threeScene.value && threeScene.value.deleteZone));
  }
  
  console.log('删除功能区完成:', zoneId);
}

function getZoneTypeLabel(type) {
  const zoneType = zoneTypes.find(t => t.value === type);
  return zoneType ? zoneType.label : type;
}

// 生成3D仓库（保留用于兼容，实际逻辑已迁移到autoGenerate3DWarehouse）
async function generate3DWarehouse() {
  if (warehouseShape.value.length < 3) {
    alert('请先完成仓库形状绘制！');
    return;
  }
  
  await autoGenerate3DWarehouse();
}

// 自动生成3D仓库（带加载状态）
async function autoGenerate3DWarehouse() {
  if (warehouseShape.value.length < 3) {
    console.error('仓库形状点数不足，无法生成3D');
    return;
  }
  
  isGenerating3D.value = true;
  console.log('开始自动生成3D仓库...');
  
  try {
    // 等待3D场景准备就绪（最多等待5秒）
    let waitCount = 0;
    while (!threeScene.value && waitCount < 50) {
      await nextTick();
      await new Promise(resolve => setTimeout(resolve, 100));
      waitCount++;
      console.log(`等待3D场景准备... ${waitCount * 100}ms`);
    }
    
    if (!threeScene.value) {
      throw new Error('3D场景初始化超时');
    }
    
    // 调用生成逻辑
    await generate3DWarehouseInternal();

    // 强制渲染刷新（解决v-show切换后的渲染延迟问题）
    setTimeout(() => {
      if (threeScene.value) {
        threeScene.value.forceRender();
        // 触发resize事件模拟F12打开效果
        window.dispatchEvent(new Event('resize'));
      }
    }, 100);

    // 多次触发resize确保渲染
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 300);

    console.log('3D仓库自动生成完成');
  } catch (error) {
    console.error('自动生成3D仓库失败:', error);
    alert('生成3D仓库失败，请重试');
  } finally {
    isGenerating3D.value = false;
  }
}

// 内部生成3D仓库方法（提取自原generate3DWarehouse）
function generate3DWarehouseInternal() {
  return new Promise((resolve, reject) => {
    if (!threeScene.value) {
      reject(new Error('3D场景未准备好'));
      return;
    }
    
    // 转换仓库形状为3D坐标
    const shape3D = warehouseShape.value.map(p => ({
      x: p.x / 10,
      y: warehouseConfig.value.baseHeight,
      z: p.y / 10
    }));
    
    // 构建配置
    const config = {
      height: warehouseConfig.value.height,
      baseHeight: warehouseConfig.value.baseHeight,
      wallThickness: warehouseConfig.value.wallThickness,
      wallOpacity: warehouseConfig.value.wallOpacity
    };
    
    // 生成3D仓库
    threeScene.value.createWarehouseFromShape(warehouseShape.value, config, zones.value, textLabels.value);
    
    is3DGenerated.value = true;
    
    console.log('3D仓库生成完成，轮廓点:', warehouseShape.value.length, '个');
    
    // 如果有待加载的对象，加载它们
    if (window.pendingObjects && window.pendingObjects.length > 0) {
      console.log('加载导入的对象:', window.pendingObjects.length, '个');
      loadImportedObjects(window.pendingObjects);
      window.pendingObjects = null;
    }
    
    // 如果有待加载的对齐线，加载它们
    if (window.pendingAlignmentLines && window.pendingAlignmentLines.length > 0) {
      console.log('加载导入的对齐线:', window.pendingAlignmentLines.length, '条');
      if (threeScene.value) {
        threeScene.value.setAlignmentLines(window.pendingAlignmentLines);
        // 同步对齐线数据到UI
        syncAlignLines();
        console.log('对齐线加载完成');
      }
      window.pendingAlignmentLines = null;
    }
    
    resolve();
  });
}

// 加载导入的对象到3D场景
function loadImportedObjects(objects) {
  if (!threeScene.value) {
    console.error('加载导入对象失败: threeScene未准备好');
    return;
  }

  console.log('开始加载导入的对象:', objects.length, '个');

  objects.forEach((objData, index) => {
    setTimeout(() => {
      // 处理门/窗对象
      if (objData.type === 'door' || objData.type === 'window') {
        console.log(`加载${objData.type === 'door' ? '门' : '窗'} ${index + 1}/${objects.length}:`, `墙体${objData.wallIndex}`);

        const config = {
          width: objData.width / 100, // cm -> m
          height: objData.height / 100 // cm -> m
        };
        if (objData.type === 'window' && objData.sillHeight) {
          config.sillHeight = objData.sillHeight / 100; // cm -> m
        }

        let placedObject;
        // 获取墙体类型，支持办公区墙体
        const wallType = objData.wallType || 'wall';
        if (objData.type === 'door') {
          placedObject = threeScene.value.createDoor(objData.wallIndex, objData.wallPosition / 100, config, wallType);
        } else {
          placedObject = threeScene.value.createWindow(objData.wallIndex, objData.wallPosition / 100, config, wallType);
        }

        if (placedObject) {
          console.log(`${objData.type === 'door' ? '门' : '窗'}加载成功`);
        } else {
          console.error(`${objData.type === 'door' ? '门' : '窗'}加载失败`);
        }
        return;
      }

      // 处理普通模型对象
      const modelType = objData.modelType || objData.modelName;

      console.log(`加载对象 ${index + 1}/${objects.length}:`, modelType);

      // 使用ThreeScene的addModelInternal方法添加对象
      const placedObject = threeScene.value.addModelInternal(modelType, objData.position);

      if (placedObject) {
        // 设置旋转
        placedObject.rotation.x = objData.rotation.x;
        placedObject.rotation.y = objData.rotation.y;
        placedObject.rotation.z = objData.rotation.z;

        // 设置缩放
        if (objData.scale) {
          placedObject.scale.set(objData.scale.x, objData.scale.y, objData.scale.z);
        }

        // 恢复中文名称（如果存在）
        if (objData.name) {
          placedObject.userData.name = objData.name;
        }

        console.log('加载对象成功:', modelType);
      } else {
        console.error('加载对象失败:', modelType);
      }
    }, index * 100); // 逐个加载，避免同时加载过多
  });
}

// 切换到3D视图
function switchTo3D() {
  if (!is3DGenerated.value) {
    alert('请先生成3D仓库！');
    return;
  }
  currentView.value = '3d';
  console.log('切换到3D视图');
}

// 开始添加门
function startAddDoor() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  isAddingDoor.value = !isAddingDoor.value;
  isAddingWindow.value = false;
  console.log(isAddingDoor.value ? '开始添加门，请点击墙体' : '取消添加门');
}

// 开始添加窗
function startAddWindow() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  isAddingWindow.value = !isAddingWindow.value;
  isAddingDoor.value = false;
  console.log(isAddingWindow.value ? '开始添加窗，请点击墙体' : '取消添加窗');
}

// 在3D场景中添加门
function addDoorToWall(wallIndex, position) {
  if (!threeScene.value) return;
  
  const door = threeScene.value.createDoor(wallIndex, position, doorConfig.value);
  if (door) {
    console.log('门添加成功');
    isAddingDoor.value = false;
  }
}

// 在3D场景中添加窗
function addWindowToWall(wallIndex, position) {
  if (!threeScene.value) return;
  
  const window = threeScene.value.createWindow(wallIndex, position, windowConfig.value);
  if (window) {
    console.log('窗添加成功');
    isAddingWindow.value = false;
  }
}

// 添加货架
function addShelf() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    threeScene.value.addModel('shelf');
  }
}

// 添加传送带
function addConveyor() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    threeScene.value.addModel('conveyor');
  }
}

// 项目操作
function saveProject() {
  showSaveDialog.value = true;
  // 如果已有项目名称，保留；否则清空
  if (!projectName.value) {
    projectName.value = '';
  }
}

// 传统下载方式（用于不支持 File System Access API 的浏览器）
function downloadWithTraditionalMethod(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// 从功能区规划页面保存项目
function saveProjectFromZone() {
  if (isProjectSaved.value && projectName.value) {
    // 已有项目名称，直接保存
    confirmSaveProject();
  } else {
    // 新项目，显示弹窗输入名称
    showSaveDialog.value = true;
    projectName.value = '';
  }
}

// 计算仓库面积（使用多边形面积公式）
function calculateWarehouseArea() {
  if (warehouseShape.value.length < 3) return 0;
  
  let area = 0;
  const points = warehouseShape.value;
  const n = points.length;
  
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    area += points[i].x * points[j].y;
    area -= points[j].x * points[i].y;
  }
  
  area = Math.abs(area) / 2;
  
  // 转换单位：像素 -> 平方米 (1像素 = 0.1米 = 10cm)
  const scaleFactor = 0.1; // 1像素 = 0.1米
  return Math.round(area * scaleFactor * scaleFactor);
}

// 导入项目
function importProject() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const project = JSON.parse(e.target.result);
          // 加载项目数据
          if (project.warehouseShape) {
            warehouseShape.value = project.warehouseShape;
          }
          if (project.zones) {
            zones.value = project.zones;
          }
          if (project.warehouseConfig) {
            warehouseConfig.value = { ...warehouseConfig.value, ...project.warehouseConfig };
          }
          if (project.textLabels) {
            textLabels.value = project.textLabels;
          }
          
          // 保存对象数据，在生成3D仓库后加载
          if (project.objects && project.objects.length > 0) {
            // 存储对象数据，等待3D场景初始化后加载
            window.pendingObjects = project.objects;
            console.log('导入对象数据:', project.objects.length, '个对象待加载');
            const doorWindowInImport = project.objects.filter(obj => obj.type === 'door' || obj.type === 'window');
            console.log('导入数据门/窗数量:', doorWindowInImport.length, '个');
          }
          
          // 保存对齐线数据，在生成3D仓库后加载
          if (project.alignmentLines && project.alignmentLines.length > 0) {
            // 存储对齐线数据，等待3D场景初始化后加载
            window.pendingAlignmentLines = project.alignmentLines;
            console.log('导入对齐线数据:', project.alignmentLines.length, '条对齐线待加载');
          }
          
          isProjectSaved.value = true;
          projectName.value = file.name.replace('.json', '');
          
          // 导入项目时不标记is3DGenerated，让切换步骤时重新生成3D仓库
          // 这样可以确保3D仓库正确加载
          
          console.log('导入项目:', project);
        } catch (error) {
          console.error('导入项目失败:', error);
          alert('导入项目失败！请检查文件格式。');
        }
      };
      reader.readAsText(file);
    }
  };
  input.click();
}

async function confirmSaveProject() {
  if (!projectName.value.trim()) {
    alert('请输入项目名称！');
    return;
  }

  // 保存时退出编辑模式
  if (isZoneEditMode.value) {
    exitZoneEditMode();
  }

  // 从3D场景获取所有物流对象
  let sceneObjectsData = [];
  console.log('保存项目 - 当前视图:', currentView.value, '3D已生成:', is3DGenerated.value, 'threeScene:', !!threeScene.value);
  
  if (threeScene.value && is3DGenerated.value) {
    const sceneObjects = threeScene.value.getSceneObjects();
    console.log('获取到场景对象:', sceneObjects.length, '个');
    sceneObjectsData = sceneObjects
      .filter(obj => obj.userData.modelType || obj.userData.modelName ||
                     obj.userData.type === 'door' || obj.userData.type === 'window') // 保存模型对象和门/窗
      .map(obj => {
        const baseData = {
          modelType: obj.userData.modelType || obj.userData.modelName,
          modelName: obj.userData.modelName,
          name: obj.userData.name, // 中文名称
          position: {
            x: obj.position.x,
            y: obj.position.y,
            z: obj.position.z
          },
          rotation: {
            x: obj.rotation.x,
            y: obj.rotation.y,
            z: obj.rotation.z
          },
          scale: {
            x: obj.scale.x,
            y: obj.scale.y,
            z: obj.scale.z
          }
        };
        // 门/窗对象保存额外属性
        if (obj.userData.type === 'door' || obj.userData.type === 'window') {
          baseData.type = obj.userData.type;
          baseData.wallType = obj.userData.wallType || 'wall'; // 保存墙体类型，支持办公区墙体
          baseData.wallIndex = obj.userData.wallIndex;
          baseData.wallPosition = obj.userData.position;
          baseData.width = obj.userData.width;
          baseData.height = obj.userData.height;
          if (obj.userData.type === 'window') {
            baseData.sillHeight = obj.userData.sillHeight;
          }
        }
        return baseData;
      });
    console.log('保存场景对象:', sceneObjectsData.length, '个');
  } else {
    console.warn('3D场景未准备好，无法保存对象。当前视图:', currentView.value, 'is3DGenerated:', is3DGenerated.value);
  }

  // 从3D场景获取对齐线数据
  let alignmentLinesData = [];
  if (threeScene.value && is3DGenerated.value) {
    alignmentLinesData = threeScene.value.getAlignmentLines();
    console.log('保存对齐线数据:', alignmentLinesData.length, '条对齐线');
  }

  // 构建项目数据
  const projectData = {
    version: '1.0',
    timestamp: new Date().toISOString(),
    projectName: projectName.value,
    warehouseShape: warehouseShape.value,
    zones: zones.value,
    warehouseConfig: warehouseConfig.value,
    textLabels: textLabels.value,
    objects: sceneObjectsData, // 保存3D场景中的对象
    alignmentLines: alignmentLinesData // 保存对齐线数据
  };
  
  console.log('项目数据对象数量:', projectData.objects.length, '个');
  const doorWindowInProject = projectData.objects.filter(obj => obj.type === 'door' || obj.type === 'window');
  console.log('项目数据门/窗数量:', doorWindowInProject.length, '个');

  // 导出JSON文件
  const projectJson = JSON.stringify(projectData, null, 2);
  const blob = new Blob([projectJson], { type: 'application/json' });
  
  // 尝试使用 File System Access API 支持覆盖保存
  if ('showSaveFilePicker' in window) {
    try {
      const fileHandle = await window.showSaveFilePicker({
        suggestedName: `${projectName.value}.json`,
        types: [{
          description: 'JSON文件',
          accept: { 'application/json': ['.json'] }
        }]
      });
      const writable = await fileHandle.createWritable();
      await writable.write(blob);
      await writable.close();
    } catch (err) {
      // 用户取消或API失败，回退到传统下载方式
      if (err.name !== 'AbortError') {
        console.log('File System Access API 失败，使用传统下载方式:', err);
        downloadWithTraditionalMethod(blob, projectName.value);
      } else {
        // 用户取消，不执行保存
        return;
      }
    }
  } else {
    // 浏览器不支持 File System Access API，使用传统下载方式
    downloadWithTraditionalMethod(blob, projectName.value);
  }

  isProjectSaved.value = true;
  showSaveDialog.value = false;
  console.log('保存项目:', projectName.value);
}

function generateReport() {
  if (!isProjectSaved.value) {
    alert('请先保存项目！');
    return;
  }
  alert('项目报告生成中...');
  console.log('生成项目报告');
}

function exportImage() {
  if (currentView.value === '3d' && threeScene.value) {
    threeScene.value.exportImage();
  } else {
    alert('请在3D视图下导出效果图！');
  }
}

function exportReport() {
  if (warehouseShape.value.length < 3) {
    alert('请先创建仓库！');
    return;
  }
  alert('项目报告导出中...');
  console.log('导出项目报告');
}

function closeProject() {
  if (confirm('确定要关闭当前项目吗？未保存的更改将丢失。')) {
    // 重置所有状态
    warehouseShape.value = [];
    zones.value = [];
    textLabels.value = [];
    projectName.value = '';
    selectedObject.value = null;
    is3DGenerated.value = false;
    currentStep.value = 'create-warehouse';
    expandedStep.value = 'create-warehouse';
    currentView.value = '2d';
    
    // 清空3D场景
    if (threeScene.value) {
      threeScene.value.clearScene();
    }
    
    // 清除localStorage中的自定义对象
    localStorage.removeItem('customShelves');
    localStorage.removeItem('customWalls');
    
    console.log('项目已关闭，状态已重置');
  }
}

// 返回产品使用页
function goToUsage() {
  router.push('/usage');
}

// 设置选择模式
function setSelectMode() {
  // 如果当前在测量模式，先停止测量
  if (isMeasuring.value && threeScene.value) {
    threeScene.value.stopMeasuring();
  }
  // 如果当前在对齐线绘制模式，先停止绘制
  if (isAlignLineMode.value && threeScene.value) {
    threeScene.value.stopDrawingAlignmentLine();
  }
  
  isAddingText.value = false;
  isMeasuring.value = false;
  isAlignLineMode.value = false;
  console.log('切换到选择模式');
}

// 开始测量
function startMeasure() {
  // 如果当前在对齐线绘制模式，先停止绘制（确保模式互斥）
  if (isAlignLineMode.value && threeScene.value) {
    threeScene.value.stopDrawingAlignmentLine();
    console.log('退出对齐线绘制模式，准备进入测量模式');
  }
  
  isMeasuring.value = !isMeasuring.value;
  isAddingText.value = false;
  isAlignLineMode.value = false;
  
  if (isMeasuring.value) {
    // 进入测量模式
    if (threeScene.value) {
      threeScene.value.startMeasuring();
      console.log('进入测量模式');
    }
  } else {
    // 退出测量模式，自动切换到选择模式
    if (threeScene.value) {
      threeScene.value.stopMeasuring();
      console.log('退出测量模式，切换到选择模式');
    }
  }
}

// 添加对齐线
function addAlignLine() {
  // 如果当前在测量模式，先停止测量（确保模式互斥）
  if (isMeasuring.value && threeScene.value) {
    threeScene.value.stopMeasuring();
    console.log('退出测量模式，准备进入对齐线绘制模式');
  }
  
  isAlignLineMode.value = !isAlignLineMode.value;
  isAddingText.value = false;
  isMeasuring.value = false;
  
  if (isAlignLineMode.value) {
    // 开始绘制对齐线
    if (threeScene.value) {
      threeScene.value.startDrawingAlignmentLine();
      console.log('进入对齐线绘制模式');
    }
  } else {
    // 结束绘制对齐线，自动切换到选择模式
    if (threeScene.value) {
      threeScene.value.stopDrawingAlignmentLine();
      console.log('退出对齐线绘制模式，切换到选择模式');
    }
    // 自动切换到选择模式
    setSelectMode();
  }
}

// 选中对齐线（高亮显示）
function selectAlignLine(lineId) {
  if (selectedAlignmentLineId.value === lineId) {
    // 如果已选中，则取消选中
    selectedAlignmentLineId.value = null;
    if (threeScene.value) {
      threeScene.value.highlightAlignmentLine(null);
    }
    console.log('取消选中对齐线');
  } else {
    // 选中新的对齐线
    selectedAlignmentLineId.value = lineId;
    if (threeScene.value) {
      threeScene.value.highlightAlignmentLine(lineId);
    }
    console.log('选中对齐线:', lineId);
  }
}

// 删除单条对齐线
function deleteAlignLine(index) {
  if (alignLines.value[index]) {
    const lineId = alignLines.value[index].id;
    if (threeScene.value) {
      const success = threeScene.value.removeAlignmentLine(lineId);
      if (success) {
        alignLines.value.splice(index, 1);
        // 如果删除的是当前选中的对齐线，清除选中状态
        if (selectedAlignmentLineId.value === lineId) {
          selectedAlignmentLineId.value = null;
        }
        console.log('删除对齐线:', lineId);
      }
    }
  }
}

// 清空所有对齐线
function clearAllAlignLines() {
  if (alignLines.value.length === 0) {
    alert('暂无对齐线');
    return;
  }
  if (confirm(`确定要清空全部 ${alignLines.value.length} 条对齐线吗？`)) {
    if (threeScene.value) {
      threeScene.value.clearAlignmentLines();
      alignLines.value = [];
      console.log('清空所有对齐线');
    }
  }
}

// 同步对齐线数据
function syncAlignLines() {
  if (threeScene.value) {
    const lines = threeScene.value.getAllAlignmentLines();
    alignLines.value = lines;
    console.log('同步对齐线数据:', lines.length, '条');
  }
}

// 处理对齐线更新事件
function handleAlignmentLinesUpdated(lines) {
  alignLines.value = lines;
  console.log('对齐线数据已更新:', lines.length, '条');
}

// 打开自定义货架页面（P2）
function openCustomShelf() {
  // 在新标签页打开P2页面
  window.open('/models', '_blank');
  console.log('打开自定义货架页面');
}

// 格式化位置显示
function formatPosition(value) {
  if (value === undefined || value === null) return '0.00';
  return (value / 10).toFixed(2); // 转换为米
}

// 格式化旋转角度显示
function formatRotation(rotation) {
  if (!rotation) return '0';
  // 将弧度转换为角度
  const degrees = Math.round((rotation * 180 / Math.PI) % 360);
  return degrees < 0 ? degrees + 360 : degrees;
}

// 获取选中功能区的名称
function getSelectedZoneName() {
  if (!selectedZone.value) return '';
  const zone = zones.value.find(z => z.id === selectedZone.value);
  return zone ? zone.name : '';
}

// 获取选中功能区的面积信息
function getSelectedZoneArea() {
  if (!selectedZone.value) return '';
  const zone = zones.value.find(z => z.id === selectedZone.value);
  if (!zone) return '';
  // 将像素转换为米（假设100像素 = 10米）
  const widthM = (zone.width / 100 * 10).toFixed(1);
  const heightM = (zone.height / 100 * 10).toFixed(1);
  const area = (widthM * heightM).toFixed(1);
  return `${widthM}米×${heightM}米=${area}平方米`;
}

// 获取选中文字标注的内容
function getSelectedTextLabelContent() {
  const label = textLabels.value.find(l => l.id === selectedTextLabel.value);
  return label ? label.content : '';
}

// 获取选中文字标注的字体大小
function getSelectedTextLabelFontSize() {
  const label = textLabels.value.find(l => l.id === selectedTextLabel.value);
  return label ? label.fontSize : 0;
}

// 获取选中文字标注的X坐标
function getSelectedTextLabelX() {
  const label = textLabels.value.find(l => l.id === selectedTextLabel.value);
  return label ? Math.round(label.x) : 0;
}

// 获取选中文字标注的Y坐标
function getSelectedTextLabelY() {
  const label = textLabels.value.find(l => l.id === selectedTextLabel.value);
  return label ? Math.round(label.y) : 0;
}

// 编辑选中的文字标注（通过按钮）
function editSelectedTextLabel() {
  if (!selectedTextLabel.value) {
    alert('请先选中要编辑的文字标注！');
    return;
  }
  editTextLabel(selectedTextLabel.value);
}

// 删除选中的文字标注
function deleteSelectedTextLabel() {
  if (!selectedTextLabel.value) {
    alert('请先选中要删除的文字标注！');
    return;
  }
  if (confirm('确定要删除这个文字标注吗？')) {
    const index = textLabels.value.findIndex(l => l.id === selectedTextLabel.value);
    if (index !== -1) {
      textLabels.value.splice(index, 1);
      selectedTextLabel.value = null;
      console.log('删除文字标注');
    }
  }
}

// 批量放置功能
function setBatchDirection(direction) {
  batchDirection.value = direction;
  console.log('批量放置方向:', direction);
}

function startBatchPlace() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  isBatchPlacing.value = true;
  console.log('开始批量放置模式');
  if (threeScene.value) {
    threeScene.value.enableBatchPlaceMode(batchCount.value, batchSpacing.value, batchDirection.value);
  }
}

function onBatchPlaceCompleted() {
  isBatchPlacing.value = false;
  console.log('批量放置完成');
}

// 对象操作
function moveSelectedObject() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    threeScene.value.moveObject(true);
  }
}

function toggleRotateMode() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (!selectedObject.value) {
    alert('请先选中要旋转的对象！');
    return;
  }
  // 打开精确旋转角度输入对话框
  openRotationDialog();
}

// 打开旋转角度输入对话框
function openRotationDialog() {
  if (!selectedObject.value) return;
  
  // 获取当前对象的旋转角度（转换为度数）
  const currentRotation = selectedObject.value.rotationY || 0;
  rotationAngle.value = Math.round(currentRotation * 180 / Math.PI);
  rotationOriginalAngle.value = rotationAngle.value;
  isRotationPreview.value = false;
  showRotationDialog.value = true;
  
  console.log('打开旋转对话框，当前角度:', rotationAngle.value);
}

// 关闭旋转对话框
function closeRotationDialog() {
  showRotationDialog.value = false;
  rotationAngle.value = 0;
  rotationOriginalAngle.value = 0;
  isRotationPreview.value = false;
}

// 旋转角度输入变化时实时预览
function onRotationAngleChange() {
  if (!threeScene.value || !selectedObject.value) return;
  
  isRotationPreview.value = true;
  // 将角度转换为弧度，顺时针为正
  const angleRad = rotationAngle.value * Math.PI / 180;
  threeScene.value.previewRotation(angleRad);
}

// 确认旋转角度
function confirmRotation() {
  if (!threeScene.value || !selectedObject.value) return;
  
  // 应用旋转
  const angleRad = rotationAngle.value * Math.PI / 180;
  threeScene.value.applyRotation(angleRad);
  
  console.log('确认旋转角度:', rotationAngle.value);
  closeRotationDialog();
}

// 取消旋转
function cancelRotation() {
  if (!threeScene.value || !selectedObject.value) return;
  
  // 恢复原始角度
  if (isRotationPreview.value) {
    const originalRad = rotationOriginalAngle.value * Math.PI / 180;
    threeScene.value.applyRotation(originalRad);
  }
  
  console.log('取消旋转，恢复原角度:', rotationOriginalAngle.value);
  closeRotationDialog();
}

function deleteSelectedObject() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    threeScene.value.deleteSelectedObjects();
    selectedObject.value = null;
  }
}

// 复制选中对象
function copySelectedObject() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value && selectedObject.value) {
    const copiedObject = threeScene.value.copySelectedObject();
    if (copiedObject) {
      selectedObject.value = copiedObject;
      console.log('对象已复制');
    }
  }
}

// NO2功能区操作
// selectedZone 已在第1018行定义
// selectedTextLabel 已在第1029行定义

// 删除选中功能区
function deleteSelectedZone() {
  if (!selectedZone.value) {
    alert('请先选中要删除的功能区！');
    return;
  }
  if (confirm('确定要删除选中的功能区吗？')) {
    // selectedZone.value 存储的是 zoneId 字符串
    const zoneId = selectedZone.value;
    const index = zones.value.findIndex(z => z.id === zoneId);
    if (index > -1) {
      zones.value.splice(index, 1);
      selectedZone.value = null;
      
      // 从3D场景中删除
      if (threeScene.value && threeScene.value.deleteZone) {
        threeScene.value.deleteZone(zoneId);
      }
      
      console.log('功能区已删除:', zoneId);
    }
  }
}

// 编辑选中的功能区 - 打开精确尺寸编辑对话框
function editSelectedZone() {
  if (!selectedZone.value) {
    alert('请先选中要编辑的功能区！');
    return;
  }
  
  // 打开精确尺寸编辑对话框
  zoneEditWidth.value = 0;
  zoneEditHeight.value = 0;
  showZoneSizeDialog.value = true;
  
  // 自动聚焦长度输入框
  setTimeout(() => {
    const input = document.querySelector('.zone-size-dialog input[name="width"]');
    if (input) {
      input.focus();
    }
  }, 100);
  
  console.log('打开功能区精确尺寸编辑对话框:', selectedZone.value);
}

// 确认功能区尺寸编辑
function confirmZoneSizeEdit() {
  if (!selectedZone.value) return;
  
  const zone = zones.value.find(z => z.id === selectedZone.value);
  if (!zone) return;
  
  // 将米转换为像素（1米 = 10像素）
  const newWidth = zoneEditWidth.value * 10;
  const newHeight = zoneEditHeight.value * 10;
  
  if (newWidth <= 0 || newHeight <= 0) {
    alert('请输入有效的尺寸（大于0）');
    return;
  }
  
  // 保持中心点不变，调整尺寸
  const centerX = zone.x + zone.width / 2;
  const centerY = zone.y + zone.height / 2;
  
  zone.width = newWidth;
  zone.height = newHeight;
  zone.x = centerX - newWidth / 2;
  zone.y = centerY - newHeight / 2;
  
  console.log('功能区尺寸已更新:', zone.width / 10, 'm x', zone.height / 10, 'm');
  
  // 关闭对话框
  showZoneSizeDialog.value = false;
  zoneEditWidth.value = 0;
  zoneEditHeight.value = 0;
}

// 取消功能区尺寸编辑
function cancelZoneSizeEdit() {
  showZoneSizeDialog.value = false;
  zoneEditWidth.value = 0;
  zoneEditHeight.value = 0;
  console.log('取消功能区尺寸编辑');
}

// 编辑选中的文字标注
function editSelectedText() {
  if (!selectedTextLabel.value) {
    alert('请先选中要编辑的文字标注！');
    return;
  }
  const newText = prompt('编辑文字:', selectedTextLabel.value.text);
  if (newText !== null) {
    selectedTextLabel.value.text = newText;
    console.log('文字已编辑:', newText);
  }
}

// 删除选中的文字标注
function deleteSelectedText() {
  if (!selectedTextLabel.value) {
    alert('请先选中要删除的文字标注！');
    return;
  }
  if (confirm('确定要删除选中的文字标注吗？')) {
    const index = textLabels.value.findIndex(t => t.id === selectedTextLabel.value.id);
    if (index > -1) {
      textLabels.value.splice(index, 1);
      selectedTextLabel.value = null;
      console.log('文字标注已删除');
    }
  }
}

// 批量复制功能
function startBatchPreview() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (!selectedObject.value) {
    alert('请先选中要复制的对象！');
    return;
  }
  isBatchPreview.value = true;
  console.log('开始批量复制预览:', batchRows.value, '行', batchCols.value, '列');
  console.log('方向设置 - 行:', batchRowDirection.value, '列:', batchColDirection.value);
  if (threeScene.value) {
    threeScene.value.startBatchPreview({
      rows: batchRows.value,
      cols: batchCols.value,
      rowSpacing: batchRowSpacing.value,
      colSpacing: batchColSpacing.value,
      rotation: batchRotation.value,
      rowDirection: batchRowDirection.value,
      colDirection: batchColDirection.value
    });
  }
}

function confirmBatchPlace() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  console.log('confirmBatchPlace 被调用, isBatchPreview:', isBatchPreview.value);
  if (threeScene.value) {
    threeScene.value.confirmBatchPlace();
    isBatchPreview.value = false;
    console.log('批量复制完成, isBatchPreview 设置为:', isBatchPreview.value);
  }
}

function cancelBatchPreview() {
  console.log('cancelBatchPreview 被调用, isBatchPreview:', isBatchPreview.value, 'selectedObject:', !!selectedObject.value);
  if (threeScene.value) {
    threeScene.value.cancelBatchPreview();
  }
  isBatchPreview.value = false;
  console.log('取消批量复制预览, isBatchPreview 设置为:', isBatchPreview.value);
}

// 对齐工具
function alignObjects(alignType) {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    threeScene.value.alignObjects(alignType);
    console.log('对齐对象:', alignType);
  }
}

function distributeObjects(distributeType) {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    threeScene.value.distributeObjects(distributeType);
    console.log('等距分布:', distributeType);
  }
}

// 场景操作
function saveLayout() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (threeScene.value) {
    const layout = threeScene.value.saveLayout();
    const layoutJson = JSON.stringify(layout, null, 2);
    const blob = new Blob([layoutJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const projectName = prompt('请输入布局名称:', '仓库布局');
    a.download = projectName ? `${projectName}.json` : 'warehouse-layout.json';
    a.click();
    URL.revokeObjectURL(url);
  }
}

function loadLayout() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const layout = JSON.parse(e.target.result);
          if (threeScene.value) {
            threeScene.value.loadLayout(layout);
          }
        } catch (error) {
          console.error('加载布局失败:', error);
          alert('加载布局失败！');
        }
      };
      reader.readAsText(file);
    }
  };
  input.click();
}

function clearScene() {
  if (currentView.value !== '3d') {
    alert('请先切换到3D视图！');
    return;
  }
  if (confirm('确定要清空场景中的所有对象吗？')) {
    if (threeScene.value) {
      threeScene.value.clearScene();
    }
  }
}

// 模型操作
function onDragStart(event, modelName) {
  event.dataTransfer.setData('modelName', modelName);
  event.dataTransfer.effectAllowed = 'copy';
  console.log('开始拖动模型:', modelName);
}

// 自定义模型拖拽（使用 modelUrl 提取模型ID）
function onCustomModelDragStart(event, model) {
  // 从 modelUrl 提取模型ID（如 /assets/models/shelf-beam-medium.glb -> shelf-beam-medium）
  let modelIdentifier = model.id;
  if (model.modelUrl) {
    const match = model.modelUrl.match(/\/([^\/]+)\.glb$/);
    if (match) {
      modelIdentifier = match[1];
    }
  }
  event.dataTransfer.setData('modelName', modelIdentifier);
  event.dataTransfer.setData('isCustomModel', 'true');
  event.dataTransfer.setData('customModelId', model.id);
  event.dataTransfer.effectAllowed = 'copy';
  console.log('开始拖动自定义模型:', model.name, 'ID:', modelIdentifier);
}

// 创建拖拽预览图像
function createDragPreview(width, height, color, type) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // 设置画布大小
  const scale = 20; // 缩放比例
  canvas.width = width * scale;
  canvas.height = height * scale;
  
  // 绘制背景
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // 绘制边框
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 2;
  ctx.strokeRect(0, 0, canvas.width, canvas.height);
  
  // 绘制文字
  ctx.fillStyle = '#fff';
  ctx.font = 'bold 12px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(type, canvas.width / 2, canvas.height / 2);
  
  return canvas;
}

// 门拖拽开始
function onDoorDragStart(event) {
  event.dataTransfer.setData('objectType', 'door');
  event.dataTransfer.setData('doorWidth', doorConfig.value.width);
  event.dataTransfer.setData('doorHeight', doorConfig.value.height);
  event.dataTransfer.effectAllowed = 'copy';
  
  // 设置自定义拖拽图像
  const preview = createDragPreview(4, 3, '#8B4513', '🚪');
  event.dataTransfer.setDragImage(preview, 40, 30);
  
  console.log('开始拖动门');
}

// 提升门拖拽开始
function onLiftDoorDragStart(event) {
  event.dataTransfer.setData('objectType', 'liftDoor');
  event.dataTransfer.setData('doorWidth', liftDoorConfig.value.width);
  event.dataTransfer.setData('doorHeight', liftDoorConfig.value.height);
  event.dataTransfer.effectAllowed = 'copy';

  // 设置自定义拖拽图像（更大一些体现提升门）
  const preview = createDragPreview(5, 4, '#654321', '🚪');
  event.dataTransfer.setDragImage(preview, 50, 40);

  console.log('开始拖动提升门');
}

// 提升门(2.7x3.0m)拖拽开始
function onLiftDoor27DragStart(event) {
  event.dataTransfer.setData('objectType', 'liftDoor27');
  event.dataTransfer.setData('doorWidth', liftDoor27Config.value.width);
  event.dataTransfer.setData('doorHeight', liftDoor27Config.value.height);
  event.dataTransfer.effectAllowed = 'copy';

  // 设置自定义拖拽图像
  const preview = createDragPreview(4, 3.5, '#654321', '🚪');
  event.dataTransfer.setDragImage(preview, 40, 35);

  console.log('开始拖动提升门(2.7x3.0m)');
}

// 窗拖拽开始
function onWindowDragStart(event) {
  event.dataTransfer.setData('objectType', 'window');
  event.dataTransfer.setData('windowWidth', windowConfig.value.width);
  event.dataTransfer.setData('windowHeight', windowConfig.value.height);
  event.dataTransfer.setData('windowSillHeight', windowConfig.value.sillHeight);
  event.dataTransfer.effectAllowed = 'copy';
  
  // 设置自定义拖拽图像
  const preview = createDragPreview(3, 2.5, '#87CEEB', '🪟');
  event.dataTransfer.setDragImage(preview, 30, 25);
  
  console.log('开始拖动窗');
}

// 立柱拖拽开始
function onPillarDragStart(event) {
  event.dataTransfer.setData('objectType', 'pillar');
  event.dataTransfer.effectAllowed = 'copy';

  // 设置自定义拖拽图像
  const preview = createDragPreview(2, 3, '#888888', '🏛️');
  event.dataTransfer.setDragImage(preview, 20, 30);

  console.log('开始拖动立柱');
}

function onModelAdded(model) {
  console.log('模型添加成功:', model);
}

function onObjectSelected(object) {
  selectedObject.value = object;
  console.log('对象选中:', object);
}

function onObjectDeselected() {
  // 使用统一清空函数，确保所有选中状态都被清空
  clearAllSelection();
}

// 处理3D视图中功能区选中事件
function onZoneSelectedIn3D(zoneId) {
  // 在3D视图中选中功能区时，设置selectedZone并清空selectedObject
  selectedZone.value = zoneId;
  selectedObject.value = null;
  console.log('3D视图选中功能区:', zoneId);
}

// 处理添加门事件
function onAddDoor(wallIndex, position) {
  console.log('添加门到墙体:', wallIndex, '位置:', position);
  addDoorToWall(wallIndex, position);
}

// 处理添加窗事件
function onAddWindow(wallIndex, position) {
  console.log('添加窗到墙体:', wallIndex, '位置:', position);
  addWindowToWall(wallIndex, position);
}

function toggleCategory(category) {
  expandedCategories.value[category] = !expandedCategories.value[category];
}

// 组件挂载时加载我的模型
onMounted(() => {
  loadMyModels();
});

// 暴露给模板使用的变量和函数
defineExpose({
  isEditMode,
  enterEditMode,
  toggleEditMode,
  onLineClick,
  handleLineClick,
  editLine,
  isZoneCreateMode,
  isZoneEditMode,
  enterZoneCreateMode,
  toggleZoneEditMode,
  onZoneDragStart,
  onZoneDrop,
  onZoneClick,
  findClickedZone,
  isPointInPolygon,
  expandedStep,
  toggleStepMenu,
  canvasScale,
  canvasOffset,
  resetCanvasView,
  onCanvasWheel,
  onCanvasMouseDown,
  onCanvasMouseMove,
  onCanvasMouseUp,
  isResizingZone,
  resizeHandle,
  onZoneResizeStart,
  onZoneResizeMove,
  onZoneResizeEnd,
  onZoneDoubleClick,
  updateZonePoints,
  exitZoneEditMode,
  toggleZoneEditMode,
  isMovingZone,
  onZoneMoveStart,
  onZoneMove,
  onZoneMoveEnd,
  onZoneMouseMove,
  onZoneMouseUp,
  showQuickRectDialog,
  generateQuickRectWarehouse,
  cancelQuickRectWarehouse,
  showQuickRectWarehouseDialog,
  quickRectWidth,
  quickRectHeight,
  getZoneDimensions,
  textLabels,
  isAddingText,
  showTextInputDialog,
  textInputContent,
  textInputSize,
  startAddText,
  addTextLabel,
  confirmAddText,
  cancelAddText,
  editTextLabel,
  confirmEditText,
  deleteTextLabel,
  onTextLabelDragStart,
  isAddingDoor,
  isAddingWindow,
  doorConfig,
  windowConfig,
  startAddDoor,
  startAddWindow,
  addDoorToWall,
  addWindowToWall,
  onAddDoor,
  onAddWindow,
  switchTo3D,
  addShelf,
  addConveyor,
  onDoorDragStart,
  onLiftDoorDragStart,
  onLiftDoor27DragStart,
  onPillarDragStart,
  onWindowDragStart,
  createDragPreview,
  expandedObjectCategories,
  toggleObjectCategory,
  batchCount,
  batchSpacing,
  batchDirection,
  isBatchPlacing,
  isRotating,
  setBatchDirection,
  startBatchPlace,
  onBatchPlaceCompleted,
  moveSelectedObject,
  toggleRotateMode,
  deleteSelectedObject,
  copySelectedObject,
  saveLayout,
  loadLayout,
  clearScene,
  importProject,
  selectedZone,
  selectedTextLabel,
  deleteZone,
  deleteSelectedZone,
  editSelectedText,
  deleteSelectedText,
  batchRows,
  batchCols,
  batchRowSpacing,
  batchColSpacing,
  batchRotation,
  isBatchPreview,
  startBatchPreview,
  confirmBatchPlace,
  cancelBatchPreview,
  alignObjects,
  distributeObjects,
  saveProjectFromZone,
  calculateWarehouseArea,
  myModels,
  loadMyModels,
  onCustomModelDragStart
});
</script>

<style scoped>
.core-function {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

/* 顶部项目栏 */
.top-project-bar {
  background: #fff;
  border-bottom: 1px solid #ddd;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  height: 48px;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.top-bar-center {
  flex: 1;
  text-align: center;
  min-width: 0;
  padding: 0 16px;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* 顶部栏分隔线 */
.top-bar-divider {
  width: 1px;
  height: 20px;
  background: #ddd;
  margin: 0 4px;
}

/* 面板切换按钮 */
.panel-toggle-btn {
  background: #f5f5f5;
  border-color: #ccc;
  font-size: 12px;
}

.panel-toggle-btn:hover {
  background: #e0e0e0;
}

.top-bar-btn.home-btn {
  background: #e3f2fd;
  border-color: #4fc3f7;
  color: #0288d1;
}

.top-bar-btn.home-btn:hover {
  background: #4fc3f7;
  color: white;
}

.view-toggle {
  display: flex;
  gap: 4px;
  background: #f0f0f0;
  padding: 2px;
  border-radius: 4px;
}

.view-toggle button {
  padding: 4px 12px;
  border: none;
  border-radius: 3px;
  background: transparent;
  color: #666;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggle button.active {
  background: #4fc3f7;
  color: white;
}

.view-toggle button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

/* 顶部栏左侧按钮间距调整 */
.top-bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-bar-btn {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  flex-shrink: 0;
}

.top-bar-btn:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.top-bar-btn.active {
  background: #ffebee;
  border-color: #ff0000;
  color: #ff0000;
  box-shadow: 0 0 8px rgba(255, 0, 0, 0.3);
  font-weight: bold;
}

.top-bar-btn:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  border-color: #ddd;
}

.top-bar-btn.close-btn:hover {
  background: #ffebee;
  border-color: #f44336;
  color: #f44336;
}

/* 图标按钮（简化显示的面板切换按钮） */
.top-bar-btn.icon-btn {
  padding: 4px 6px;
  font-size: 14px;
}

/* 禁用按钮样式 */
.top-bar-btn.disabled-btn {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
  border-color: #ddd;
  opacity: 0.7;
}

.top-bar-btn.disabled-btn:hover {
  background: #f5f5f5;
  border-color: #ddd;
  color: #999;
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

.top-toolbar button.active {
  background: #4fc3f7;
  color: white;
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
  width: 280px;
  background: #f9f9f9;
  padding: 12px;
  overflow: hidden;
  border-right: 1px solid #ddd;
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease, padding 0.3s ease;
}

/* 右侧面板 */
.right-panel {
  width: 280px;
  background: #f9f9f9;
  padding: 12px;
  overflow-y: auto;
  overflow-x: hidden;
  border-left: 1px solid #ddd;
  position: relative;
  z-index: 10;
  transition: width 0.3s ease, padding 0.3s ease;
}

/* 面板折叠状态 */
.left-panel.panel-collapsed,
.right-panel.panel-collapsed {
  width: 0;
  padding: 0;
  overflow: hidden;
  border: none;
  flex-shrink: 0;
}

/* 属性面板 */
.property-panel {
  margin-bottom: 12px;
}

.property-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.property-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.property-label {
  color: #666;
}

.property-value {
  color: #333;
  font-weight: 500;
}

.property-divider {
  height: 1px;
  background: #eee;
  margin: 4px 0;
}

/* 对象操作面板 */
.operation-panel {
  margin-bottom: 12px;
}

.operation-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.operation-row {
  display: flex;
  gap: 8px;
}

.operation-btn {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.operation-btn:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.operation-btn.active {
  background: #4fc3f7;
  color: white;
  border-color: #4fc3f7;
}

.operation-btn:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  border-color: #ddd;
}

.operation-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.operation-divider {
  height: 1px;
  background: #ddd;
  margin: 4px 0;
}

.operation-subtitle {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: #555;
}

/* 自定义轻型货架弹窗样式 */
.custom-shelf-dialog {
  min-width: 400px;
  max-width: 500px;
}

.custom-shelf-dialog .spec-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.custom-shelf-dialog .spec-select:focus {
  outline: none;
  border-color: #4361ee;
}

.custom-shelf-dialog .spec-details {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9ff;
  border-radius: 8px;
  border: 1px solid #e8ecff;
}

.custom-shelf-dialog .detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e8;
}

.custom-shelf-dialog .detail-item:last-child {
  border-bottom: none;
}

.custom-shelf-dialog .detail-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.custom-shelf-dialog .detail-value {
  font-size: 13px;
  color: #333;
  font-weight: 600;
  text-align: right;
  max-width: 60%;
}

.custom-shelf-dialog .spec-empty {
  margin-top: 20px;
  padding: 30px;
  text-align: center;
  color: #999;
  background: #f5f5f5;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

/* 自定义货架按钮样式 */
.custom-shelf-btn {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  border: 1px dashed #4361ee;
  color: #4361ee;
  font-weight: 500;
  cursor: pointer !important; /* 覆盖拖拽光标 */
}

.custom-shelf-btn:hover {
  background: linear-gradient(135deg, #e8ecff 0%, #d4d9ff 100%);
}

/* 批量复制控制 */
.batch-controls-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.control-row label {
  width: 40px;
  color: #666;
}

.control-row input {
  flex: 1;
  padding: 4px 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 11px;
}

.control-row span {
  color: #999;
  font-size: 10px;
}

.control-row.direction-row label {
  width: 40px;
}

.direction-select {
  flex: 1;
  padding: 4px 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 11px;
  background: #fff;
  cursor: pointer;
}

.direction-select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.direction-legend {
  margin: 4px 0;
  padding: 4px 6px;
  background: #f5f5f5;
  border-radius: 4px;
  text-align: center;
}

.direction-legend small {
  color: #666;
  font-size: 10px;
}

.batch-actions-compact {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.batch-btn {
  flex: 1;
  padding: 6px 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.batch-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.batch-btn.preview-btn:hover:not(:disabled) {
  border-color: #4fc3f7;
  background: #e3f2fd;
}

.batch-btn.confirm-btn:hover:not(:disabled) {
  border-color: #4caf50;
  background: #e8f5e9;
}

.batch-btn.cancel-btn:hover:not(:disabled) {
  border-color: #f44336;
  background: #ffebee;
}

.batch-btn:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
}

.batch-hint-compact {
  margin: 4px 0 0 0;
  font-size: 10px;
  color: #ff9800;
  text-align: center;
}

/* 对齐工具 */
.align-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.align-btn {
  padding: 8px 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.align-btn:hover:not(:disabled) {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.align-btn:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
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

/* 卡片式步骤导航 - 固定在顶部 */
.step-cards {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-shrink: 0;
}

/* 步骤内容区域 - 可滚动 */
.process-steps {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 细滚动条样式 */
.process-steps::-webkit-scrollbar {
  width: 4px;
}

.process-steps::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.process-steps::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.process-steps::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.step-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 70px;
}

.step-card:hover {
  border-color: #4fc3f7;
  background: #f5f5f5;
}

.step-card.active {
  background: #e3f2fd;
  border-color: #4fc3f7;
}

.step-card.completed {
  background: #e8f5e9;
  border-color: #4caf50;
}

.step-card-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.step-card-title {
  font-size: 11px;
  font-weight: 600;
  color: #333;
  text-align: center;
  line-height: 1.2;
}

.step-card.active .step-card-title {
  color: #0288d1;
}

.step-card.completed .step-card-title {
  color: #2e7d32;
}

/* 流程步骤 */
.process-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.process-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.process-step:hover {
  background: #f0f0f0;
}

.process-step.active {
  background: #e3f2fd;
  border-color: #4fc3f7;
}

.process-step.completed {
  background: #e8f5e9;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ddd;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
}

.process-step.active .step-number {
  background: #4fc3f7;
  color: white;
}

.process-step.completed .step-number {
  background: #4caf50;
  color: white;
}

.step-content h4 {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #333;
}

.step-content p {
  margin: 0;
  font-size: 11px;
  color: #666;
}

/* 步骤内容面板 */
.step-content-panel {
  max-height: 400px;
  overflow-y: auto;
}

.step-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.warehouse-creation,
.zone-tools,
.generate-3d-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.creation-mode,
.tool-buttons,
.control-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-primary {
  background: #4fc3f7 !important;
  color: white !important;
  border-color: #4fc3f7 !important;
}

.btn-secondary {
  background: #f5f5f5 !important;
  color: #333 !important;
  border-color: #ddd !important;
}

.warning-btn {
  background: #ff7043 !important;
  color: white !important;
  border-color: #ff7043 !important;
}

.next-btn {
  margin-top: 8px;
}

/* 功能区面积显示 */
.zone-area {
  font-family: monospace;
  font-weight: 500;
}

/* 文字标注样式 */
.text-label {
  cursor: move;
  user-select: none;
}

.text-label:hover {
  filter: drop-shadow(0 0 2px rgba(0,0,0,0.3));
}

.generate-btn {
  padding: 12px !important;
  font-size: 14px !important;
}

.warehouse-hint,
.panel-hint {
  font-size: 11px;
  color: #666;
  background: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
}

.warehouse-hint p,
.panel-hint p {
  margin: 4px 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 12px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.opacity-value {
  font-size: 11px;
  color: #666;
  text-align: right;
}

/* 流程面板 */
.process-panel {
  padding: 12px;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.process-step-wrapper {
  margin-bottom: 4px;
}

.process-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.process-step:hover {
  background: #f5f5f5;
}

.process-step.active {
  background: #e3f2fd;
  border-color: #4fc3f7;
}

.process-step.completed {
  background: #e8f5e9;
}

.step-arrow {
  margin-left: auto;
  font-size: 10px;
  color: #999;
  transition: transform 0.2s;
}

.step-arrow.expanded {
  transform: rotate(180deg);
}

/* 2级菜单 */
.sub-menu {
  padding: 8px;
  background: #f9f9f9;
  border-radius: 0 0 6px 6px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 下拉菜单样式 */
.dropdown-menu {
  margin-bottom: 6px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
}

.dropdown-header {
  padding: 10px 12px;
  background: #f0f0f0;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
}

.dropdown-header:hover {
  background: #e8e8e8;
}

.dropdown-title {
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.dropdown-icon {
  font-size: 10px;
  color: #666;
  transition: transform 0.2s;
}

.dropdown-icon.expanded {
  transform: rotate(180deg);
}

.dropdown-content {
  padding: 10px;
  background: #fff;
  border-top: 1px solid #e0e0e0;
}

.sub-menu-row {
  display: flex;
  gap: 6px;
}

.sub-menu-row button {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.sub-menu button {
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 4px;
}

.sub-menu button:hover,
.sub-menu-row button:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.sub-menu button.active,
.sub-menu-row button.active {
  background: #4fc3f7;
  color: white;
  border-color: #4fc3f7;
}

.sub-menu button:disabled,
.sub-menu-row button:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
  border-color: #ddd;
}

.btn-full {
  width: 100%;
  justify-content: center !important;
}

.sub-menu-config-row {
  display: flex;
  gap: 8px;
}

.sub-menu-config-compact {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sub-menu-config-compact label {
  font-size: 10px;
  color: #666;
}

.sub-menu-config-compact input {
  padding: 4px 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 11px;
  width: 100%;
}

.sub-menu-divider {
  height: 1px;
  background: #ddd;
  margin: 8px 0;
}

.sub-menu-config {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.sub-menu-config label {
  color: #666;
  min-width: 70px;
}

.sub-menu-config input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.sub-menu-info {
  font-size: 11px;
  color: #666;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
}

.sub-menu-info p {
  margin: 4px 0;
}

.sub-menu-info.compact {
  padding: 6px 8px;
}

.sub-menu-info.compact .info-row {
  display: flex;
  justify-content: space-between;
  margin: 3px 0;
}

.sub-menu-info.compact .info-row span {
  flex: 1;
}

.sub-menu-hint {
  font-size: 11px;
  color: #888;
  text-align: center;
  padding: 8px;
}

.btn-next {
  background: #66bb6a !important;
  color: white !important;
  border-color: #66bb6a !important;
  margin-top: 8px;
  justify-content: center !important;
}

.btn-next:disabled {
  background: #e0e0e0 !important;
  color: #999 !important;
  border-color: #ddd !important;
}

.sub-menu-zone-types {
  padding: 8px;
  background: #fff;
  border-radius: 4px;
}

.zone-type-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.zone-drag-hint {
  font-size: 10px;
  color: #888;
  margin: 0 0 6px 0;
}

.zone-stats {
  font-size: 11px;
  color: #666;
  text-align: center;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  margin: 0;
}

/* 工具组 */
.tool-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-label {
  font-size: 11px;
  color: #888;
  text-transform: uppercase;
  font-weight: bold;
}

.tool-buttons button,
.control-buttons button {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-buttons button:hover,
.control-buttons button:hover {
  background: #f0f0f0;
}

.tool-buttons button.active {
  background: #4fc3f7;
  color: white;
  border-color: #4fc3f7;
}

/* 区域类型 */
.zone-types {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.zone-types button {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.zone-types button:hover {
  background: #f0f0f0;
}

.zone-types button.active {
  background: #e3f2fd;
  border-color: #4fc3f7;
}

/* 模型分类 */
.model-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.category-content {
  padding-left: 16px;
}

.model-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.model-item:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.model-item.draggable {
  cursor: move;
}

.model-icon {
  font-size: 16px;
}

/* 对象分类折叠面板 */
.object-category {
  margin-bottom: 8px;
}

.category-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: #333;
  transition: background 0.2s;
}

.category-title:hover {
  background: #e8e8e8;
}

.toggle-icon {
  font-size: 10px;
  transition: transform 0.2s;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.category-items {
  padding-top: 8px;
}

/* 批量放置控制 */
.batch-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
}

.batch-controls .control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.batch-controls label {
  font-size: 11px;
  color: #666;
}

.batch-controls input[type="range"] {
  width: 100%;
}

.direction-buttons {
  display: flex;
  gap: 8px;
}

.direction-buttons button {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.direction-buttons button.active {
  background: #4fc3f7;
  color: white;
  border-color: #4fc3f7;
}

.batch-btn {
  padding: 8px;
  background: #4fc3f7;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.batch-btn:hover {
  background: #29b6f6;
}

.batch-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 可拖拽项目样式 */
.draggable-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  cursor: move;
  font-size: 12px;
  transition: all 0.2s;
  flex: 1;
}

.draggable-item:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.draggable-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.draggable-item .btn-icon {
  font-size: 16px;
}

/* 单列布局的大类菜单 */
.object-category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.object-category-compact {
  margin-bottom: 4px;
}

.category-title-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  color: #333;
  transition: background 0.2s;
}

.category-title-compact:hover {
  background: #e8e8e8;
}

.category-items-compact {
  padding-top: 4px;
}

.sub-menu-row-compact {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 4px;
}

.draggable-item-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 6px;
  border: 1px solid #ddd;
  border-radius: 3px;
  background: #fff;
  cursor: move;
  font-size: 10px;
  transition: all 0.2s;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.draggable-item-compact:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.draggable-item-compact.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 我的模型删除按钮 */
.my-model-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.my-model-item .draggable-item-compact {
  flex: 1;
}

.delete-my-model-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  font-size: 12px;
  border-radius: 3px;
  transition: all 0.2s;
}

.my-model-item:hover .delete-my-model-btn {
  display: inline-block;
}

.delete-my-model-btn:hover {
  background: #ff4444;
  color: white;
}

/* 完成项目 */
.finalize-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.finalize-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}

.item-icon {
  font-size: 20px;
}

.item-content h4 {
  margin: 0 0 4px 0;
  font-size: 13px;
}

.item-content p {
  margin: 0;
  font-size: 11px;
  color: #666;
}

.finalize-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.finalize-actions button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}

/* 功能区类型列表 */
.zone-type-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.zone-type-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.zone-type-grid-compact {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.zone-type-grid-compact .zone-type-item {
  justify-content: center;
  padding: 8px 4px;
  font-size: 10px;
  text-align: center;
  border-radius: 4px;
}

.zone-type-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #f9f9f9;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s;
}

.zone-type-grid .zone-type-item {
  justify-content: center;
  padding: 10px 6px;
  font-size: 11px;
  text-align: center;
}

.zone-type-item:hover {
  background: #e3f2fd;
  transform: translateX(4px);
}

.zone-type-grid .zone-type-item:hover {
  transform: scale(1.05);
}

.zone-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.zone-label {
  font-size: 12px;
  color: #333;
}

.edit-hint {
  font-size: 11px;
  color: #666;
  background: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
}

.edit-hint p {
  margin: 4px 0;
}

.zone-count {
  font-size: 13px;
  color: #666;
  text-align: center;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

/* 画布容器 */
.canvas-container {
  flex: 1;
  position: relative;
  background: #f0f0e6;
  overflow: hidden;
}

/* 3D生成加载遮罩 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #4fc3f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  color: white;
  font-size: 14px;
}

/* 2D画布 */
.canvas-2d {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.canvas-2d-area.create-mode {
  cursor: crosshair;
}

.canvas-2d-area.edit-mode {
  cursor: pointer;
}

.canvas-2d-area.panning {
  cursor: grabbing;
}

/* 功能区调整手柄 */
.resize-handle {
  cursor: pointer;
  stroke: white;
  stroke-width: 1;
}

.resize-handle:hover {
  fill: #ff5722;
  transform: scale(1.2);
}

/* 坐标标尺 - 左下角，透明背景 */
.canvas-ruler {
  position: absolute;
  bottom: 40px;
  left: 10px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(200, 200, 200, 0.5);
  border-radius: 4px;
  padding: 5px;
}

.ruler-svg {
  width: 180px;
  height: 180px;
  overflow: visible;
}

/* 鼠标坐标显示 */
.mouse-coords {
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-family: monospace;
}

/* 缩放控制 */
.zoom-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 5px;
  background: rgba(255, 255, 255, 0.9);
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.zoom-controls button {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.zoom-controls button:hover {
  background: #f0f0f0;
}

.zoom-level {
  font-size: 10px;
  text-align: center;
  color: #666;
  margin-top: 2px;
}

.canvas-2d-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ddd;
  position: relative;
}

.canvas-2d-header h3 {
  margin: 0;
  font-size: 14px;
  color: #333;
  position: absolute;
  left: 16px;
}

.canvas-2d-header .project-name-display {
  font-size: 13px;
  color: #4fc3f7;
  font-weight: 500;
  padding: 4px 12px;
  background: #f0f9ff;
  border-radius: 4px;
  border: 1px solid #b3e5fc;
}

.canvas-2d-tools {
  display: flex;
  gap: 8px;
}

.canvas-2d-tools button {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.canvas-2d-tools button:hover {
  background: #f0f0f0;
}

.canvas-2d-tools button.active {
  background: #4fc3f7;
  color: white;
  border-color: #4fc3f7;
}

.canvas-2d-area {
  flex: 1;
  position: relative;
  /* 使用亮紫色自定义十字光标，确保在各种背景下都可见 */
  cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath stroke='%23E040FB' stroke-width='2' d='M12 0v24M0 12h24'/%3E%3Ccircle cx='12' cy='12' r='2' fill='%23E040FB'/%3E%3C/svg%3E") 12 12, crosshair;
  overflow: hidden;
}

.canvas-grid {
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  position: relative;
}

.drawing-svg,
.zones-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.drawing-svg {
  pointer-events: none;
}

.drawing-svg line {
  cursor: pointer;
  pointer-events: stroke;
  stroke-width: 8;
}

.drawing-svg line.editable-line {
  cursor: pointer;
  pointer-events: stroke;
  stroke-width: 8;
}

.drawing-svg line:hover {
  stroke: #ff7043;
}

/* 功能区样式 */
.zones-svg {
  pointer-events: all;
}

.zone-rect {
  cursor: pointer;
  pointer-events: all;
}

.zone-rect:hover {
  opacity: 0.8;
}

.zone-label {
  pointer-events: none;
  user-select: none;
}

.editable-line {
  cursor: pointer;
}

.canvas-2d-info {
  display: flex;
  gap: 20px;
  padding: 8px 16px;
  background: #fff;
  border-top: 1px solid #ddd;
  font-size: 12px;
  color: #666;
}

.drawing-hint {
  color: #4fc3f7;
  font-weight: bold;
}

/* 绘制状态提示 */
.drawing-status {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(79, 195, 247, 0.9);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 长度标注样式 */
.length-label {
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 长度输入对话框 */
.length-dialog {
  width: 350px;
}

.length-dialog .hint-text {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

/* 3D画布 */
.canvas-3d {
  width: 100%;
  height: 100%;
  position: relative;
}

/* 3D视图控制工具栏 */
.canvas-3d-controls {
  position: absolute;
  right: 16px;
  top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.canvas-3d-controls button {
  width: 36px;
  height: 36px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #333;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.canvas-3d-controls button:hover {
  background: #f0f0f0;
  border-color: #4fc3f7;
}

.canvas-3d-controls button:active {
  background: #e0e0e0;
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
}

.modal-title {
  margin: 0;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #eee;
  cursor: move;
  user-select: none;
}

.modal-title:hover {
  background: #f5f5f5;
}

.modal-content {
  padding: 20px;
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
}

.confirm-btn {
  background: #66bb6a;
  color: white;
}

.cancel-btn {
  background: #ef5350;
  color: white;
}

/* 旋转对话框样式 */
.rotation-dialog {
  width: 360px;
}

.rotation-dialog .form-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.rotation-dialog .form-group label {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.rotation-dialog .form-group input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  text-align: center;
}

.rotation-dialog .hint-text {
  font-size: 12px;
  color: #666;
  margin: 12px 0;
  line-height: 1.5;
}

.rotation-presets {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.preset-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
  color: #333;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #e0e0e0;
  border-color: #bbb;
}

/* 功能区尺寸编辑对话框 */
.zone-size-dialog {
  width: 320px;
}

.zone-size-dialog .form-row {
  display: flex;
  gap: 16px;
}

.zone-size-dialog .form-group {
  flex: 1;
}

.zone-size-dialog .form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: #333;
}

.zone-size-dialog .form-group input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.zone-size-dialog .hint-text {
  font-size: 12px;
  color: #666;
  margin-top: 12px;
  line-height: 1.5;
}

/* 区域列表 */
.zone-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.zone-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}

.zone-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.zone-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.zone-details {
  display: flex;
  flex-direction: column;
}

.zone-name {
  font-size: 13px;
  font-weight: 500;
}

.zone-type {
  font-size: 11px;
  color: #666;
}

.zone-actions button {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  background: #ff7043;
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.empty-hint {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 13px;
}

/* 对齐线列表样式 */
.align-line-list {
  max-height: 200px;
  overflow-y: auto;
}

.align-line-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 6px;
  font-size: 12px;
}

.align-line-item .line-name {
  color: #333;
}

.align-line-item .delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  font-size: 14px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.align-line-item .delete-btn:hover {
  opacity: 1;
}

.align-line-item.active {
  background: #ffebee;
  border: 2px solid #ff0000;
  box-shadow: 0 0 8px rgba(255, 0, 0, 0.3);
}

.align-line-item.active .line-name {
  color: #ff0000;
  font-weight: bold;
}

/* 信息区域 */
.info-section {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
}

.info-section h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #333;
}

.info-section p {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}
</style>