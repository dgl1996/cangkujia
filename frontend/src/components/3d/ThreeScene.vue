<template>
  <div ref="container" class="three-container" tabindex="0"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const container = ref(null);
const props = defineProps({
  addingDoor: {
    type: Boolean,
    default: false
  },
  addingWindow: {
    type: Boolean,
    default: false
  },
  modelNameMap: {
    type: Object,
    default: () => ({})
  },
  warehouseConfig: {
    type: Object,
    default: () => ({
      baseHeight: 0,
      height: 5,
      wallThickness: 0.2,
      wallOpacity: 0.3
    })
  }
});

const emit = defineEmits(['model-added', 'object-selected', 'object-deselected', 'zone-selected', 'save-project', 'add-door', 'add-window', 'alignment-lines-updated', 'show-distance-line-dialog', 'distance-line-created']);

let scene, camera, renderer, controls, loader, raycaster, mouse;
let sceneObjects = [];
let selectedObject = null;
let selectedObjects = [];
let models = {};
let isMoving = false;
let movePlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
let moveIntersectPoint = new THREE.Vector3();
let moveOffset = new THREE.Vector3();
let cornerMarkers = [];
let isRotating = false;
let rotationRing = null;
let batchPreviewObjects = [];
let isBatchPreviewMode = false;
let batchPreviewConfig = null;
let rotationStartAngle = 0;
let rotationStartPositions = new Map();
let warehouseConfig = null;

// 对齐线绘制状态
let isDrawingAlignmentLine = false;
let alignmentLineStartPoint = null;
let alignmentLinePreview = null;

// 测量工具状态
let isMeasuring = false;
let measureStartPoint = null;
let measureEndPoint = null;
let measureLine = null;
let measureResultDiv = null;

// 距离线功能状态
let isDistanceLineMode = false;
let distanceLineStartPoint = null;
let distanceLinePreview = null;
let distanceLineValue = null; // 距离值（厘米）
let isDistanceLineWaitingForEnd = false; // 是否正在等待确定终点
let distanceLines = []; // 存储多个距离线对象
let nextDistanceLineId = 1;

// 对齐线数据结构和管理
let alignmentLines = [];
let nextLineId = 1;

// 空间分区优化 - 网格索引
let alignmentLineGrid = null;
const ALIGNMENT_GRID_CELL_SIZE = 500; // 对齐线网格单元大小500cm
const MAX_LINES_PER_CELL = 10; // 每个单元格最大对齐线数量，超过则细分

// 地面网格常量 - 固定1米单元格
const GRID_CELL_SIZE = 100; // 1米 = 100cm
const GRID_TOTAL_SIZE = 10000; // 100米 = 10000cm
const GRID_DIVISIONS = 100; // 100×100个单元格

// 对齐线类
class AlignmentLine {
  constructor(id, name, startPoint, endPoint, color = 0x00ffff, style = 'dashed', visible = true) {
    this.id = id;
    this.name = name;
    
    // 原始数据（用于吸附计算）- 用户绘制的真实端点
    this.originalStart = startPoint.clone();
    this.originalEnd = endPoint.clone();
    
    // 视觉数据（用于Three.js渲染）- 无限长直线端点
    // 关键修复：强制Y=0，确保在XZ平面（地面）延伸，防止Y坐标污染
    const direction = new THREE.Vector3()
      .subVectors(endPoint, startPoint);
    direction.y = 0; // 强制Y分量为0，确保在地面平面延伸
    direction.normalize(); // 重新归一化
    
    // 计算视觉端点（无限长线）
    this.visualStart = new THREE.Vector3()
      .copy(startPoint)
      .add(direction.clone().multiplyScalar(-100000));
    this.visualEnd = new THREE.Vector3()
      .copy(startPoint)
      .add(direction.clone().multiplyScalar(100000));
    
    // 关键修复：确保视觉端点的Y坐标也是0
    this.visualStart.y = 0;
    this.visualEnd.y = 0;
    
    // 保持向后兼容：startPoint/endPoint指向视觉端点（用于渲染）
    this.startPoint = this.visualStart;
    this.endPoint = this.visualEnd;
    
    this.color = color;
    this.style = style;
    this.visible = visible;
  }
}

// 对齐线管理函数
function addAlignmentLine(startPoint, endPoint) {
  // 详细记录坐标值
  console.log('🔴 对齐线创建 - 传入坐标:');
  console.log('   起点:', startPoint.x, startPoint.y, startPoint.z);
  console.log('   终点:', endPoint.x, endPoint.y, endPoint.z);
  
  // 检查是否有选中的货架，记录货架位置
  if (selectedObjects.length > 0) {
    const shelf = selectedObjects[0];
    console.log('🔴 货架实际位置:', shelf.position.x, shelf.position.y, shelf.position.z);
    const shelfBounds = getObjectBounds(shelf);
    if (shelfBounds) {
      console.log('🔴 货架边界 min:', shelfBounds.min.x, shelfBounds.min.y, shelfBounds.min.z);
      console.log('🔴 货架边界 max:', shelfBounds.max.x, shelfBounds.max.y, shelfBounds.max.z);
    }
  } else {
    console.log('🔴 没有选中的货架');
  }
  
  const name = `对齐线${nextLineId++}`;
  
  // 确保起点和终点是Vector3对象
  const start = startPoint instanceof THREE.Vector3 ? startPoint.clone() : new THREE.Vector3(startPoint.x, startPoint.y, startPoint.z);
  const end = endPoint instanceof THREE.Vector3 ? endPoint.clone() : new THREE.Vector3(endPoint.x, endPoint.y, endPoint.z);
  
  console.log('克隆后起点:', start.x, start.y, start.z);
  console.log('克隆后终点:', end.x, end.y, end.z);
  
  const line = new AlignmentLine(
    `line-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    name,
    start,
    end
  );
  
  alignmentLines.push(line);
  console.log('对齐线已添加到数组，当前数量:', alignmentLines.length);
  
  // 性能优化：重新构建网格索引
  clearAlignmentLineGrid();
  
  renderAlignmentLines();
  emit('alignment-lines-updated', alignmentLines);
  
  console.log('=== 对齐线添加完成 ===');
  return line;
}

function removeAlignmentLine(id) {
  const index = alignmentLines.findIndex(line => line.id === id);
  if (index > -1) {
    alignmentLines.splice(index, 1);
    
    // 性能优化：重新构建网格索引
    clearAlignmentLineGrid();
    
    renderAlignmentLines();
    emit('alignment-lines-updated', alignmentLines);
    return true;
  }
  return false;
}

function updateAlignmentLine(id, data) {
  const line = alignmentLines.find(line => line.id === id);
  if (line) {
    Object.assign(line, data);
    
    // 性能优化：重新构建网格索引
    clearAlignmentLineGrid();
    
    renderAlignmentLines();
    emit('alignment-lines-updated', alignmentLines);
    return true;
  }
  return false;
}

function clearAlignmentLines() {
  alignmentLines = [];
  nextLineId = 1;
  
  // 性能优化：清除网格索引
  clearAlignmentLineGrid();
  
  renderAlignmentLines();
  emit('alignment-lines-updated', alignmentLines);
}

function getAlignmentLine(id) {
  return alignmentLines.find(line => line.id === id);
}

function getAllAlignmentLines() {
  return [...alignmentLines];
}

// 空间分区 - 构建网格索引
function buildAlignmentLineGrid() {
  alignmentLineGrid = new Map();
  
  alignmentLines.forEach(line => {
    if (!line.visible) return;
    
    // 获取对齐线的边界框
    const minX = Math.min(line.originalStart.x, line.originalEnd.x);
    const maxX = Math.max(line.originalStart.x, line.originalEnd.x);
    const minZ = Math.min(line.originalStart.z, line.originalEnd.z);
    const maxZ = Math.max(line.originalStart.z, line.originalEnd.z);
    
    // 计算覆盖的网格单元
    const startCellX = Math.floor(minX / ALIGNMENT_GRID_CELL_SIZE);
    const endCellX = Math.floor(maxX / ALIGNMENT_GRID_CELL_SIZE);
    const startCellZ = Math.floor(minZ / ALIGNMENT_GRID_CELL_SIZE);
    const endCellZ = Math.floor(maxZ / ALIGNMENT_GRID_CELL_SIZE);
    
    // 将对齐线添加到所有覆盖的网格单元
    for (let x = startCellX; x <= endCellX; x++) {
      for (let z = startCellZ; z <= endCellZ; z++) {
        const cellKey = `${x},${z}`;
        if (!alignmentLineGrid.has(cellKey)) {
          alignmentLineGrid.set(cellKey, []);
        }
        alignmentLineGrid.get(cellKey).push(line);
      }
    }
  });
  
  console.log('网格索引构建完成，单元格数量:', alignmentLineGrid.size);
}

// 空间分区 - 获取点附近的对齐线（优化版）
function getNearbyAlignmentLines(point, radius = 1000) {
  if (!alignmentLineGrid) {
    buildAlignmentLineGrid();
  }
  
  const nearbyLines = new Set();
  
  // 计算点所在的网格单元
  const centerCellX = Math.floor(point.x / ALIGNMENT_GRID_CELL_SIZE);
  const centerCellZ = Math.floor(point.z / ALIGNMENT_GRID_CELL_SIZE);
  
  // 计算需要检查的单元格范围（半径覆盖的单元格）
  const cellRadius = Math.ceil(radius / ALIGNMENT_GRID_CELL_SIZE);
  
  for (let x = centerCellX - cellRadius; x <= centerCellX + cellRadius; x++) {
    for (let z = centerCellZ - cellRadius; z <= centerCellZ + cellRadius; z++) {
      const cellKey = `${x},${z}`;
      if (alignmentLineGrid.has(cellKey)) {
        alignmentLineGrid.get(cellKey).forEach(line => {
          if (line.visible) {
            nearbyLines.add(line);
          }
        });
      }
    }
  }
  
  return Array.from(nearbyLines);
}

// 空间分区 - 清除网格索引
function clearAlignmentLineGrid() {
  alignmentLineGrid = null;
}

// 对齐线数据序列化
function serializeAlignmentLines() {
  console.log('💾 开始保存对齐线，数量:', alignmentLines.length);
  
  return alignmentLines.map(line => {
    // 调试日志：确认数据污染环节
    console.log('💾 保存对齐线:', line.id, 
      '\n  originalStart:', line.originalStart?.x?.toFixed(2), line.originalStart?.z?.toFixed(2),
      '\n  visualStart:', line.visualStart?.x?.toFixed(2), line.visualStart?.z?.toFixed(2),
      '\n  startPoint:', line.startPoint?.x?.toFixed(2), line.startPoint?.z?.toFixed(2)
    );
    
    return {
      id: line.id,
      name: line.name,
      // 关键修复：保存原始端点（originalStart/End），而不是视觉端点（startPoint/End）
      // 视觉端点是无限长线的端点（延伸±10万cm），保存后会导致加载时对齐线跑到画面外
      startPoint: { 
        x: line.originalStart.x, 
        y: 0, // 强制Y=0
        z: line.originalStart.z 
      },
      endPoint: { 
        x: line.originalEnd.x, 
        y: 0, // 强制Y=0
        z: line.originalEnd.z 
      },
      color: line.color,
      style: line.style,
      visible: line.visible !== false
    };
  });
}

// 对齐线渲染相关
let alignmentLineObjects = new Map(); // 存储对齐线的Three.js对象

// 创建对齐线材质
function createAlignmentLineMaterial() {
  return new THREE.LineDashedMaterial({
    color: 0xff0000,  // 红色，醒目对比
    linewidth: 2,
    transparent: true,
    opacity: 0.9,  // 提高透明度
    dashSize: 50,  // 增大虚线尺寸
    gapSize: 30,   // 增大间隙
    scale: 1       // 虚线缩放
  });
}

// 创建高亮对齐线材质
function createHighlightedMaterial() {
  return new THREE.LineBasicMaterial({
    color: 0xffff00,
    linewidth: 3,
    transparent: true,
    opacity: 0.9
  });
}

// 更新线条材质
function updateLineMaterial(line, isHighlighted) {
  if (!line) return;
  
  const lineObject = alignmentLineObjects.get(line.id);
  if (!lineObject) return;
  
  const material = isHighlighted ? createHighlightedMaterial() : createAlignmentLineMaterial();
  lineObject.material = material;
  
  // 对于虚线材质，需要重新计算线条长度
  if (material.type === 'LineDashedMaterial') {
    lineObject.computeLineDistances();
  }
}

// 高亮对齐线
let highlightedLineId = null; // 当前高亮的对齐线ID

function highlightAlignmentLine(lineId) {
  console.log('高亮对齐线:', lineId);
  
  // 先取消所有高亮
  alignmentLineObjects.forEach((lineObject, id) => {
    lineObject.material = createAlignmentLineMaterial();
    if (lineObject.material.type === 'LineDashedMaterial') {
      lineObject.computeLineDistances();
    }
  });
  
  // 高亮选中的对齐线
  if (lineId) {
    const lineObject = alignmentLineObjects.get(lineId);
    if (lineObject) {
      // 使用发光效果的高亮材质
      const highlightMaterial = new THREE.LineBasicMaterial({
        color: 0xffff00, // 黄色高亮
        linewidth: 3,
        transparent: true,
        opacity: 1.0
      });
      lineObject.material = highlightMaterial;
      console.log('对齐线已高亮:', lineId);
    }
    highlightedLineId = lineId;
  } else {
    highlightedLineId = null;
    console.log('取消所有高亮');
  }
}

// 吸附时高亮对齐线（变绿）
let snappedLineIdForMove = null;

function highlightAlignmentLineForSnap(lineId, isGreen) {
  // 如果已经高亮同一条线，不需要重复设置
  if (snappedLineIdForMove === lineId && isGreen) return;
  
  // 先恢复之前高亮的线
  if (snappedLineIdForMove && snappedLineIdForMove !== lineId) {
    const oldLineObject = alignmentLineObjects.get(snappedLineIdForMove);
    if (oldLineObject) {
      oldLineObject.material = createAlignmentLineMaterial();
      oldLineObject.computeLineDistances();
    }
  }
  
  // 高亮新的线
  if (lineId && isGreen) {
    const lineObject = alignmentLineObjects.get(lineId);
    if (lineObject) {
      // 绿色高亮材质（表示已吸附）
      const greenMaterial = new THREE.LineBasicMaterial({
        color: 0x00ff00, // 绿色
        linewidth: 4,
        transparent: true,
        opacity: 1.0
      });
      lineObject.material = greenMaterial;
      console.log('🟢 对齐线已变绿（吸附）:', lineId);
    }
    snappedLineIdForMove = lineId;
  } else if (!isGreen) {
    snappedLineIdForMove = null;
  }
}

// 恢复所有对齐线颜色（红色虚线）
function restoreAllAlignmentLineColors() {
  if (snappedLineIdForMove) {
    const lineObject = alignmentLineObjects.get(snappedLineIdForMove);
    if (lineObject) {
      lineObject.material = createAlignmentLineMaterial();
      lineObject.computeLineDistances();
    }
    snappedLineIdForMove = null;
    console.log('🔴 对齐线颜色已恢复');
  }
}

// 创建对齐线几何体（无限长直线）
function createAlignmentLineGeometry(start, end) {
  console.log('创建对齐线几何体，起点:', start, '终点:', end);
  
  // 确保起点和终点是Vector3对象
  const startPoint = start instanceof THREE.Vector3 ? start : new THREE.Vector3(start.x, start.y, start.z);
  const endPoint = end instanceof THREE.Vector3 ? end : new THREE.Vector3(end.x, end.y, end.z);
  
  // 计算方向向量（从start指向end）
  // 关键修复：强制Y=0，确保在XZ平面（地面）延伸，防止Y坐标漂移
  const direction = new THREE.Vector3().subVectors(endPoint, startPoint);
  direction.y = 0; // 强制Y分量为0，确保在地面平面延伸
  direction.normalize(); // 重新归一化
  
  // 向两端延伸足够长的距离（100000cm = 1000米）
  const extensionLength = 100000;
  
  // 计算无限长直线的两个端点
  const lineStart = new THREE.Vector3().copy(startPoint).add(direction.clone().multiplyScalar(-extensionLength));
  const lineEnd = new THREE.Vector3().copy(startPoint).add(direction.clone().multiplyScalar(extensionLength));
  
  // 关键修复：确保视觉端点的Y坐标也是0（防止飘在空中）
  lineStart.y = 0;
  lineEnd.y = 0;
  
  const points = [lineStart, lineEnd];
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  
  console.log('无限长直线几何体创建完成，顶点数:', geometry.attributes.position.count);
  console.log('直线起点:', lineStart.x, lineStart.y, lineStart.z, '直线终点:', lineEnd.x, lineEnd.y, lineEnd.z);
  return geometry;
}

// 更新对齐线几何体
function updateAlignmentLineGeometry(line, start, end) {
  if (!line || !line.geometry) return;
  
  const points = [start, end];
  line.geometry.setFromPoints(points);
  line.geometry.attributes.position.needsUpdate = true;
}

// 添加对齐线到场景
function addLineToScene(line) {
  if (!line || !line.visible) {
    console.log('对齐线不可见或不存在，跳过渲染');
    return;
  }
  
  console.log('=== 添加对齐线到场景 ===');
  console.log('对齐线ID:', line.id);
  // 关键修复：使用原始端点（originalStart/End），而不是视觉端点（startPoint/End）
  // 视觉端点是已经延伸10万cm的无限长线端点，会导致双倍延伸成天文数字
  console.log('起点坐标(原始):', line.originalStart.x, line.originalStart.y, line.originalStart.z);
  console.log('终点坐标(原始):', line.originalEnd.x, line.originalEnd.y, line.originalEnd.z);
  
  // 传入原始端点，让createAlignmentLineGeometry正确计算无限长直线
  const geometry = createAlignmentLineGeometry(line.originalStart, line.originalEnd);
  const material = createAlignmentLineMaterial();
  
  console.log('材质类型:', material.type);
  console.log('材质颜色:', material.color);
  console.log('材质透明度:', material.opacity);
  
  const lineObject = new THREE.Line(geometry, material);
  
  // 对于虚线材质，需要计算线条长度
  console.log('检查材质类型是否为LineDashedMaterial:', material.type === 'LineDashedMaterial');
  if (material.type === 'LineDashedMaterial') {
    console.log('调用computeLineDistances...');
    lineObject.computeLineDistances();
    console.log('computeLineDistances调用完成');
    console.log('线条距离属性:', lineObject.userData.lineDistances);
  }
  
  // 确保对齐线在仓库地面上方（考虑baseHeight）
  const baseHeight = props.warehouseConfig ? props.warehouseConfig.baseHeight * 100 : 0; // 米转厘米
  lineObject.position.y = baseHeight + 2; // 在地面之上2cm，避免z-fighting
  
  console.log('对齐线Y轴位置:', lineObject.position.y, 'baseHeight:', baseHeight, 'props.warehouseConfig:', props.warehouseConfig);
  console.log('相机位置:', camera ? camera.position : '未定义');
  
  scene.add(lineObject);
  alignmentLineObjects.set(line.id, lineObject);
  
  console.log('对齐线已添加到场景:', line.id);
  console.log('场景中对齐线对象:', lineObject);
  console.log('========================');
}

// 从场景中移除对齐线
function removeLineFromScene(line) {
  if (!line) return;
  
  const lineObject = alignmentLineObjects.get(line.id);
  if (lineObject) {
    scene.remove(lineObject);
    alignmentLineObjects.delete(line.id);
  }
}

// 更新对齐线可见性
function updateLineVisibility(line, visible) {
  if (!line) return;
  
  line.visible = visible;
  
  const lineObject = alignmentLineObjects.get(line.id);
  if (lineObject) {
    lineObject.visible = visible;
  } else if (visible) {
    // 如果对象不存在且需要显示，则添加到场景
    addLineToScene(line);
  }
}

// 渲染对齐线
function renderAlignmentLines() {
  console.log('渲染对齐线，当前对齐线数量:', alignmentLines.length);
  
  // 清除旧的对齐线对象
  alignmentLineObjects.forEach(obj => scene.remove(obj));
  alignmentLineObjects.clear();
  
  // 渲染新的对齐线
  alignmentLines.forEach(line => {
    console.log('处理对齐线:', line.id, 'visible:', line.visible);
    if (line.visible) {
      addLineToScene(line);
    }
  });
  
  console.log('对齐线渲染完成，场景中对齐线对象数量:', alignmentLineObjects.size);
}

// 对齐线数据反序列化
function deserializeAlignmentLines(data) {
  if (!Array.isArray(data)) return;
  
  console.log('📂 开始加载对齐线，数量:', data.length);
  
  alignmentLines = data.map(item => {
    // 版本兼容处理：确保所有必要字段都存在
    const id = item.id || `line-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const name = item.name || `对齐线${nextLineId++}`;
    
    // 调试日志：确认加载的数据
    console.log('📂 加载对齐线数据:', id, 
      'item.startPoint:', item.startPoint?.x?.toFixed(2), item.startPoint?.z?.toFixed(2)
    );
    
    // 关键修复：强制Y=0，使用保存的原始坐标
    const startPoint = item.startPoint ? 
      new THREE.Vector3(item.startPoint.x, 0, item.startPoint.z) : 
      new THREE.Vector3(0, 0, 0);
    const endPoint = item.endPoint ? 
      new THREE.Vector3(item.endPoint.x, 0, item.endPoint.z) : 
      new THREE.Vector3(100, 0, 100);
    
    console.log('📂 创建AlignmentLine:', id, 
      'startPoint:', startPoint.x.toFixed(2), startPoint.z.toFixed(2)
    );
    
    const color = item.color || 0x00ffff;
    const style = item.style || 'dashed';
    const visible = item.visible !== undefined ? item.visible : true;
    
    return new AlignmentLine(id, name, startPoint, endPoint, color, style, visible);
  });
  
  // 更新nextLineId
  if (alignmentLines.length > 0) {
    const maxNumber = Math.max(...alignmentLines.map(line => {
      const match = line.name.match(/对齐线(\d+)/);
      return match ? parseInt(match[1]) : 0;
    }));
    nextLineId = maxNumber + 1;
  } else {
    nextLineId = 1;
  }
  
  // 重新渲染对齐线
  renderAlignmentLines();
}

// 开始绘制对齐线
function startDrawingAlignmentLine() {
  isDrawingAlignmentLine = true;
  alignmentLineStartPoint = null;
  console.log('开始绘制对齐线');
}

// 结束绘制对齐线
function stopDrawingAlignmentLine() {
  isDrawingAlignmentLine = false;
  clearAlignmentLinePreview();
  console.log('结束绘制对齐线');
}

// 取消绘制对齐线
function cancelDrawingAlignmentLine() {
  isDrawingAlignmentLine = false;
  clearAlignmentLinePreview();
  console.log('取消绘制对齐线');
}

// 开始测量
function startMeasuring() {
  isMeasuring = true;
  measureStartPoint = null;
  measureEndPoint = null;
  console.log('开始测量模式');
}

// 结束测量
function stopMeasuring() {
  isMeasuring = false;
  clearMeasureLine();
  hideMeasureResult();
  console.log('结束测量模式');
}

// 取消测量
function cancelMeasuring() {
  isMeasuring = false;
  clearMeasureLine();
  hideMeasureResult();
  console.log('取消测量');
}

// ========== 距离线功能 ==========

// 开始距离线模式
function startDistanceLineMode() {
  console.log('【关键-debug】startDistanceLineMode() 被调用');
  isDistanceLineMode = true;
  distanceLineStartPoint = null;
  distanceLinePreview = null;
  distanceLineValue = null;
  isDistanceLineWaitingForEnd = false;
  console.log('【关键-debug】ThreeScene 状态:', { isDistanceLineMode, isDistanceLineWaitingForEnd });
  console.log('开始距离线模式');
}

// 结束距离线模式
function stopDistanceLineMode() {
  isDistanceLineMode = false;
  clearDistanceLinePreview();
  distanceLineStartPoint = null;
  distanceLineValue = null;
  isDistanceLineWaitingForEnd = false;
  console.log('结束距离线模式');
}

// 设置距离线值（由CoreFunction调用）
function setDistanceLineValue(value) {
  console.log('【关键-debug】ThreeScene.setDistanceLineValue() 被调用:', value);
  distanceLineValue = value; // 厘米
  isDistanceLineWaitingForEnd = true;
  console.log('【关键-debug】ThreeScene 状态更新:', {
    isDistanceLineMode,
    isDistanceLineWaitingForEnd,
    hasStartPoint: !!distanceLineStartPoint,
    distanceLineValue
  });
}

// 清除距离线预览
function clearDistanceLinePreview() {
  if (distanceLinePreview) {
    scene.remove(distanceLinePreview.line);
    distanceLinePreview.line.geometry.dispose();
    distanceLinePreview.line.material.dispose();
    if (distanceLinePreview.label) {
      scene.remove(distanceLinePreview.label);
      if (distanceLinePreview.label.material.map) {
        distanceLinePreview.label.material.map.dispose();
      }
      distanceLinePreview.label.material.dispose();
    }
    // 清除标记球
    if (distanceLinePreview.sphere) {
      scene.remove(distanceLinePreview.sphere);
      distanceLinePreview.sphere.geometry.dispose();
      distanceLinePreview.sphere.material.dispose();
    }
    distanceLinePreview = null;
  }
}

// 创建距离线预览
// 创建距离线预览（参考测量工具实现）
function createDistanceLinePreview(start, end) {
  console.log('【关键-debug】createDistanceLinePreview() 被调用');
  
  if (!start || !end) {
    console.error('【关键-debug】起点或终点为空');
    return;
  }
  
  // 确保起点和终点在地面水平面（Y=0）
  const startOnGround = new THREE.Vector3(start.x, 0, start.z);
  const endOnGround = new THREE.Vector3(end.x, 0, end.z);
  
  // 如果预览线已存在，更新几何体；否则创建新线
  if (distanceLinePreview && distanceLinePreview.line) {
    const points = [startOnGround, endOnGround];
    distanceLinePreview.line.geometry.setFromPoints(points);
    distanceLinePreview.start = start;
    distanceLinePreview.end = end;
    // 更新标记球位置
    if (distanceLinePreview.sphere) {
      distanceLinePreview.sphere.position.copy(endOnGround);
      distanceLinePreview.sphere.position.y = 0.5;
    }
    console.log('【关键-debug】预览线已更新');
  } else {
    const points = [startOnGround, endOnGround];
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    
    // 参考测量工具的材质设置
    const material = new THREE.LineBasicMaterial({
      color: 0xff0000, // 红色
      linewidth: 2
    });
    
    const line = new THREE.Line(geometry, material);
  line.position.y = 0.2; // 在地面之上0.2cm（参考测量工具）
  
  if (!scene) {
    console.error('【关键-debug】scene对象为空');
    return;
  }
  
  scene.add(line);
  
  // 添加一个明显的标记球在终点，帮助定位
  const sphereGeometry = new THREE.SphereGeometry(0.5, 16, 16); // 0.5米半径的球
  const sphereMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
  const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
  sphere.position.copy(endOnGround);
  sphere.position.y = 0.5; // 在地面之上
  scene.add(sphere);
  
  console.log('【关键-debug】预览线已添加到场景，并添加标记球');
    
    distanceLinePreview = {
      line: line,
      start: start,
      end: end,
      sphere: sphere // 存储标记球
    };
  }
}

// 更新距离线预览
function updateDistanceLinePreview(direction) {
  if (!distanceLineStartPoint || !distanceLineValue || !isDistanceLineWaitingForEnd) return;
  
  // 计算终点：起点 + 方向 * 距离
  // 场景使用厘米单位，distanceLineValue已经是厘米，直接使用
  const endPoint = distanceLineStartPoint.clone().add(
    direction.clone().normalize().multiplyScalar(distanceLineValue)
  );
  
  createDistanceLinePreview(distanceLineStartPoint, endPoint);
}

// 创建距离标签
function createDistanceLabel(position, distance) {
  // 创建Canvas纹理
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = 256;
  canvas.height = 64;
  
  // 背景
  context.fillStyle = 'rgba(0, 0, 0, 0.7)';
  context.fillRect(0, 0, canvas.width, canvas.height);
  
  // 文字
  context.font = 'bold 32px Arial';
  context.fillStyle = '#ffffff';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  const distanceInMeters = (distance / 100).toFixed(1);
  context.fillText(distanceInMeters + '米', canvas.width / 2, canvas.height / 2);
  
  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(material);
  
  sprite.position.copy(position);
  sprite.position.y = 1.0; // 在距离线上方1米
  sprite.scale.set(2, 0.5, 1);
  
  scene.add(sprite);
  return sprite;
}

// 确认距离线（创建固定距离线）
function confirmDistanceLine() {
  console.log('【关键-debug】confirmDistanceLine() 被调用');
  if (!distanceLineStartPoint || !distanceLineValue || !distanceLinePreview) {
    console.error('【关键-debug】confirmDistanceLine 参数不完整');
    return;
  }
  
  const id = nextDistanceLineId++;
  const endPoint = distanceLinePreview.end.clone();
  
  // 确保起点和终点在地面水平面（Y=0）
  const startOnGround = new THREE.Vector3(distanceLineStartPoint.x, 0, distanceLineStartPoint.z);
  const endOnGround = new THREE.Vector3(endPoint.x, 0, endPoint.z);
  
  // 创建固定距离线（实线）- 参考测量工具实现
  const points = [startOnGround, endOnGround];
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({
    color: 0x9370DB, // 紫色，提高可见性
    linewidth: 2
  });

  const line = new THREE.Line(geometry, material);
  line.position.y = 0.2; // 在地面之上0.2cm（参考测量工具）
  scene.add(line);

  // 添加一个明显的标记球在终点，帮助定位
  const sphereGeometry = new THREE.SphereGeometry(0.5, 16, 16); // 0.5米半径的球
  const sphereMaterial = new THREE.MeshBasicMaterial({ color: 0x9370DB }); // 紫色
  const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
  sphere.position.copy(endOnGround);
  sphere.position.y = 0.5; // 在地面之上
  scene.add(sphere);
  
  console.log('【关键-debug】固定距离线已添加到场景，并添加标记球');
  
  // 创建距离标签（使用中点位置）
  const midPoint = new THREE.Vector3().addVectors(startOnGround, endOnGround).multiplyScalar(0.5);
  const label = createDistanceLabel(midPoint, distanceLineValue);
  
  // 存储距离线对象
  const distanceLineObj = {
    id: id,
    startPoint: startOnGround,
    endPoint: endOnGround,
    distance: distanceLineValue,
    line: line,
    label: label,
    sphere: sphere, // 存储标记球
    createdAt: Date.now()
  };
  
  distanceLines.push(distanceLineObj);
  
  // 先保存距离值用于日志
  const savedDistance = distanceLineValue;
  
  // 清除预览
  clearDistanceLinePreview();
  
  // 重置状态
  distanceLineStartPoint = null;
  distanceLineValue = null;
  isDistanceLineWaitingForEnd = false;
  isDistanceLineMode = false; // 退出距离线模式

  console.log('距离线已创建:', id, '距离:', savedDistance, '厘米');

  // 通知父组件距离线已创建，自动切换到选择模式
  emit('distance-line-created');

  // 15秒后自动清除
  setTimeout(() => {
    console.log('【调试】15秒倒计时结束，清除距离线:', id);
    clearDistanceLine(id);
  }, 15000);
}

// 清除指定距离线
function clearDistanceLine(id) {
  const index = distanceLines.findIndex(dl => dl.id === id);
  if (index === -1) return;
  
  const dl = distanceLines[index];
  
  // 清除线
  if (dl.line) {
    scene.remove(dl.line);
    dl.line.geometry.dispose();
    dl.line.material.dispose();
  }
  
  // 清除标签
  if (dl.label) {
    scene.remove(dl.label);
    if (dl.label.material.map) {
      dl.label.material.map.dispose();
    }
    dl.label.material.dispose();
  }
  
  // 清除标记球
  if (dl.sphere) {
    scene.remove(dl.sphere);
    dl.sphere.geometry.dispose();
    dl.sphere.material.dispose();
  }
  
  distanceLines.splice(index, 1);
  console.log('距离线已清除:', id);
}

// 清理所有距离线
function clearAllDistanceLines() {
  distanceLines.forEach(dl => {
    if (dl.line) {
      scene.remove(dl.line);
      dl.line.geometry.dispose();
      dl.line.material.dispose();
    }
    if (dl.label) {
      scene.remove(dl.label);
      if (dl.label.material.map) {
        dl.label.material.map.dispose();
      }
      dl.label.material.dispose();
    }
  });
  distanceLines = [];
  console.log('所有距离线已清除');
}

// 清除测量线
function clearMeasureLine() {
  if (measureLine) {
    scene.remove(measureLine);
    measureLine.geometry.dispose();
    measureLine.material.dispose();
    measureLine = null;
  }
}

// 隐藏测量结果
function hideMeasureResult() {
  if (measureResultDiv) {
    measureResultDiv.remove();
    measureResultDiv = null;
  }
}

// 创建测量线
function createMeasureLine(start, end) {
  clearMeasureLine();
  
  const points = [start, end];
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  
  const material = new THREE.LineBasicMaterial({
    color: 0xff0000,
    linewidth: 2
  });
  
  measureLine = new THREE.Line(geometry, material);
  measureLine.position.y = 0.2; // 在地面之上0.2cm
  scene.add(measureLine);
}

// 更新测量线
function updateMeasureLine(end) {
  if (measureLine && measureStartPoint) {
    const points = [measureStartPoint, end];
    measureLine.geometry.setFromPoints(points);
  }
}

// 显示测量结果
function showMeasureResult(distance) {
  hideMeasureResult();
  
  // 转换为米并格式化
  const distanceMeters = (distance / 100).toFixed(2);
  
  // 创建结果显示div
  measureResultDiv = document.createElement('div');
  measureResultDiv.style.cssText = `
    position: fixed;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
    z-index: 1000;
    pointer-events: none;
  `;
  measureResultDiv.textContent = `距离: ${distanceMeters} 米`;
  document.body.appendChild(measureResultDiv);
  
  // 10秒后自动隐藏
  setTimeout(() => {
    hideMeasureResult();
  }, 10000);
}

// 清除对齐线预览
function clearAlignmentLinePreview() {
  if (alignmentLinePreview) {
    scene.remove(alignmentLinePreview);
    alignmentLinePreview = null;
  }
}

// 更新对齐线预览
function updateAlignmentLinePreview(start, end) {
  clearAlignmentLinePreview();
  
  const geometry = createAlignmentLineGeometry(start, end);
  const material = createAlignmentLineMaterial();
  alignmentLinePreview = new THREE.Line(geometry, material);
  
  if (material.type === 'LineDashedMaterial') {
    alignmentLinePreview.computeLineDistances();
  }
  
  alignmentLinePreview.position.y = 0.1;
  scene.add(alignmentLinePreview);
}

// 子任务3.1: 对象边界计算

// 计算对象的边界框
function getObjectBounds(object) {
  if (!object) return null;
  
  const box = new THREE.Box3().setFromObject(object);
  return box;
}

// 提取对象的边缘线
function getObjectEdges(bounds) {
  if (!bounds) return [];
  
  const min = bounds.min;
  const max = bounds.max;
  
  // 计算中心点
  const center = bounds.getCenter(new THREE.Vector3());
  
  // 提取边缘线
  const edges = [
    // 底部边缘（地面上的边缘）
    { start: new THREE.Vector3(min.x, 0, min.z), end: new THREE.Vector3(max.x, 0, min.z) }, // 前边缘
    { start: new THREE.Vector3(max.x, 0, min.z), end: new THREE.Vector3(max.x, 0, max.z) }, // 右边缘
    { start: new THREE.Vector3(max.x, 0, max.z), end: new THREE.Vector3(min.x, 0, max.z) }, // 后边缘
    { start: new THREE.Vector3(min.x, 0, max.z), end: new THREE.Vector3(min.x, 0, min.z) }, // 左边缘
    
    // 中心线（可选）
    { start: new THREE.Vector3(center.x, 0, min.z), end: new THREE.Vector3(center.x, 0, max.z) }, // 垂直中心线
    { start: new THREE.Vector3(min.x, 0, center.z), end: new THREE.Vector3(max.x, 0, center.z) }  // 水平中心线
  ];
  
  return edges;
}

// 子任务3.2: 参考线生成逻辑

// 基于对象生成参考线
function generateReferenceLines(object) {
  if (!object) return [];
  
  // 计算对象边界
  const bounds = getObjectBounds(object);
  if (!bounds) return [];
  
  // 提取对象边缘
  const edges = getObjectEdges(bounds);
  
  // 生成参考线（将边缘线转换为对齐线）
  const referenceLines = edges.map((edge, index) => {
    const name = `参考线-${index + 1}`;
    return new AlignmentLine(
      `ref-line-${Date.now()}-${index}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      edge.start,
      edge.end,
      0x00ffff, // 青色
      'dashed',
      true
    );
  });
  
  // 过滤冗余参考线
  const filteredLines = filterReferenceLines(referenceLines);
  
  return filteredLines;
}

// 过滤冗余参考线
function filterReferenceLines(lines) {
  if (!lines || lines.length === 0) return [];
  
  const filtered = [];
  const threshold = 0.1; // 阈值，用于判断两条线是否重合
  
  lines.forEach((line, index) => {
    // 检查是否与已添加的线重合
    const isRedundant = filtered.some(existingLine => {
      // 检查两条线是否有相同的起点和终点（考虑方向）
      const sameStart = line.startPoint.distanceTo(existingLine.startPoint) < threshold &&
                      line.endPoint.distanceTo(existingLine.endPoint) < threshold;
      const reverseStart = line.startPoint.distanceTo(existingLine.endPoint) < threshold &&
                          line.endPoint.distanceTo(existingLine.startPoint) < threshold;
      
      return sameStart || reverseStart;
    });
    
    if (!isRedundant) {
      filtered.push(line);
    }
  });
  
  return filtered;
}

// 子任务5.1: 距离计算与吸附逻辑

// 吸附配置
const SNAP_CONFIG = {
  threshold: 10, // 吸附距离阈值：10CM
  enabled: true  // 是否启用吸附
};

// 当前吸附状态
let currentSnapState = {
  isSnapped: false,
  snappedLineId: null,
  snapPoint: null,
  originalPosition: null
};

// 计算点到线段的距离
function calculateDistance(point, lineStart, lineEnd) {
  if (!point || !lineStart || !lineEnd) return Infinity;
  
  // 将输入转换为Vector3
  const p = point instanceof THREE.Vector3 ? point : new THREE.Vector3(point.x, point.y, point.z);
  const start = lineStart instanceof THREE.Vector3 ? lineStart : new THREE.Vector3(lineStart.x, lineStart.y, lineStart.z);
  const end = lineEnd instanceof THREE.Vector3 ? lineEnd : new THREE.Vector3(lineEnd.x, lineEnd.y, lineEnd.z);
  
  // 计算线段方向向量
  const lineVector = new THREE.Vector3().subVectors(end, start);
  const lineLength = lineVector.length();
  
  if (lineLength === 0) {
    return p.distanceTo(start);
  }
  
  // 计算投影参数 t
  const t = Math.max(0, Math.min(1, new THREE.Vector3().subVectors(p, start).dot(lineVector) / (lineLength * lineLength)));
  
  // 计算投影点
  const projection = new THREE.Vector3().copy(start).add(lineVector.multiplyScalar(t));
  
  // 返回点到投影点的距离
  return p.distanceTo(projection);
}

// 计算点到无限长直线的距离（用于对齐线）
function calculateDistanceToInfiniteLine(point, lineStart, lineEnd) {
  if (!point || !lineStart || !lineEnd) return Infinity;
  
  const p = point instanceof THREE.Vector3 ? point : new THREE.Vector3(point.x, point.y, point.z);
  const start = lineStart instanceof THREE.Vector3 ? lineStart : new THREE.Vector3(lineStart.x, lineStart.y, lineStart.z);
  const end = lineEnd instanceof THREE.Vector3 ? lineEnd : new THREE.Vector3(lineEnd.x, lineEnd.y, lineEnd.z);
  
  // 计算直线方向向量
  const lineVector = new THREE.Vector3().subVectors(end, start).normalize();
  
  // 计算从起点到点的向量
  const pointVector = new THREE.Vector3().subVectors(p, start);
  
  // 计算叉积的模 = |a||b|sin(theta)
  const cross = new THREE.Vector3().crossVectors(lineVector, pointVector);
  
  // 距离 = |叉积| / |方向向量| = |叉积| (因为方向向量已归一化)
  return cross.length();
}

// 找到最近的对齐线（使用空间分区优化）
function findClosestAlignmentLine(point, lines) {
  if (!point || !lines || lines.length === 0) {
    return { line: null, distance: Infinity, projection: null };
  }
  
  let closestLine = null;
  let minDistance = Infinity;
  let closestProjection = null;
  
  const p = point instanceof THREE.Vector3 ? point : new THREE.Vector3(point.x, point.y, point.z);
  
  // 性能优化：如果对齐线数量超过20条，使用空间分区
  let linesToCheck = lines;
  if (lines.length > 20) {
    linesToCheck = getNearbyAlignmentLines(p, 2000); // 只检查2000cm范围内的对齐线
    
    // 如果附近没有对齐线，直接返回
    if (linesToCheck.length === 0) {
      return { line: null, distance: Infinity, projection: null };
    }
  }
  
  linesToCheck.forEach(line => {
    if (!line.visible) return;
    
    // 计算到无限长直线的距离（使用原始端点）
    const distance = calculateDistanceToInfiniteLine(p, line.originalStart, line.originalEnd);
    
    if (distance < minDistance) {
      minDistance = distance;
      closestLine = line;
      
      // 计算投影点（使用原始端点）
      const start = line.originalStart instanceof THREE.Vector3 ? line.originalStart : new THREE.Vector3(line.originalStart.x, line.originalStart.y, line.originalStart.z);
      const end = line.originalEnd instanceof THREE.Vector3 ? line.originalEnd : new THREE.Vector3(line.originalEnd.x, line.originalEnd.y, line.originalEnd.z);
      const lineVector = new THREE.Vector3().subVectors(end, start).normalize();
      const pointVector = new THREE.Vector3().subVectors(p, start);
      const projectionDistance = pointVector.dot(lineVector);
      closestProjection = new THREE.Vector3().copy(start).add(lineVector.multiplyScalar(projectionDistance));
    }
  });
  
  return {
    line: closestLine,
    distance: minDistance,
    projection: closestProjection
  };
}

// 应用吸附逻辑
function applySnap(position, object, moveDirection) {
  console.log('applySnap被调用，原始position:', position.x, position.y, position.z);
  console.log('alignmentLines数量:', alignmentLines.length);
  console.log('SNAP_CONFIG:', SNAP_CONFIG);
  
  if (!SNAP_CONFIG.enabled || snapDisabled || !position || alignmentLines.length === 0) {
    console.log('applySnap提前返回，原因:', 
      !SNAP_CONFIG.enabled ? 'SNAP_CONFIG.enabled=false' :
      snapDisabled ? 'snapDisabled=true' :
      !position ? 'position为空' :
      'alignmentLines为空'
    );
    return { snapped: false, position: position };
  }
  
  // P0修复：强制投影到地面（Y=0），仓库布局是平面逻辑
  const groundPosition = position.clone();
  groundPosition.y = 0;
  console.log('🔧 投影后位置:', groundPosition.x, groundPosition.y, groundPosition.z);
  
  // 获取对象的边界中心点（用于吸附计算）- 使用投影后的位置
  let snapPoint = groundPosition.clone();
  
  if (object) {
    const bounds = getObjectBounds(object);
    if (bounds) {
      const center = bounds.getCenter(new THREE.Vector3());
      // 使用底部中心点进行吸附，Y强制为0
      snapPoint = new THREE.Vector3(center.x, 0, center.z);
    }
  }
  
  // 使用handleBoundarySnap处理边界吸附（包含优先级逻辑）
  // 传入投影后的位置进行计算
  const boundaryResult = handleBoundarySnap(object, alignmentLines, moveDirection);
  
  if (boundaryResult.shouldSnap) {
    const line = boundaryResult.line;
    const projection = boundaryResult.position;
    const distance = boundaryResult.distance;
    
    // 计算吸附后的位置偏移
    const deltaX = projection.x - snapPoint.x;
    const deltaZ = projection.z - snapPoint.z;
    
    // 应用偏移到原位置（保持原高度）
    const snappedPosition = position.clone();
    snappedPosition.x += deltaX;
    snappedPosition.z += deltaZ;
    // Y保持原高度不变
    
    console.log('🎯 吸附成功！吸附到位置:', snappedPosition.x, snappedPosition.y, snappedPosition.z);
    
    // 更新吸附状态
    currentSnapState = {
      isSnapped: true,
      snappedLineId: line.id,
      snapPoint: projection,
      originalPosition: position.clone(),
      priority: boundaryResult.priority
    };
    
    return {
      snapped: true,
      position: snappedPosition,
      line: line,
      distance: distance,
      projection: projection,
      priority: boundaryResult.priority
    };
  }
  
  // 未吸附，重置状态
  currentSnapState = {
    isSnapped: false,
    snappedLineId: null,
    snapPoint: null,
    originalPosition: null,
    priority: null
  };
  
  return {
    snapped: false,
    position: position
  };
}

// 获取当前吸附状态
function getSnapState() {
  return { ...currentSnapState };
}

// 步骤1：获取对象的世界坐标边界框（强制更新矩阵）
function getObjectWorldBounds(object) {
  if (!object) return null;
  
  // 强制更新世界矩阵，确保边界框准确
  object.updateMatrixWorld();
  
  // 使用 Box3 计算世界坐标边界
  const box = new THREE.Box3().setFromObject(object);
  
  console.log('📦 边界框计算:', {
    min: { x: box.min.x.toFixed(2), z: box.min.z.toFixed(2) },
    max: { x: box.max.x.toFixed(2), z: box.max.z.toFixed(2) }
  });
  
  return {
    min: box.min,
    max: box.max,
    center: box.getCenter(new THREE.Vector3())
  };
}

// 步骤2：获取对象4条边的中点（世界坐标）
function getObjectEdgeMidpoints(object) {
  const bounds = getObjectWorldBounds(object);
  if (!bounds) return null;
  
  // 4条边的中点（XZ平面，Y=0）
  const edges = {
    front: {  // Z正向（前面）
      x: (bounds.min.x + bounds.max.x) / 2,
      z: bounds.max.z,
      name: 'front'
    },
    back: {   // Z负向（后面）
      x: (bounds.min.x + bounds.max.x) / 2,
      z: bounds.min.z,
      name: 'back'
    },
    left: {   // X负向（左面）
      x: bounds.min.x,
      z: (bounds.min.z + bounds.max.z) / 2,
      name: 'left'
    },
    right: {  // X正向（右面）
      x: bounds.max.x,
      z: (bounds.min.z + bounds.max.z) / 2,
      name: 'right'
    }
  };
  
  console.log('📐 边中点计算:', {
    front: `(${edges.front.x.toFixed(2)}, ${edges.front.z.toFixed(2)})`,
    back: `(${edges.back.x.toFixed(2)}, ${edges.back.z.toFixed(2)})`,
    left: `(${edges.left.x.toFixed(2)}, ${edges.left.z.toFixed(2)})`,
    right: `(${edges.right.x.toFixed(2)}, ${edges.right.z.toFixed(2)})`
  });
  
  return edges;
}

// 步骤3：检查对齐线吸附（重构版）
function checkAlignmentLineSnap(objectPosition, object, threshold = 10) {
  if (!objectPosition || !object || alignmentLines.length === 0) {
    return null;
  }
  
  // 获取4条边的中点
  const edges = getObjectEdgeMidpoints(object);
  if (!edges) return null;
  
  let bestSnap = null;
  let minDistance = threshold;
  
  // 遍历4条边
  for (const [edgeName, edgePoint] of Object.entries(edges)) {
    // 遍历所有对齐线
    for (const line of alignmentLines) {
      if (!line.visible) continue;
      
      const lineStart = line.originalStart;
      const lineEnd = line.originalEnd;
      
      // 创建向量
      const point = new THREE.Vector3(edgePoint.x, 0, edgePoint.z);
      const line0 = new THREE.Vector3(lineStart.x, 0, lineStart.z);
      const line1 = new THREE.Vector3(lineEnd.x, 0, lineEnd.z);
      
      // 计算点到无限长直线的投影（关键修复：使用直线而非线段）
      const lineVector = new THREE.Vector3().subVectors(line1, line0);
      const lineLength = lineVector.length();
      
      if (lineLength < 0.001) continue;
      
      const lineDir = lineVector.clone().normalize();
      const pointVector = new THREE.Vector3().subVectors(point, line0);
      const projection = pointVector.dot(lineDir);
      
      // 关键修复：始终使用投影点（不考虑线段端点限制）
      // 这样即使货架在对齐线延长线上也能触发吸附
      const closestPoint = new THREE.Vector3()
        .copy(line0)
        .add(lineDir.clone().multiplyScalar(projection));
      
      // 计算距离（点到直线的垂直距离）
      const distance = point.distanceTo(closestPoint);
      
      console.log(`🔍 检测: 边=${edgeName}, 距离=${distance.toFixed(2)}cm, 阈值=${threshold}cm`);
      
      // 记录最佳吸附
      if (distance < minDistance) {
        minDistance = distance;
        bestSnap = {
          edgeName: edgeName,
          edgePoint: edgePoint,
          snapPoint: closestPoint,
          lineId: line.id,
          lineName: line.name,
          offset: {
            x: closestPoint.x - edgePoint.x,
            z: closestPoint.z - edgePoint.z
          }
        };
      }
    }
  }
  
  if (bestSnap) {
    console.log('🎯 最佳吸附:', {
      edge: bestSnap.edgeName,
      distance: minDistance.toFixed(2) + 'cm',
      offset: `(${bestSnap.offset.x.toFixed(2)}, ${bestSnap.offset.z.toFixed(2)})`
    });
  }
  
  return bestSnap;
}

// 设置吸附配置
function setSnapConfig(config) {
  if (config.threshold !== undefined) {
    SNAP_CONFIG.threshold = config.threshold;
  }
  if (config.enabled !== undefined) {
    SNAP_CONFIG.enabled = config.enabled;
  }
}

// 获取吸附配置
function getSnapConfig() {
  return { ...SNAP_CONFIG };
}

// 子任务5.2: 吸附优先级与边界处理

// 用户操作意图跟踪
let userIntent = {
  preferredAxis: null, // 'x' | 'z' | null
  lastMoveDirection: new THREE.Vector3(),
  moveHistory: []
};

// 计算吸附优先级
// 优先级顺序：最近距离 > 轴向优先 > 用户意图
function calculateSnapPriority(distance, line, object, moveDirection) {
  if (!line || !object) return { score: Infinity, priority: 'none' };
  
  let score = distance; // 基础分数为距离
  let priority = 'distance';
  
  // 获取对齐线方向
  const lineDirection = new THREE.Vector3()
    .subVectors(line.endPoint, line.startPoint)
    .normalize();
  
  // 判断对齐线主要轴向 (X轴或Z轴)
  const isLineXAxis = Math.abs(lineDirection.x) > Math.abs(lineDirection.z);
  const isLineZAxis = Math.abs(lineDirection.z) > Math.abs(lineDirection.x);
  
  // 1. 轴向优先：如果移动方向与对齐线方向一致，降低分数（提高优先级）
  if (moveDirection && moveDirection.length() > 0) {
    const moveDirNormalized = moveDirection.clone().normalize();
    const isMoveXAxis = Math.abs(moveDirNormalized.x) > Math.abs(moveDirNormalized.z);
    const isMoveZAxis = Math.abs(moveDirNormalized.z) > Math.abs(moveDirNormalized.x);
    
    // 如果移动方向与对齐线方向匹配，给予优先级奖励
    if ((isLineXAxis && isMoveXAxis) || (isLineZAxis && isMoveZAxis)) {
      score *= 0.7; // 降低30%分数，提高优先级
      priority = 'axis';
    }
  }
  
  // 2. 用户意图优先：如果用户有偏好的轴向
  if (userIntent.preferredAxis) {
    const isPreferredX = userIntent.preferredAxis === 'x';
    const isPreferredZ = userIntent.preferredAxis === 'z';
    
    if ((isLineXAxis && isPreferredX) || (isLineZAxis && isPreferredZ)) {
      score *= 0.5; // 降低50%分数，最高优先级
      priority = 'intent';
    }
  }
  
  return { score, priority, isLineXAxis, isLineZAxis };
}

// 更新用户移动意图
function updateUserIntent(moveDelta) {
  if (!moveDelta || moveDelta.length() < 0.01) return;
  
  // 记录移动历史
  userIntent.moveHistory.push({
    direction: moveDelta.clone(),
    timestamp: Date.now()
  });
  
  // 只保留最近10次移动记录
  if (userIntent.moveHistory.length > 10) {
    userIntent.moveHistory.shift();
  }
  
  // 分析移动方向偏好
  const recentMoves = userIntent.moveHistory.slice(-5);
  let totalX = 0;
  let totalZ = 0;
  
  recentMoves.forEach(move => {
    totalX += Math.abs(move.direction.x);
    totalZ += Math.abs(move.direction.z);
  });
  
  // 如果某个方向的移动明显占优，记录为用户意图
  if (totalX > totalZ * 2) {
    userIntent.preferredAxis = 'x';
  } else if (totalZ > totalX * 2) {
    userIntent.preferredAxis = 'z';
  } else {
    userIntent.preferredAxis = null;
  }
  
  userIntent.lastMoveDirection = moveDelta.clone();
}

// 重置用户意图
function resetUserIntent() {
  userIntent = {
    preferredAxis: null,
    lastMoveDirection: new THREE.Vector3(),
    moveHistory: []
  };
}

// 处理边界吸附
function handleBoundarySnap(object, lines, moveDirection) {
  console.log('📐 handleBoundarySnap被调用，对齐线数量:', lines.length);
  
  if (!object || !lines || lines.length === 0) {
    console.log('❌ handleBoundarySnap提前返回：对象或对齐线为空');
    return { shouldSnap: false, line: null, position: null };
  }
  
  const bounds = getObjectBounds(object);
  if (!bounds) {
    console.log('❌ handleBoundarySnap提前返回：无法获取对象边界');
    return { shouldSnap: false, line: null, position: null };
  }
  
  const center = bounds.getCenter(new THREE.Vector3());
  // 投影到地面（Y=0），仓库布局是平面逻辑
  const centerOnGround = new THREE.Vector3(center.x, 0, center.z);
  console.log('📍 对象中心点（地面投影）:', centerOnGround.x, centerOnGround.z);
  console.log('📏 吸附阈值:', SNAP_CONFIG.threshold);
  
  const snapCandidates = [];
  
  // 评估每条对齐线的吸附优先级
  lines.forEach((line, index) => {
    console.log(`📊 检查对齐线 ${index}:`, line.name, 'visible:', line.visible);
    console.log(`   原始起点: (${line.originalStart.x}, ${line.originalStart.z})`);
    console.log(`   原始终点: (${line.originalEnd.x}, ${line.originalEnd.z})`);
    console.log(`   视觉起点: (${line.startPoint.x}, ${line.startPoint.z})`);
    console.log(`   视觉终点: (${line.endPoint.x}, ${line.endPoint.z})`);
    
    if (!line.visible) {
      console.log(`   ⏭️ 跳过：对齐线不可见`);
      return;
    }
    
    // 计算到对齐线的距离（使用原始端点和地面投影后的中心点）
    const distance = calculateDistanceToInfiniteLine(centerOnGround, line.originalStart, line.originalEnd);
    console.log(`   📏 计算距离（基于原始端点）: ${distance.toFixed(2)}cm`);
    
    // 只有在阈值内才考虑
    if (distance <= SNAP_CONFIG.threshold) {
      console.log(`   ✅ 距离在阈值内，加入候选`);
      const priority = calculateSnapPriority(distance, line, object, moveDirection);
      
      snapCandidates.push({
        line,
        distance,
        score: priority.score,
        priority: priority.priority,
        isLineXAxis: priority.isLineXAxis,
        isLineZAxis: priority.isLineZAxis
      });
    } else {
      console.log(`   ❌ 距离超出阈值 (${SNAP_CONFIG.threshold}cm)`);
    }
  });
  
  // 按分数排序（分数越低优先级越高）
  snapCandidates.sort((a, b) => a.score - b.score);
  
  console.log('📋 候选对齐线数量:', snapCandidates.length);
  if (snapCandidates.length > 0) {
    console.log('🏆 最佳候选距离:', snapCandidates[0].distance.toFixed(2), 'cm');
  }
  
  // 返回最佳吸附候选
  if (snapCandidates.length > 0) {
    const bestCandidate = snapCandidates[0];
    
    // 计算投影点（使用原始端点和地面投影后的中心点）
    const start = bestCandidate.line.originalStart;
    const end = bestCandidate.line.originalEnd;
    const lineVector = new THREE.Vector3().subVectors(end, start).normalize();
    const pointVector = new THREE.Vector3().subVectors(centerOnGround, start);
    const projectionDistance = pointVector.dot(lineVector);
    const projection = new THREE.Vector3().copy(start).add(lineVector.multiplyScalar(projectionDistance));
    
    console.log('✅ handleBoundarySnap返回：应该吸附');
    console.log('   投影点:', projection.x, projection.z);
    
    return {
      shouldSnap: true,
      line: bestCandidate.line,
      position: projection,
      distance: bestCandidate.distance,
      priority: bestCandidate.priority
    };
  }
  
  console.log('❌ handleBoundarySnap返回：无候选对齐线');
  return { shouldSnap: false, line: null, position: null };
}

// 取消吸附功能
let snapDisabled = false;
let snapDisableTimer = null;

function cancelSnap() {
  // 临时禁用吸附
  snapDisabled = true;
  
  // 清除当前吸附状态
  currentSnapState = {
    isSnapped: false,
    snappedLineId: null,
    snapPoint: null,
    originalPosition: null
  };
  
  // 清除用户意图
  resetUserIntent();
  
  // 3秒后自动恢复吸附功能
  if (snapDisableTimer) {
    clearTimeout(snapDisableTimer);
  }
  
  snapDisableTimer = setTimeout(() => {
    snapDisabled = false;
    console.log('吸附功能已恢复');
  }, 3000);
  
  console.log('吸附功能已临时取消（3秒）');
  return true;
}

// 检查吸附是否被禁用
function isSnapDisabled() {
  return snapDisabled;
}

// 恢复吸附功能
function enableSnap() {
  snapDisabled = false;
  if (snapDisableTimer) {
    clearTimeout(snapDisableTimer);
    snapDisableTimer = null;
  }
  console.log('吸附功能已手动恢复');
  return true;
}

// 子任务5.3: 对齐辅助提示

// 吸附指示器对象
let snapIndicator = null;
let snapIndicatorGroup = null;

// 创建吸附提示指示器
function createSnapIndicator() {
  // 如果已存在，先移除
  if (snapIndicatorGroup) {
    hideSnapIndicator();
  }
  
  // 创建指示器组
  snapIndicatorGroup = new THREE.Group();
  
  // 1. 创建中心点（绿色圆点）
  const centerGeometry = new THREE.SphereGeometry(3, 16, 16);
  const centerMaterial = new THREE.MeshBasicMaterial({
    color: 0x00ff00,
    transparent: true,
    opacity: 0.8
  });
  const centerDot = new THREE.Mesh(centerGeometry, centerMaterial);
  snapIndicatorGroup.add(centerDot);
  
  // 2. 创建外圈环（脉冲效果）
  const ringGeometry = new THREE.RingGeometry(5, 6, 32);
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: 0x00ff00,
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide
  });
  const ring = new THREE.Mesh(ringGeometry, ringMaterial);
  ring.rotation.x = -Math.PI / 2;
  snapIndicatorGroup.add(ring);
  
  // 3. 创建十字线
  const crossSize = 10;
  const crossGeometry = new THREE.BufferGeometry();
  const crossVertices = new Float32Array([
    -crossSize, 0, 0,  crossSize, 0, 0,  // X轴线
    0, 0, -crossSize,  0, 0, crossSize   // Z轴线
  ]);
  crossGeometry.setAttribute('position', new THREE.BufferAttribute(crossVertices, 3));
  const crossMaterial = new THREE.LineBasicMaterial({
    color: 0x00ff00,
    transparent: true,
    opacity: 0.7,
    linewidth: 2
  });
  const crossLines = new THREE.LineSegments(crossGeometry, crossMaterial);
  snapIndicatorGroup.add(crossLines);
  
  // 4. 创建距离文字标签（使用Sprite）
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 64;
  const context = canvas.getContext('2d');
  context.font = 'bold 24px Arial';
  context.fillStyle = '#00ff00';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText('已吸附', 64, 32);
  
  const texture = new THREE.CanvasTexture(canvas);
  const spriteMaterial = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    opacity: 0.9
  });
  const labelSprite = new THREE.Sprite(spriteMaterial);
  labelSprite.position.set(0, 15, 0);
  labelSprite.scale.set(30, 15, 1);
  snapIndicatorGroup.add(labelSprite);
  
  // 默认隐藏
  snapIndicatorGroup.visible = false;
  
  // 添加到场景
  scene.add(snapIndicatorGroup);
  
  return snapIndicatorGroup;
}

// 更新吸附提示
function updateSnapIndicator(position, line, distance) {
  if (!snapIndicatorGroup) {
    createSnapIndicator();
  }
  
  if (!position || !snapIndicatorGroup) return;
  
  // 更新位置
  snapIndicatorGroup.position.copy(position);
  // 确保指示器在地面上方
  snapIndicatorGroup.position.y = 5;
  
  // 显示指示器
  snapIndicatorGroup.visible = true;
  
  // 如果有距离信息，更新标签
  if (distance !== undefined) {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 64;
    const context = canvas.getContext('2d');
    context.font = 'bold 20px Arial';
    context.fillStyle = '#00ff00';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(`已吸附 ${distance.toFixed(1)}cm`, 64, 32);
    
    const texture = new THREE.CanvasTexture(canvas);
    const labelSprite = snapIndicatorGroup.children[3];
    if (labelSprite && labelSprite.material) {
      labelSprite.material.map = texture;
      labelSprite.material.needsUpdate = true;
    }
  }
  
  // 添加脉冲动画效果
  const ring = snapIndicatorGroup.children[1];
  if (ring) {
    // 简单的脉冲效果：缩放变化
    const time = Date.now() * 0.005;
    const scale = 1 + Math.sin(time) * 0.2;
    ring.scale.set(scale, scale, 1);
  }
}

// 隐藏吸附提示
function hideSnapIndicator() {
  if (snapIndicatorGroup) {
    snapIndicatorGroup.visible = false;
  }
}

// 销毁吸附提示（清理资源）
function destroySnapIndicator() {
  if (snapIndicatorGroup) {
    scene.remove(snapIndicatorGroup);
    snapIndicatorGroup.traverse(child => {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (child.material.map) child.material.map.dispose();
        child.material.dispose();
      }
    });
    snapIndicatorGroup = null;
  }
}

// 功能区规划相关
let zones = [];
let currentDrawTool = null;
let currentZoneType = 'storage';
let isDrawingZone = false;
let currentZonePoints = [];
let currentZoneMesh = null;
let zoneMaterials = {};

// 区域类型颜色映射
const zoneTypeColors = {
  receiving: 0x4CAF50, // 收货区 - 绿色
  storage: 0x2196F3,   // 存储区 - 蓝色
  shipping: 0xFF9800,  // 出库区 - 橙色
  picking: 0x9C27B0,   // 拣选区 - 紫色
  packing: 0xF44336,   // 打包区 - 红色
  office: 0x607D8B,    // 办公区 - 蓝灰色
  charging: 0xFFC107,  // 充电区 - 黄色
  other: 0x795548      // 其他 - 棕色
};

onMounted(() => {
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0e6);

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    45,
    container.value.clientWidth / container.value.clientHeight,
    1,
    50000
  );
  camera.position.set(500, 400, 500);

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  container.value.appendChild(renderer.domElement);

  // 添加轨道控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // 添加灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.9);
  directionalLight.position.set(5, 10, 7.5);
  scene.add(directionalLight);

  // 添加网格辅助线（默认20米 = 2000cm）
  const gridHelper = new THREE.GridHelper(2000, 20, 0xaaaaaa, 0xdddddd);
  gridHelper.name = 'gridHelper';
  scene.add(gridHelper);

  // 创建射线投射器
  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();

  // 添加事件监听
  window.addEventListener('resize', handleResize);
  container.value.addEventListener('click', onClick);
  container.value.addEventListener('mousedown', onMouseDown);
  container.value.addEventListener('mousemove', onMouseMove);
  container.value.addEventListener('mouseup', onMouseUp);
  
  // 添加拖放事件监听
  container.value.addEventListener('dragover', onDragOver);
  container.value.addEventListener('drop', onDrop);
  
  // 添加键盘事件监听
  window.addEventListener('keydown', onKeyDown);

  // 加载所有模型
  loadAllModels();

  // 初始化区域材质
  initZoneMaterials();

  // 开始渲染循环
  animate();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('keydown', onKeyDown);
  if (container.value) {
    container.value.removeEventListener('click', onClick);
    container.value.removeEventListener('mousedown', onMouseDown);
    container.value.removeEventListener('mousemove', onMouseMove);
    container.value.removeEventListener('mouseup', onMouseUp);
    container.value.removeEventListener('dragover', onDragOver);
    container.value.removeEventListener('drop', onDrop);
  }
});

// 更新相机位置
function updateCameraPosition(config) {
  if (!config || !camera || !controls) return;
  
  console.log('更新相机位置，warehouseConfig:', config);
  
  // 计算仓库中心点
  const centerX = 4000; // 默认中心
  const centerZ = 4000; // 默认中心
  
  // 设置相机位置（俯视仓库）
  const cameraHeight = 10000; // 100米高度
  camera.position.set(centerX, cameraHeight, centerZ);
  
  // 相机看向仓库中心
  camera.lookAt(centerX, 0, centerZ);
  
  // 更新控制器
  controls.target.set(centerX, 0, centerZ);
  controls.update();
  
  console.log('相机位置已更新:', camera.position.x, camera.position.y, camera.position.z);
  console.log('相机看向:', centerX, 0, centerZ);
}

// 监听warehouseConfig变化，更新相机位置
watch(() => props.warehouseConfig, (newConfig) => {
  console.log('warehouseConfig变化:', newConfig);
  if (newConfig && camera && controls) {
    updateCameraPosition(newConfig);
  }
}, { deep: true, immediate: true });

function handleResize() {
  if (camera && renderer && container.value) {
    camera.aspect = container.value.clientWidth / container.value.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  }
}

// ============================================
// 统一模型数据库（方案3）
// 包含所有对象的完整信息：短ID、长ID、中文名称、文件路径、参数
// ============================================
const modelDatabase = {
  // ========== 轻型货架（10个）==========
  'A15-4': {
    shortId: 'A15-4', longId: 'light-duty-A15-4',
    name: '4层轻型货架-L1.5xD0.4xH2.0',
    category: 'light-shelf', fileName: 'light-duty-A15-4.glb',
    params: { length: 1500, width: 400, height: 2000, levels: 4, type: 'shelf', color: 0x4169E1 }
  },
  'A15-5': {
    shortId: 'A15-5', longId: 'light-duty-A15-5',
    name: '5层轻型货架-L1.5xD0.4xH2.0',
    category: 'light-shelf', fileName: 'light-duty-A15-5.glb',
    params: { length: 1500, width: 400, height: 2000, levels: 5, type: 'shelf', color: 0x4169E1 }
  },
  'A20-4': {
    shortId: 'A20-4', longId: 'light-duty-A20-4',
    name: '4层轻型货架-L2.0xD0.6xH2.0',
    category: 'light-shelf', fileName: 'light-duty-A20-4.glb',
    params: { length: 2000, width: 600, height: 2000, levels: 4, type: 'shelf', color: 0x4169E1 }
  },
  'A20-5': {
    shortId: 'A20-5', longId: 'light-duty-A20-5',
    name: '5层轻型货架-L2.0xD0.6xH2.5',
    category: 'light-shelf', fileName: 'light-duty-A20-5.glb',
    params: { length: 2000, width: 600, height: 2500, levels: 5, type: 'shelf', color: 0x4169E1 }
  },
  'A20-6': {
    shortId: 'A20-6', longId: 'light-duty-A20-6',
    name: '6层轻型货架-L2.0xD0.6xH3.0',
    category: 'light-shelf', fileName: 'light-duty-A20-6.glb',
    params: { length: 2000, width: 600, height: 3000, levels: 6, type: 'shelf', color: 0x4169E1 }
  },
  'A15-4-pair': {
    shortId: 'A15-4-pair', longId: 'light-duty-A15-4-pair',
    name: '4层轻型货架-L1.5xD0.4xH2.0-配组',
    category: 'light-shelf', fileName: 'light-duty-A15-4-pair.glb',
    params: { length: 1500, width: 800, height: 2000, levels: 4, type: 'shelf', color: 0x4169E1 }
  },
  'A15-5-pair': {
    shortId: 'A15-5-pair', longId: 'light-duty-A15-5-pair',
    name: '5层轻型货架-L1.5xD0.4xH2.0-配组',
    category: 'light-shelf', fileName: 'light-duty-A15-5-pair.glb',
    params: { length: 1500, width: 800, height: 2000, levels: 5, type: 'shelf', color: 0x4169E1 }
  },
  'A20-4-pair': {
    shortId: 'A20-4-pair', longId: 'light-duty-A20-4-pair',
    name: '4层轻型货架-L2.0xD0.6xH2.0-配组',
    category: 'light-shelf', fileName: 'light-duty-A20-4-pair.glb',
    params: { length: 2000, width: 1200, height: 2000, levels: 4, type: 'shelf', color: 0x4169E1 }
  },
  'A20-5-pair': {
    shortId: 'A20-5-pair', longId: 'light-duty-A20-5-pair',
    name: '5层轻型货架-L2.0xD0.6xH2.5-配组',
    category: 'light-shelf', fileName: 'light-duty-A20-5-pair.glb',
    params: { length: 2000, width: 1200, height: 2500, levels: 5, type: 'shelf', color: 0x4169E1 }
  },
  'A20-6-pair': {
    shortId: 'A20-6-pair', longId: 'light-duty-A20-6-pair',
    name: '6层轻型货架-L2.0xD0.6xH3.0-配组',
    category: 'light-shelf', fileName: 'light-duty-A20-6-pair.glb',
    params: { length: 2000, width: 1200, height: 3000, levels: 6, type: 'shelf', color: 0x4169E1 }
  },

  // ========== 中型货架（8个）==========
  'B20-4': {
    shortId: 'B20-4', longId: 'medium-duty-B20-4',
    name: '4层中型货架-L2.0xD0.6xH2.0',
    category: 'medium-shelf', fileName: 'medium-duty-B20-4.glb',
    params: { length: 2000, width: 600, height: 2000, levels: 4, type: 'shelf', color: 0x00008B }
  },
  'B20-5': {
    shortId: 'B20-5', longId: 'medium-duty-B20-5',
    name: '5层中型货架-L2.0xD0.6xH2.5',
    category: 'medium-shelf', fileName: 'medium-duty-B20-5.glb',
    params: { length: 2000, width: 600, height: 2500, levels: 5, type: 'shelf', color: 0x00008B }
  },
  'B20-6': {
    shortId: 'B20-6', longId: 'medium-duty-B20-6',
    name: '6层中型货架-L2.0xD0.6xH3.0',
    category: 'medium-shelf', fileName: 'medium-duty-B20-6.glb',
    params: { length: 2000, width: 600, height: 3000, levels: 6, type: 'shelf', color: 0x00008B }
  },
  'C23-3': {
    shortId: 'C23-3', longId: 'high-duty-C23-3',
    name: '3层高位货架-L2.3xD1.0xH3.0',
    category: 'high-shelf', fileName: 'high-duty-C23-3.glb',
    params: { length: 2300, width: 1000, height: 3000, levels: 3, type: 'shelf', color: 0xFF4500 }
  },
  'B20-4-pair': {
    shortId: 'B20-4-pair', longId: 'medium-duty-B20-4-pair',
    name: '4层中型货架-L2.0xD0.6xH2.0-配组',
    category: 'medium-shelf', fileName: 'medium-duty-B20-4-pair.glb',
    params: { length: 2000, width: 1200, height: 2000, levels: 4, type: 'shelf', color: 0x00008B }
  },
  'B20-5-pair': {
    shortId: 'B20-5-pair', longId: 'medium-duty-B20-5-pair',
    name: '5层中型货架-L2.0xD0.6xH2.5-配组',
    category: 'medium-shelf', fileName: 'medium-duty-B20-5-pair.glb',
    params: { length: 2000, width: 1200, height: 2500, levels: 5, type: 'shelf', color: 0x00008B }
  },
  'B20-6-pair': {
    shortId: 'B20-6-pair', longId: 'medium-duty-B20-6-pair',
    name: '6层中型货架-L2.0xD0.6xH3.0-配组',
    category: 'medium-shelf', fileName: 'medium-duty-B20-6-pair.glb',
    params: { length: 2000, width: 1200, height: 3000, levels: 6, type: 'shelf', color: 0x00008B }
  },
  'C23-3-pair': {
    shortId: 'C23-3-pair', longId: 'high-duty-C23-3-pair',
    name: '3层高位货架-L2.3xD1.0xH3.0-配组',
    category: 'high-shelf', fileName: 'high-duty-C23-3-pair.glb',
    params: { length: 2300, width: 2000, height: 3000, levels: 3, type: 'shelf', color: 0xFF4500 }
  },

  // ========== 高位货架（22个）==========
  // C23系列
  'C23-4': {
    shortId: 'C23-4', longId: 'high-duty-C23-4',
    name: '4层高位货架-L2.3xD1.0xH4.5',
    category: 'heavy-shelf', fileName: 'high-duty-C23-4.glb',
    params: { length: 2300, width: 1000, height: 4500, levels: 4, type: 'shelf', color: 0xFF4500 }
  },
  'C23-5': {
    shortId: 'C23-5', longId: 'high-duty-C23-5',
    name: '5层高位货架-L2.3xD1.0xH6.0',
    category: 'heavy-shelf', fileName: 'high-duty-C23-5.glb',
    params: { length: 2300, width: 1000, height: 6000, levels: 5, type: 'shelf', color: 0xFF4500 }
  },
  'C23-6': {
    shortId: 'C23-6', longId: 'high-duty-C23-6',
    name: '6层高位货架-L2.3xD1.0xH7.0',
    category: 'heavy-shelf', fileName: 'high-duty-C23-6.glb',
    params: { length: 2300, width: 1000, height: 7000, levels: 6, type: 'shelf', color: 0xFF4500 }
  },
  'C23-4-pair': {
    shortId: 'C23-4-pair', longId: 'high-duty-C23-4-pair',
    name: '4层高位货架-L2.3xD1.0xH4.5-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C23-4-pair.glb',
    params: { length: 2300, width: 2000, height: 4500, levels: 4, type: 'shelf', color: 0xFF4500 }
  },
  'C23-5-pair': {
    shortId: 'C23-5-pair', longId: 'high-duty-C23-5-pair',
    name: '5层高位货架-L2.3xD1.0xH6.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C23-5-pair.glb',
    params: { length: 2300, width: 2000, height: 6000, levels: 5, type: 'shelf', color: 0xFF4500 }
  },
  'C23-6-pair': {
    shortId: 'C23-6-pair', longId: 'high-duty-C23-6-pair',
    name: '6层高位货架-L2.3xD1.0xH7.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C23-6-pair.glb',
    params: { length: 2300, width: 2000, height: 7000, levels: 6, type: 'shelf', color: 0xFF4500 }
  },
  // C25系列
  'C25-3': {
    shortId: 'C25-3', longId: 'high-duty-C25-3',
    name: '3层高位货架-L2.5xD1.0xH3.0',
    category: 'heavy-shelf', fileName: 'high-duty-C25-3.glb',
    params: { length: 2500, width: 1000, height: 3000, levels: 3, type: 'shelf', color: 0xFF4500 }
  },
  'C25-4': {
    shortId: 'C25-4', longId: 'high-duty-C25-4',
    name: '4层高位货架-L2.5xD1.0xH4.5',
    category: 'heavy-shelf', fileName: 'high-duty-C25-4.glb',
    params: { length: 2500, width: 1000, height: 4500, levels: 4, type: 'shelf', color: 0xFF4500 }
  },
  'C25-5': {
    shortId: 'C25-5', longId: 'high-duty-C25-5',
    name: '5层高位货架-L2.5xD1.0xH6.0',
    category: 'heavy-shelf', fileName: 'high-duty-C25-5.glb',
    params: { length: 2500, width: 1000, height: 6000, levels: 5, type: 'shelf', color: 0xFF4500 }
  },
  'C25-6': {
    shortId: 'C25-6', longId: 'high-duty-C25-6',
    name: '6层高位货架-L2.5xD1.0xH7.0',
    category: 'heavy-shelf', fileName: 'high-duty-C25-6.glb',
    params: { length: 2500, width: 1000, height: 7000, levels: 6, type: 'shelf', color: 0xFF4500 }
  },
  'C25-3-pair': {
    shortId: 'C25-3-pair', longId: 'high-duty-C25-3-pair',
    name: '3层高位货架-L2.5xD1.0xH3.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C25-3-pair.glb',
    params: { length: 2500, width: 2000, height: 3000, levels: 3, type: 'shelf', color: 0xFF4500 }
  },
  'C25-4-pair': {
    shortId: 'C25-4-pair', longId: 'high-duty-C25-4-pair',
    name: '4层高位货架-L2.5xD1.0xH4.5-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C25-4-pair.glb',
    params: { length: 2500, width: 2000, height: 4500, levels: 4, type: 'shelf', color: 0xFF4500 }
  },
  'C25-5-pair': {
    shortId: 'C25-5-pair', longId: 'high-duty-C25-5-pair',
    name: '5层高位货架-L2.5xD1.0xH6.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C25-5-pair.glb',
    params: { length: 2500, width: 2000, height: 6000, levels: 5, type: 'shelf', color: 0xFF4500 }
  },
  'C25-6-pair': {
    shortId: 'C25-6-pair', longId: 'high-duty-C25-6-pair',
    name: '6层高位货架-L2.5xD1.0xH7.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C25-6-pair.glb',
    params: { length: 2500, width: 2000, height: 7000, levels: 6, type: 'shelf', color: 0xFF4500 }
  },
  // C27系列
  'C27-3': {
    shortId: 'C27-3', longId: 'high-duty-C27-3',
    name: '3层高位货架-L2.7xD1.0xH3.0',
    category: 'heavy-shelf', fileName: 'high-duty-C27-3.glb',
    params: { length: 2700, width: 1000, height: 3000, levels: 3, type: 'shelf', color: 0xFF4500 }
  },
  'C27-4': {
    shortId: 'C27-4', longId: 'high-duty-C27-4',
    name: '4层高位货架-L2.7xD1.0xH4.5',
    category: 'heavy-shelf', fileName: 'high-duty-C27-4.glb',
    params: { length: 2700, width: 1000, height: 4500, levels: 4, type: 'shelf', color: 0xFF4500 }
  },
  'C27-5': {
    shortId: 'C27-5', longId: 'high-duty-C27-5',
    name: '5层高位货架-L2.7xD1.0xH6.0',
    category: 'heavy-shelf', fileName: 'high-duty-C27-5.glb',
    params: { length: 2700, width: 1000, height: 6000, levels: 5, type: 'shelf', color: 0xFF4500 }
  },
  'C27-6': {
    shortId: 'C27-6', longId: 'high-duty-C27-6',
    name: '6层高位货架-L2.7xD1.0xH7.0',
    category: 'heavy-shelf', fileName: 'high-duty-C27-6.glb',
    params: { length: 2700, width: 1000, height: 7000, levels: 6, type: 'shelf', color: 0xFF4500 }
  },
  'C27-3-pair': {
    shortId: 'C27-3-pair', longId: 'high-duty-C27-3-pair',
    name: '3层高位货架-L2.7xD1.0xH3.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C27-3-pair.glb',
    params: { length: 2700, width: 2000, height: 3000, levels: 3, type: 'shelf', color: 0xFF4500 }
  },
  'C27-4-pair': {
    shortId: 'C27-4-pair', longId: 'high-duty-C27-4-pair',
    name: '4层高位货架-L2.7xD1.0xH4.5-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C27-4-pair.glb',
    params: { length: 2700, width: 2000, height: 4500, levels: 4, type: 'shelf', color: 0xFF4500 }
  },
  'C27-5-pair': {
    shortId: 'C27-5-pair', longId: 'high-duty-C27-5-pair',
    name: '5层高位货架-L2.7xD1.0xH6.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C27-5-pair.glb',
    params: { length: 2700, width: 2000, height: 6000, levels: 5, type: 'shelf', color: 0xFF4500 }
  },
  'C27-6-pair': {
    shortId: 'C27-6-pair', longId: 'high-duty-C27-6-pair',
    name: '6层高位货架-L2.7xD1.0xH7.0-配组',
    category: 'heavy-shelf', fileName: 'high-duty-C27-6-pair.glb',
    params: { length: 2700, width: 2000, height: 7000, levels: 6, type: 'shelf', color: 0xFF4500 }
  },

  // ========== 其他货架（旧版兼容）==========
  'shelf-beam-heavy': {
    shortId: 'shelf-beam-heavy', longId: 'shelf-beam-heavy',
    name: 'A101 重型横梁式货架-5层重型',
    category: 'other-shelf', fileName: 'shelf-beam-heavy.glb',
    params: { length: 2700, width: 1000, height: 4500, levels: 5, type: 'shelf', color: 0xCC0000 }
  },
  'shelf-beam-medium': {
    shortId: 'shelf-beam-medium', longId: 'shelf-beam-medium',
    name: 'A102 横梁式货架-中型4层',
    category: 'other-shelf', fileName: 'shelf-beam-medium.glb',
    params: { length: 2000, width: 800, height: 3500, levels: 4, type: 'shelf', color: 0x4169E1 }
  },
  'shelf-drive-in': {
    shortId: 'shelf-drive-in', longId: 'shelf-drive-in',
    name: 'A103 驶入式货架-重型',
    category: 'other-shelf', fileName: 'shelf-drive-in.glb',
    params: { length: 3600, width: 1500, height: 6000, levels: 5, type: 'shelf', color: 0x8B4513 }
  },
  'shelf-flow-4level': {
    shortId: 'shelf-flow-4level', longId: 'shelf-flow-4level',
    name: 'A104 流利式货架-4层拣选',
    category: 'other-shelf', fileName: 'shelf-flow-4level.glb',
    params: { length: 900, width: 450, height: 1800, levels: 4, type: 'shelf', color: 0x98FB98 }
  },

  // ========== 载具容器（8个）==========
  'pallet-wooden-1200': {
    shortId: 'pallet-wooden-1200', longId: 'pallet-wooden-1200',
    name: 'C101 木质托盘 1200×1000mm',
    category: 'containers', fileName: 'pallet-wooden-1200.glb',
    params: { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0xD2691E }
  },
  'pallet-plastic-1200': {
    shortId: 'pallet-plastic-1200', longId: 'pallet-plastic-1200',
    name: 'C102 塑料托盘 1200×1000mm',
    category: 'containers', fileName: 'pallet-plastic-1200.glb',
    params: { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0x4169E1 }
  },
  'pallet-wood-1200x1000': {
    shortId: 'pallet-wood-1200x1000', longId: 'pallet-wood-1200x1000',
    name: 'C103 木质托盘-标准双向',
    category: 'containers', fileName: 'pallet-wood-1200x1000.glb',
    params: { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0x8B4513 }
  },
  'pallet-plastic-1200x1000': {
    shortId: 'pallet-plastic-1200x1000', longId: 'pallet-plastic-1200x1000',
    name: 'C104 塑料托盘-网格双面',
    category: 'containers', fileName: 'pallet-plastic-1200x1000.glb',
    params: { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0x4169E1 }
  },
  'container-foldable': {
    shortId: 'container-foldable', longId: 'container-foldable',
    name: 'C105 可折叠周转箱',
    category: 'containers', fileName: 'container-foldable.glb',
    params: { length: 600, width: 400, height: 340, type: 'container', color: 0x32CD32 }
  },
  'container-tote-600x400x300': {
    shortId: 'container-tote-600x400x300', longId: 'container-tote-600x400x300',
    name: 'C106 可堆叠周转箱-600×400×300',
    category: 'containers', fileName: 'container-tote-600x400.glb',
    params: { length: 600, width: 400, height: 300, type: 'container', color: 0x4169E1 }
  },
  'container-tote-600x400x220': {
    shortId: 'container-tote-600x400x220', longId: 'container-tote-600x400x220',
    name: 'C107 可堆叠周转箱-600×400×220',
    category: 'containers', fileName: 'container-tote-600x400-low.glb',
    params: { length: 600, width: 400, height: 220, type: 'container', color: 0x4169E1 }
  },
  'container-tote-400x300x150': {
    shortId: 'container-tote-400x300x150', longId: 'container-tote-400x300x150',
    name: 'C108 可堆叠周转箱-400×300×150',
    category: 'containers', fileName: 'container-tote-400x300.glb',
    params: { length: 400, width: 300, height: 150, type: 'container', color: 0x4169E1 }
  },

  // ========== 搬运设备（6个）==========
  'forklift-reach-2t': {
    shortId: 'forklift-reach-2t', longId: 'forklift-reach-2t',
    name: 'B101 前移式叉车-2吨9米',
    category: 'handling', fileName: 'forklift-reach-2t.glb',
    params: { length: 1200, width: 800, height: 2500, type: 'forklift', color: 0xFFD700 }
  },
  'forklift-counterbalance-2.5t': {
    shortId: 'forklift-counterbalance-2.5t', longId: 'forklift-counterbalance-2.5t',
    name: 'B102 平衡重叉车-2.5吨4米',
    category: 'handling', fileName: 'forklift-counterbalance-2.5t.glb',
    params: { length: 2500, width: 1200, height: 2200, type: 'forklift', color: 0xFFD700 }
  },
  'forklift-pallet-truck-electric': {
    shortId: 'forklift-pallet-truck-electric', longId: 'forklift-pallet-truck-electric',
    name: 'B103 电动搬运车-2吨步行式',
    category: 'handling', fileName: 'forklift-pallet-truck-electric.glb',
    params: { length: 1500, width: 700, height: 1200, type: 'forklift', color: 0xFFD700 }
  },
  'forklift-pallet-jack-manual': {
    shortId: 'forklift-pallet-jack-manual', longId: 'forklift-pallet-jack-manual',
    name: 'B104 手动液压搬运车-2.5吨',
    category: 'handling', fileName: 'forklift-pallet-jack-manual.glb',
    params: { length: 1200, width: 550, height: 1200, type: 'forklift', color: 0xFFD700 }
  },
  'cart-picking-3tier': {
    shortId: 'cart-picking-3tier', longId: 'cart-picking-3tier',
    name: 'B105 三层拣货车-标准型',
    category: 'handling', fileName: 'cart-picking-3tier.glb',
    params: { length: 800, width: 600, height: 1000, type: 'cart', color: 0x32CD32 }
  },
  'cart-cage-logistics-2tier': {
    shortId: 'cart-cage-logistics-2tier', longId: 'cart-cage-logistics-2tier',
    name: 'B106 物流笼车-2层标准款',
    category: 'handling', fileName: 'cart-cage-logistics-2tier.glb',
    params: { length: 800, width: 600, height: 1500, type: 'cart', color: 0x32CD32 }
  },

  // ========== 输送设备（3个）==========
  'lift-cargo-hydraulic-3floor': {
    shortId: 'lift-cargo-hydraulic-3floor', longId: 'lift-cargo-hydraulic-3floor',
    name: 'D101 液压升降平台-3层货物提升',
    category: 'conveying', fileName: 'lift-cargo-hydraulic-3floor.glb',
    params: { length: 2000, width: 1500, height: 8000, type: 'conveyor', color: 0xFF6347 }
  },
  'conveyor-curve-90degree-600': {
    shortId: 'conveyor-curve-90degree-600', longId: 'conveyor-curve-90degree-600',
    name: 'D102 90度转弯输送机-滚筒转弯',
    category: 'conveying', fileName: 'conveyor-curve-90degree-600.glb',
    params: { length: 1500, width: 1500, height: 800, type: 'conveyor', color: 0xFF6347 }
  },
  'conveyor-roller-straight-600-red': {
    shortId: 'conveyor-roller-straight-600-red', longId: 'conveyor-roller-straight-600-red',
    name: 'D103 动力滚筒输送机-标准直线型',
    category: 'conveying', fileName: 'conveyor-roller-straight-600-red.glb',
    params: { length: 2000, width: 600, height: 800, type: 'conveyor', color: 0xFF6347 }
  },

  // ========== 拣选设备（3个）==========
  'putwall-standard-16cell': {
    shortId: 'putwall-standard-16cell', longId: 'putwall-standard-16cell',
    name: 'E101 播种墙-16格位标准型',
    category: 'picking', fileName: 'putwall-standard-16cell.glb',
    params: { length: 1600, width: 500, height: 1800, type: 'picking', color: 0x9370DB }
  },
  'station-packcheck-integrated-red': {
    shortId: 'station-packcheck-integrated-red', longId: 'station-packcheck-integrated-red',
    name: 'E102 打包工作站-人体工学设计',
    category: 'picking', fileName: 'station-packcheck-integrated-red.glb',
    params: { length: 1800, width: 900, height: 2000, type: 'picking', color: 0xFF6347 }
  },
  'weigher-automatic-check-600-red': {
    shortId: 'weigher-automatic-check-600-red', longId: 'weigher-automatic-check-600-red',
    name: 'E103 自动称重机-600mm宽',
    category: 'picking', fileName: 'weigher-automatic-check-600-red.glb',
    params: { length: 1600, width: 700, height: 800, type: 'picking', color: 0xFF6347 }
  },

  // ========== 其他设备（2个）==========
  'guard-rack-heavy-redyellow': {
    shortId: 'guard-rack-heavy-redyellow', longId: 'guard-rack-heavy-redyellow',
    name: 'F101 货架防撞护栏-重型红黄警示',
    category: 'others', fileName: 'guard-rack-heavy-redyellow.glb',
    params: { length: 1500, width: 150, height: 400, type: 'guard', color: 0xFF4500 }
  },
  'guard-column-protector-redyellow': {
    shortId: 'guard-column-protector-redyellow', longId: 'guard-column-protector-redyellow',
    name: 'F102 立柱防撞护角-红黄警示',
    category: 'others', fileName: 'guard-column-protector-redyellow.glb',
    params: { length: 120, width: 120, height: 400, type: 'guard', color: 0xFF4500 }
  },

  // ========== 人员（1个）==========
  'person-warehouse-admin-red': {
    shortId: 'person-warehouse-admin-red', longId: 'person-warehouse-admin-red',
    name: 'G101 仓库管理员-标准工作人员',
    category: 'personnel', fileName: 'person-warehouse-admin-red.glb',
    params: { length: 450, width: 300, height: 1750, type: 'person', color: 0xFF69B4 }
  }
};

// 向后兼容：保留旧版长ID映射（用于加载旧项目）
const longIdToShortIdMap = {};
Object.values(modelDatabase).forEach(model => {
  if (model.longId !== model.shortId) {
    longIdToShortIdMap[model.longId] = model.shortId;
  }
});

// 辅助函数：获取模型信息（支持短ID和长ID）
function getModelInfo(modelId) {
  // 先尝试短ID
  if (modelDatabase[modelId]) {
    return modelDatabase[modelId];
  }
  // 再尝试长ID转换
  const shortId = longIdToShortIdMap[modelId];
  if (shortId && modelDatabase[shortId]) {
    return modelDatabase[shortId];
  }
  // 未找到返回null
  return null;
}

// 辅助函数：获取模型文件路径
function getModelFilePath(modelId) {
  const model = getModelInfo(modelId);
  return model ? `/assets/models/${model.fileName}` : null;
}

// 辅助函数：获取模型显示名称
function getModelDisplayName(modelId) {
  const model = getModelInfo(modelId);
  return model ? model.name : modelId;
}

// 辅助函数：获取模型参数
function getModelParams(modelId) {
  const model = getModelInfo(modelId);
  return model ? model.params : null;
}

// 加载所有模型
function loadAllModels() {
  loader = new GLTFLoader();
  
  // 从 modelDatabase 加载所有模型
  Object.values(modelDatabase).forEach((model) => {
    loadModel(model.longId, model.fileName);
  });
}

function loadModel(modelId, fileName) {
  if (models[modelId]) {
    return models[modelId];
  }

  // 添加时间戳清除缓存
  const cacheBuster = `?t=${Date.now()}`;
  
  // COS配置 - 从腾讯云COS加载模型
  const COS_URL = 'https://cangkujia-models-1405539235.cos.ap-shanghai.myqcloud.com/standard';
  const isProduction = window.location.hostname === 'cangkujia666.com';
  const modelUrl = isProduction 
    ? `${COS_URL}/${fileName}${cacheBuster}`
    : `/assets/models/${fileName}${cacheBuster}`;
  
  loader.load(
    modelUrl,
    (gltf) => {
      const model = gltf.scene;
      
      // GLB模型已经通过Trimesh导出时应用了旋转（-90度绕X轴）
      // 所以不需要再次旋转，直接调整位置使底部与地面平齐
      
      // 处理材质 - 使用MeshBasicMaterial以正确显示顶点颜色
      model.traverse((child) => {
        if (child.isMesh) {
          if (child.geometry.attributes.color) {
            child.material = new THREE.MeshBasicMaterial({ vertexColors: true });
          } else {
            // 保留原始材质的颜色
            const originalColor = child.material ? child.material.color : new THREE.Color(0x888888);
            child.material = new THREE.MeshBasicMaterial({ color: originalColor });
          }
        }
      });
      
      // 缩放模型（GLB导出时使用mm单位，Three.js使用米单位，需要缩小100倍）
      model.scale.set(0.1, 0.1, 0.1);
      
      // 【关键修复】强制更新所有几何体的边界框
      model.traverse((child) => {
        if (child.isMesh && child.geometry) {
          child.geometry.computeBoundingBox();
          child.geometry.computeBoundingSphere();
        }
      });
      
      // 缩放后重新计算模型的边界框
      const box = new THREE.Box3().setFromObject(model);
      
      // 调整模型位置，使底部与地面平齐（Y=0）
      const offsetY = -box.min.y;
      model.position.y = offsetY;
      
      // 存储模型
      models[modelId] = model;
      console.log('模型加载成功:', modelId, fileName, '尺寸:', box.getSize(new THREE.Vector3()));
    },
    (xhr) => {
      // 加载进度
      if (xhr.total > 0) {
        const percent = (xhr.loaded / xhr.total * 100).toFixed(0);
        if (percent === '100') {
          console.log(`${modelId}: ${percent}%`);
        }
      }
    },
    (error) => {
      console.error('模型加载失败:', modelId, fileName, error);
    }
  );
}

function createDirectionLabels() {
  // 坐标轴长度 - 扩大到50米（5000cm）
  const axisLength = 5000;
  const arrowSize = 200;
  const labelSize = 300;

  // 创建坐标轴线
  const axisMaterial = new THREE.LineBasicMaterial({ 
    color: 0x666666, 
    linewidth: 2,
    transparent: true,
    opacity: 0.6
  });

  // X轴线
  const xAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(-axisLength, 10, 0),
    new THREE.Vector3(axisLength, 10, 0)
  ]);
  const xAxis = new THREE.Line(xAxisGeometry, new THREE.LineBasicMaterial({ color: 0xff4444, linewidth: 3 }));
  scene.add(xAxis);

  // Z轴线
  const zAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 10, -axisLength),
    new THREE.Vector3(0, 10, axisLength)
  ]);
  const zAxis = new THREE.Line(zAxisGeometry, new THREE.LineBasicMaterial({ color: 0x4444ff, linewidth: 3 }));
  scene.add(zAxis);

  // 创建箭头几何体
  const arrowShape = new THREE.Shape();
  arrowShape.moveTo(0, arrowSize * 0.6);
  arrowShape.lineTo(arrowSize * 0.4, 0);
  arrowShape.lineTo(arrowSize * 0.2, 0);
  arrowShape.lineTo(arrowSize * 0.2, -arrowSize * 0.6);
  arrowShape.lineTo(-arrowSize * 0.2, -arrowSize * 0.6);
  arrowShape.lineTo(-arrowSize * 0.2, 0);
  arrowShape.lineTo(-arrowSize * 0.4, 0);
  arrowShape.lineTo(0, arrowSize * 0.6);

  const arrowGeometry = new THREE.ShapeGeometry(arrowShape);

  // X轴正方向箭头（红色）
  const xPosArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff4444 }));
  xPosArrow.position.set(axisLength, 10, 0);
  xPosArrow.rotation.x = -Math.PI / 2;
  xPosArrow.rotation.z = -Math.PI / 2;
  scene.add(xPosArrow);

  // X轴负方向箭头（红色）
  const xNegArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff4444 }));
  xNegArrow.position.set(-axisLength, 10, 0);
  xNegArrow.rotation.x = -Math.PI / 2;
  xNegArrow.rotation.z = Math.PI / 2;
  scene.add(xNegArrow);

  // Z轴正方向箭头（蓝色）
  const zPosArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x4444ff }));
  zPosArrow.position.set(0, 10, axisLength);
  zPosArrow.rotation.x = -Math.PI / 2;
  zPosArrow.rotation.z = Math.PI;
  scene.add(zPosArrow);

  // Z轴负方向箭头（蓝色）
  const zNegArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x4444ff }));
  zNegArrow.position.set(0, 10, -axisLength);
  zNegArrow.rotation.x = -Math.PI / 2;
  scene.add(zNegArrow);

  // 添加刻度标记 - 每1米一个短刻度，每10米一个长刻度+标签
  const tickMaterial = new THREE.LineBasicMaterial({ color: 0x666666, transparent: true, opacity: 0.5 });
  const majorTickMaterial = new THREE.LineBasicMaterial({ color: 0x444444, transparent: true, opacity: 0.7 });
  
  // X轴刻度（正方向和负方向）
  for (let i = 100; i <= axisLength; i += 100) { // 每1米=100cm
    const isMajor = i % 1000 === 0; // 每10米为长刻度
    const tickLength = isMajor ? 150 : 80;
    const tickMaterialToUse = isMajor ? majorTickMaterial : tickMaterial;
    
    // X轴正方向刻度
    const xPosTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(i, 10, -tickLength / 2),
      new THREE.Vector3(i, 10, tickLength / 2)
    ]);
    const xPosTick = new THREE.Line(xPosTickGeometry, tickMaterialToUse);
    scene.add(xPosTick);
    
    // X轴负方向刻度
    const xNegTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-i, 10, -tickLength / 2),
      new THREE.Vector3(-i, 10, tickLength / 2)
    ]);
    const xNegTick = new THREE.Line(xNegTickGeometry, tickMaterialToUse);
    scene.add(xNegTick);
    
    // 每10米添加数字标签（只在正方向）
    if (isMajor && i > 0) {
      const labelCanvas = document.createElement('canvas');
      const labelContext = labelCanvas.getContext('2d');
      labelCanvas.width = 128;
      labelCanvas.height = 64;
      
      labelContext.font = 'bold 40px Arial';
      labelContext.fillStyle = '#666666';
      labelContext.textAlign = 'center';
      labelContext.textBaseline = 'middle';
      labelContext.fillText(`${i / 100}m`, 64, 32);
      
      const labelTexture = new THREE.CanvasTexture(labelCanvas);
      const labelMaterial = new THREE.SpriteMaterial({ map: labelTexture, transparent: true });
      const labelSprite = new THREE.Sprite(labelMaterial);
      labelSprite.position.set(i, 10, 250);
      labelSprite.scale.set(300, 150, 1);
      scene.add(labelSprite);
      
      // Z轴标签
      const zLabelSprite = new THREE.Sprite(labelMaterial);
      zLabelSprite.position.set(250, 10, i);
      zLabelSprite.scale.set(300, 150, 1);
      scene.add(zLabelSprite);
    }
  }
  
  // Z轴刻度（正方向和负方向）
  for (let i = 100; i <= axisLength; i += 100) { // 每1米=100cm
    const isMajor = i % 1000 === 0; // 每10米为长刻度
    const tickLength = isMajor ? 150 : 80;
    const tickMaterialToUse = isMajor ? majorTickMaterial : tickMaterial;
    
    // Z轴正方向刻度
    const zPosTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-tickLength / 2, 10, i),
      new THREE.Vector3(tickLength / 2, 10, i)
    ]);
    const zPosTick = new THREE.Line(zPosTickGeometry, tickMaterialToUse);
    scene.add(zPosTick);
    
    // Z轴负方向刻度
    const zNegTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-tickLength / 2, 10, -i),
      new THREE.Vector3(tickLength / 2, 10, -i)
    ]);
    const zNegTick = new THREE.Line(zNegTickGeometry, tickMaterialToUse);
    scene.add(zNegTick);
  }

  // 添加字母标识 - 更大更清晰
  const labels = [
    { text: 'X+', pos: [axisLength + labelSize, 100, 0], color: '#ff4444' },
    { text: 'X-', pos: [-axisLength - labelSize, 100, 0], color: '#ff4444' },
    { text: 'Z+', pos: [0, 100, axisLength + labelSize], color: '#4444ff' },
    { text: 'Z-', pos: [0, 100, -axisLength - labelSize], color: '#4444ff' }
  ];

  labels.forEach(label => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 256;

    // 绘制背景圆
    context.beginPath();
    context.arc(128, 128, 120, 0, Math.PI * 2);
    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
    context.fill();
    context.lineWidth = 8;
    context.strokeStyle = label.color;
    context.stroke();

    // 绘制文字
    context.font = 'bold 120px Arial';
    context.fillStyle = label.color;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(label.text, 128, 128);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(...label.pos);
    sprite.scale.set(400, 400, 1);

    scene.add(sprite);
  });

  console.log('方向标识已创建，范围:', axisLength, 'cm，包含刻度标记');
}

// 更新方向标识位置到仓库中心
let directionLabelsGroup = null;

function updateDirectionLabels(centerX, y, centerZ, warehouseSize) {
  // 如果已存在方向标识组，先移除
  if (directionLabelsGroup) {
    scene.remove(directionLabelsGroup);
  }
  
  // 创建新的方向标识组
  directionLabelsGroup = new THREE.Group();
  
  // 坐标轴长度 - 根据仓库大小调整
  const axisLength = Math.max(5000, warehouseSize * 1.5);
  const arrowSize = Math.min(200, warehouseSize * 0.05);
  const labelSize = Math.min(300, warehouseSize * 0.08);
  
  // X轴线（红色）
  const xAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(centerX - axisLength, y, centerZ),
    new THREE.Vector3(centerX + axisLength, y, centerZ)
  ]);
  const xAxis = new THREE.Line(xAxisGeometry, new THREE.LineBasicMaterial({ color: 0xff4444, linewidth: 3 }));
  directionLabelsGroup.add(xAxis);
  
  // Z轴线（蓝色）
  const zAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(centerX, y, centerZ - axisLength),
    new THREE.Vector3(centerX, y, centerZ + axisLength)
  ]);
  const zAxis = new THREE.Line(zAxisGeometry, new THREE.LineBasicMaterial({ color: 0x4444ff, linewidth: 3 }));
  directionLabelsGroup.add(zAxis);
  
  // 创建箭头
  const arrowShape = new THREE.Shape();
  arrowShape.moveTo(0, arrowSize * 0.6);
  arrowShape.lineTo(arrowSize * 0.4, 0);
  arrowShape.lineTo(arrowSize * 0.2, 0);
  arrowShape.lineTo(arrowSize * 0.2, -arrowSize * 0.6);
  arrowShape.lineTo(-arrowSize * 0.2, -arrowSize * 0.6);
  arrowShape.lineTo(-arrowSize * 0.2, 0);
  arrowShape.lineTo(-arrowSize * 0.4, 0);
  arrowShape.lineTo(0, arrowSize * 0.6);
  
  const arrowGeometry = new THREE.ShapeGeometry(arrowShape);
  
  // X+箭头
  const xPosArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff4444 }));
  xPosArrow.position.set(centerX + axisLength, y, centerZ);
  xPosArrow.rotation.x = -Math.PI / 2;
  xPosArrow.rotation.z = -Math.PI / 2;
  directionLabelsGroup.add(xPosArrow);
  
  // X-箭头
  const xNegArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff4444 }));
  xNegArrow.position.set(centerX - axisLength, y, centerZ);
  xNegArrow.rotation.x = -Math.PI / 2;
  xNegArrow.rotation.z = Math.PI / 2;
  directionLabelsGroup.add(xNegArrow);
  
  // Z+箭头
  const zPosArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x4444ff }));
  zPosArrow.position.set(centerX, y, centerZ + axisLength);
  zPosArrow.rotation.x = -Math.PI / 2;
  zPosArrow.rotation.z = Math.PI;
  directionLabelsGroup.add(zPosArrow);
  
  // Z-箭头
  const zNegArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x4444ff }));
  zNegArrow.position.set(centerX, y, centerZ - axisLength);
  zNegArrow.rotation.x = -Math.PI / 2;
  directionLabelsGroup.add(zNegArrow);
  
  // 添加刻度标记 - 每1米一个短刻度，每10米一个长刻度+标签
  const tickMaterial = new THREE.LineBasicMaterial({ color: 0x666666, transparent: true, opacity: 0.5 });
  const majorTickMaterial = new THREE.LineBasicMaterial({ color: 0x444444, transparent: true, opacity: 0.7 });
  
  // X轴刻度（相对于仓库中心）
  for (let i = 100; i <= axisLength; i += 100) { // 每1米=100cm
    const isMajor = i % 1000 === 0; // 每10米为长刻度
    const tickLength = isMajor ? 150 : 80;
    const tickMaterialToUse = isMajor ? majorTickMaterial : tickMaterial;
    
    // X轴正方向刻度
    const xPosTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(centerX + i, y, centerZ - tickLength / 2),
      new THREE.Vector3(centerX + i, y, centerZ + tickLength / 2)
    ]);
    const xPosTick = new THREE.Line(xPosTickGeometry, tickMaterialToUse);
    directionLabelsGroup.add(xPosTick);
    
    // X轴负方向刻度
    const xNegTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(centerX - i, y, centerZ - tickLength / 2),
      new THREE.Vector3(centerX - i, y, centerZ + tickLength / 2)
    ]);
    const xNegTick = new THREE.Line(xNegTickGeometry, tickMaterialToUse);
    directionLabelsGroup.add(xNegTick);
    
    // 每10米添加数字标签（只在正方向）
    if (isMajor && i > 0) {
      const labelCanvas = document.createElement('canvas');
      const labelContext = labelCanvas.getContext('2d');
      labelCanvas.width = 128;
      labelCanvas.height = 64;
      
      labelContext.font = 'bold 40px Arial';
      labelContext.fillStyle = '#666666';
      labelContext.textAlign = 'center';
      labelContext.textBaseline = 'middle';
      labelContext.fillText(`${i / 100}m`, 64, 32);
      
      const labelTexture = new THREE.CanvasTexture(labelCanvas);
      const labelMaterial = new THREE.SpriteMaterial({ map: labelTexture, transparent: true });
      
      // X轴标签
      const xLabelSprite = new THREE.Sprite(labelMaterial);
      xLabelSprite.position.set(centerX + i, y, centerZ + 250);
      xLabelSprite.scale.set(300, 150, 1);
      directionLabelsGroup.add(xLabelSprite);
      
      // Z轴标签
      const zLabelSprite = new THREE.Sprite(labelMaterial);
      zLabelSprite.position.set(centerX + 250, y, centerZ + i);
      zLabelSprite.scale.set(300, 150, 1);
      directionLabelsGroup.add(zLabelSprite);
    }
  }
  
  // Z轴刻度（相对于仓库中心）
  for (let i = 100; i <= axisLength; i += 100) { // 每1米=100cm
    const isMajor = i % 1000 === 0; // 每10米为长刻度
    const tickLength = isMajor ? 150 : 80;
    const tickMaterialToUse = isMajor ? majorTickMaterial : tickMaterial;
    
    // Z轴正方向刻度
    const zPosTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(centerX - tickLength / 2, y, centerZ + i),
      new THREE.Vector3(centerX + tickLength / 2, y, centerZ + i)
    ]);
    const zPosTick = new THREE.Line(zPosTickGeometry, tickMaterialToUse);
    directionLabelsGroup.add(zPosTick);
    
    // Z轴负方向刻度
    const zNegTickGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(centerX - tickLength / 2, y, centerZ - i),
      new THREE.Vector3(centerX + tickLength / 2, y, centerZ - i)
    ]);
    const zNegTick = new THREE.Line(zNegTickGeometry, tickMaterialToUse);
    directionLabelsGroup.add(zNegTick);
  }
  
  // 添加标签
  const labels = [
    { text: 'X+', pos: [centerX + axisLength + labelSize, y + labelSize * 0.3, centerZ], color: '#ff4444' },
    { text: 'X-', pos: [centerX - axisLength - labelSize, y + labelSize * 0.3, centerZ], color: '#ff4444' },
    { text: 'Z+', pos: [centerX, y + labelSize * 0.3, centerZ + axisLength + labelSize], color: '#4444ff' },
    { text: 'Z-', pos: [centerX, y + labelSize * 0.3, centerZ - axisLength - labelSize], color: '#4444ff' }
  ];
  
  labels.forEach(label => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 256;
    
    context.beginPath();
    context.arc(128, 128, 120, 0, Math.PI * 2);
    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
    context.fill();
    context.lineWidth = 8;
    context.strokeStyle = label.color;
    context.stroke();
    
    context.font = 'bold 120px Arial';
    context.fillStyle = label.color;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(label.text, 128, 128);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(...label.pos);
    sprite.scale.set(labelSize * 1.3, labelSize * 1.3, 1);
    
    directionLabelsGroup.add(sprite);
  });
  
  scene.add(directionLabelsGroup);
  console.log('方向标识已更新到仓库中心:', { x: centerX, z: centerZ }, '包含刻度标记');
}

// 键盘事件处理
function onKeyDown(event) {
  // 如果正在输入，不处理快捷键
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
    return;
  }
  
  // Ctrl+S 保存项目
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault();
    emit('save-project');
    return;
  }
  
  // Delete键删除选中对象
  if (event.key === 'Delete' || event.key === 'Backspace') {
    if (selectedObjects.length > 0) {
      deleteSelectedObjects();
    }
    return;
  }
  
  // Esc取消选择或取消对齐线绘制
  if (event.key === 'Escape') {
    if (isDrawingAlignmentLine) {
      cancelDrawingAlignmentLine();
    } else {
      clearSelection();
    }
    return;
  }
}

// 删除选中对象
function deleteSelectedObjects() {
  selectedObjects.forEach(obj => {
    const index = sceneObjects.indexOf(obj);
    if (index > -1) {
      obj.traverse((child) => {
        if (child.material && child.material.emissive) {
          child.material.emissive.setHex(0x000000);
        }
      });
      scene.remove(obj);
      sceneObjects.splice(index, 1);
    }
  });
  
  selectedObjects = [];
  selectedObject = null;
  hideRotationRing();
  cornerMarkers.forEach(marker => scene.remove(marker));
  cornerMarkers = [];
  emit('object-deselected');
}

// 复制选中对象
function copySelectedObject() {
  if (selectedObjects.length === 0) return null;
  
  const originalObj = selectedObjects[0];
  let copiedObj = null;
  
  // 获取对象类型和参数
  const modelType = originalObj.userData.modelType || originalObj.userData.modelId;
  const params = originalObj.userData.params;
  
  if (modelType) {
    // 在右侧偏移位置创建副本
    const offsetX = 50; // 50cm 偏移
    const newPosition = {
      x: originalObj.position.x + offsetX,
      y: originalObj.position.y,
      z: originalObj.position.z
    };
    
    // 使用相同的参数创建新对象
    if (params) {
      copiedObj = createDetailedModel(modelType, newPosition);
    } else {
      // 如果是门或窗等特殊对象
      if (originalObj.userData.type === 'door' || originalObj.userData.type === 'window') {
        // 门和窗需要特殊处理，暂时不支持复制
        console.log('门和窗暂不支持复制');
        return null;
      }
      copiedObj = createDetailedModel(modelType, newPosition);
    }
    
    if (copiedObj) {
      // 复制旋转
      copiedObj.rotation.copy(originalObj.rotation);
      
      // 选中新对象
      clearSelection();
      selectObject(copiedObj);
      
      console.log('对象已复制:', modelType, '新位置:', newPosition);
    }
  }
  
  return copiedObj;
}

function onClick(event) {
  // 处理区域绘制点击
  if (isDrawingZone) {
    handleZoneClick(event);
    return;
  }
  
  // 处理对齐线绘制
  if (isDrawingAlignmentLine) {
    const rect = container.value.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    
    // 强制与地面Y=0平面相交（正确做法）
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查：防止天文数字坐标
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 坐标异常，拒绝创建对齐线:', intersectPoint);
        return; // 阻止创建，避免垃圾数据
      }
      
      console.log('🎯 射线与地面交点:', intersectPoint.x, intersectPoint.z);
      
      if (!alignmentLineStartPoint) {
        // 开始点
        alignmentLineStartPoint = intersectPoint.clone();
        console.log('✅ 对齐线开始点:', alignmentLineStartPoint.x, alignmentLineStartPoint.z);
      } else {
        // 结束点，创建对齐线
        const endPoint = intersectPoint.clone();
        
        // 防御性检查：确保终点坐标也正常
        if (Math.abs(endPoint.x) > 100000 || Math.abs(endPoint.z) > 100000) {
          console.error('❌ 终点坐标异常，拒绝创建对齐线:', endPoint);
          return;
        }
        
        console.log('✅ 对齐线结束点:', endPoint.x, endPoint.z);
        addAlignmentLine(alignmentLineStartPoint, endPoint);
        alignmentLineStartPoint = null;
        clearAlignmentLinePreview();
        console.log('对齐线创建完成');
      }
    } else {
      console.error('❌ 射线与地面平面无交点');
    }
    return;
  }
  
  // 处理测量模式
  if (isMeasuring) {
    const rect = container.value.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    
    // 强制与地面Y=0平面相交
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查：防止天文数字坐标
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 坐标异常，拒绝测量:', intersectPoint);
        return;
      }
      
      if (!measureStartPoint) {
        // 第一点
        measureStartPoint = intersectPoint.clone();
        measureEndPoint = intersectPoint.clone();
        createMeasureLine(measureStartPoint, measureEndPoint);
        console.log('✅ 测量第一点:', measureStartPoint.x, measureStartPoint.z);
      } else {
        // 第二点，完成测量
        measureEndPoint = intersectPoint.clone();
        updateMeasureLine(measureEndPoint);
        
        // 计算距离
        const distance = measureStartPoint.distanceTo(measureEndPoint);
        console.log('✅ 测量第二点:', measureEndPoint.x, measureEndPoint.z);
        console.log('📏 测量距离:', distance, 'cm');
        
        // 显示结果
        showMeasureResult(distance);
        
        // 重置测量状态，准备下一次测量
        measureStartPoint = null;
        measureEndPoint = null;
        
        // 10秒后清除测量线
        setTimeout(() => {
          clearMeasureLine();
        }, 10000);
      }
    }
    return;
  }
  
  // 处理距离线模式 - 选择起点或确定终点
  if (isDistanceLineMode) {
    console.log('【关键-debug】onClick 距离线模式，isDistanceLineWaitingForEnd =', isDistanceLineWaitingForEnd);
    const rect = container.value.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    
    // 与地面Y=0平面相交
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 坐标异常，拒绝距离线:', intersectPoint);
        return;
      }
      
      if (!isDistanceLineWaitingForEnd) {
        // 选择起点
        distanceLineStartPoint = intersectPoint.clone();
        console.log('【关键-debug】选择起点:', distanceLineStartPoint.x, distanceLineStartPoint.z);
        console.log('【关键-debug】触发弹窗显示');
        
        // 触发弹窗显示（通过emit通知CoreFunction）
        emit('show-distance-line-dialog');
      } else {
        // 确定终点，创建距离线
        console.log('【关键-debug】确定终点，创建距离线');
        confirmDistanceLine();
      }
    }
    return;
  }
  
  const rect = container.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  
  // 检查是否点击了墙体（用于添加门窗）
  const wallIntersects = raycaster.intersectObjects(
    sceneObjects.filter(obj => obj.userData.type === 'wall'),
    false
  );

  if (wallIntersects.length > 0 && (props.addingDoor || props.addingWindow)) {
    const wall = wallIntersects[0].object;
    const wallIndex = wall.userData.wallIndex;
    const intersectPoint = wallIntersects[0].point;

    // 计算点击位置在墙体上的相对位置（从墙体中心开始的距离）
    const wallCenter = wall.position.clone();
    const wallDirection = new THREE.Vector3(
      Math.cos(-wall.rotation.y),
      0,
      Math.sin(-wall.rotation.y)
    );

    // 计算点击点相对于墙体中心的偏移
    const toIntersect = new THREE.Vector3().subVectors(intersectPoint, wallCenter);
    const position = toIntersect.dot(wallDirection) / 100; // 转换为米

    if (props.addingDoor) {
      emit('add-door', wallIndex, position);
    } else if (props.addingWindow) {
      emit('add-window', wallIndex, position);
    }
    return;
  }
  
  // 处理移动模式（点击事件中的备用逻辑）
  // 【注意】主要移动逻辑在 onMouseMove 中处理，这里保留作为备用
  if (isMoving && selectedObjects.length > 0) {
    if (raycaster.ray.intersectPlane(movePlane, moveIntersectPoint)) {
      moveSelectedObjects(moveIntersectPoint.sub(moveOffset));
    }
    return;
  }
  
  const intersects = raycaster.intersectObjects(sceneObjects, true);
  
  console.log('点击检测:', intersects.length, '个对象', 'sceneObjects数量:', sceneObjects.length);
  
  // 输出所有相交对象的信息
  intersects.forEach((intersect, index) => {
    const obj = intersect.object;
    let rootObj = obj;
    while (rootObj.parent && rootObj.parent !== scene) {
      rootObj = rootObj.parent;
    }
    console.log(`相交对象[${index}]:`, 
                '距离:', intersect.distance, 
                '类型:', obj.userData.type || '未知',
                '根对象类型:', rootObj.userData.type || '未知',
                '根对象modelType:', rootObj.userData.modelType || 'N/A');
  });
  
  if (intersects.length > 0) {
    // 优先查找门/窗/外墙标语对象（它们可能在墙体后面，但应该优先被选中）
    let targetObject = null;
    let targetRootObject = null;
    
    for (const intersect of intersects) {
      let rootObj = intersect.object;
      while (rootObj.parent && rootObj.parent !== scene) {
        rootObj = rootObj.parent;
      }
      // 如果是门、窗或外墙标语，优先选择
      if (rootObj.userData.type === 'door' || rootObj.userData.type === 'window' || rootObj.userData.type === 'wallSign') {
        targetObject = intersect.object;
        targetRootObject = rootObj;
        break;
      }
    }
    
    // 如果没有找到门/窗/标语，使用最近的对象
    if (!targetObject) {
      targetObject = intersects[0].object;
      targetRootObject = targetObject;
      while (targetRootObject.parent && targetRootObject.parent !== scene) {
        targetRootObject = targetRootObject.parent;
      }
    }
    
    console.log('选中对象:', targetObject.uuid, '类型:', targetObject.userData.type || '未知');
    console.log('根对象:', targetRootObject.uuid, '类型:', targetRootObject.userData.type || '未知');
    
    if (event.ctrlKey || event.metaKey) {
      toggleObjectSelection(targetRootObject);
    } else {
      clearSelection();
      selectObject(targetRootObject);
    }
  } else {
    console.log('没有点击到任何对象');
    if (!event.ctrlKey && !event.metaKey) {
      clearSelection();
    }
  }
}

function selectObject(obj) {
  // 如果是功能区对象，触发zone-selected事件而不是object-selected
  if (obj.userData.type === 'zone' || obj.userData.type === 'zoneLabel') {
    const zoneId = obj.userData.zoneId;
    console.log('点击了功能区，触发zone-selected:', zoneId);
    emit('zone-selected', zoneId);
    return;
  }

  // 关键修复：通过UUID从sceneObjects中查找原始引用，确保引用一致性
  // 避免intersectObjects返回的对象与sceneObjects中的对象引用不一致
  const originalObj = sceneObjects.find(o => o.uuid === obj.uuid);
  if (originalObj) {
    console.log('【引用修复】选中对象通过UUID匹配到原始引用:', obj.uuid, obj.userData.type);
    obj = originalObj;
  } else {
    console.warn('【引用警告】未找到原始引用，使用传入对象:', obj.uuid);
  }

  selectedObject = obj;
  selectedObjects.push(obj);
  
  obj.traverse((child) => {
    if (child.material && child.material.emissive) {
      child.material.emissive.setHex(0x4fc3f7);
      child.material.emissiveIntensity = 0.3;
    }
  });
  
  // 构建选中对象的信息
  // 优先使用已存储的中文名称，如果没有则从modelDatabase查找
  const modelType = obj.userData.modelType || '';
  let displayName = obj.userData.name;
  
  // 如果没有存储名称，尝试从modelDatabase查找
  if (!displayName && modelType) {
    const modelInfo = getModelInfo(modelType);
    displayName = modelInfo ? modelInfo.name : modelType;
  }
  
  // 最终回退
  if (!displayName) {
    displayName = obj.userData.type || '未命名对象';
  }
  
  const objectInfo = {
    uuid: obj.uuid,
    name: displayName,
    type: obj.userData.type || obj.userData.modelType || 'unknown',
    modelType: modelType,
    position: obj.position,
    rotation: obj.rotation.y,
    dimensions: obj.userData.dimensions || calculateObjectDimensions(obj)
  };
  
  // 外墙标语特殊字段
  if (obj.userData.type === 'wallSign') {
    objectInfo.text = obj.userData.text;
    objectInfo.fontSize = obj.userData.fontSize;
    objectInfo.textColor = obj.userData.textColor;
    objectInfo.bgColor = obj.userData.bgColor;
    objectInfo.signHeight = obj.userData.signHeight;
    objectInfo.wallIndex = obj.userData.wallIndex;
    objectInfo.offsetAlongWall = obj.userData.offsetAlongWall;
  }
  
  emit('object-selected', objectInfo);
  updateCornerMarkers();
}

function toggleObjectSelection(obj) {
  const index = selectedObjects.indexOf(obj);
  if (index > -1) {
    selectedObjects.splice(index, 1);
    obj.traverse((child) => {
      if (child.material && child.material.emissive) {
        child.material.emissive.setHex(0x000000);
      }
    });
    selectedObject = selectedObjects.length > 0 ? selectedObjects[selectedObjects.length - 1] : null;
    updateCornerMarkers();
  } else {
    selectObject(obj);
  }
}

function clearSelection() {
  selectedObjects.forEach(obj => {
    obj.traverse((child) => {
      if (child.material && child.material.emissive) {
        child.material.emissive.setHex(0x000000);
      }
    });
  });
  selectedObjects = [];
  selectedObject = null;
  isRotating = false;
  hideRotationRing();
  emit('object-deselected');
  cornerMarkers.forEach(marker => scene.remove(marker));
  cornerMarkers = [];
}

function moveSelectedObjects(delta) {
  console.log('🔵 moveSelectedObjects被调用', delta);
  
  // 如果有对齐线，尝试吸附
  if (alignmentLines.length > 0 && selectedObjects.length > 0) {
    const firstObj = selectedObjects[0];
    const targetPosition = firstObj.position.clone().add(delta);
    
    console.log('尝试吸附，对象当前位置:', firstObj.position.x, firstObj.position.z);
    console.log('目标位置:', targetPosition.x, targetPosition.z);
    console.log('对齐线数量:', alignmentLines.length);
    
    // 【修复】使用 checkAlignmentLineSnap 替代 applySnap，确保使用4条边的中点进行吸附
    const snapResult = checkAlignmentLineSnap(targetPosition, firstObj, SNAP_CONFIG.threshold);
    
    if (snapResult) {
      console.log('🎯 已吸附！吸附到边:', snapResult.edgeName);
      // 应用吸附偏移
      firstObj.position.x += snapResult.offset.x;
      firstObj.position.z += snapResult.offset.z;
      
      // 重新计算delta（基于实际移动后的位置）
      const newPosition = firstObj.position.clone();
      delta.subVectors(newPosition, firstObj.position.clone().sub(delta));
      
      // 显示吸附提示
      if (snapResult.snapPoint) {
        const line = alignmentLines.find(l => l.id === snapResult.lineId);
        if (line) {
          updateSnapIndicator(snapResult.snapPoint, line, 0);
        }
      }
      
      // 【重构】添加对齐线高亮视觉反馈（从原onMouseMove迁移）
      if (snapResult.lineId) {
        highlightAlignmentLineForSnap(snapResult.lineId, true);
      }
    } else {
      console.log('未吸附');
      hideSnapIndicator();
      
      // 【重构】恢复对齐线颜色（从原onMouseMove迁移）
      restoreAllAlignmentLineColors();
    }
  }
  
  // 处理每个选中对象的移动
  selectedObjects.forEach((obj, index) => {
    // 关键修复：使用更健壮的类型判断，支持多种方式识别wallSign
    const objType = obj.userData?.type || obj.userData?.modelType;
    const isWallSign = objType === 'wallSign' || obj.userData?.type === 'wallSign';

    console.log(`【移动对象${index}】类型:`, objType, '是否标语:', isWallSign, 'userData:', obj.userData);

    if (isWallSign) {
      // 外墙标语使用特殊移动逻辑
      console.log('【moveWallSign】调用外墙标语移动逻辑');
      moveWallSign(obj, delta);
    } else {
      // 其他对象正常移动，确保delta的Y分量为0，避免对象陷入地面
      console.log('【普通移动】直接修改position');
      const objDelta = delta.clone();
      objDelta.y = 0;
      obj.position.add(objDelta);
    }
  });
  updateCornerMarkers();
}

function onMouseMove(event) {
  const rect = container.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  
  // 【关键-debug】打印鼠标移动时的状态（每10帧打印一次，避免刷屏）
  if ((isDistanceLineMode || isDistanceLineWaitingForEnd) && Math.random() < 0.1) {
    console.log('【关键-debug】onMouseMove 状态:', {
      isDistanceLineMode,
      isDistanceLineWaitingForEnd,
      hasStartPoint: !!distanceLineStartPoint,
      isDrawingAlignmentLine,
      isMeasuring
    });
  }
  
  // 对齐线绘制预览
  if (isDrawingAlignmentLine && alignmentLineStartPoint) {
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查：防止天文数字坐标
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 预览坐标异常，跳过更新:', intersectPoint);
        return;
      }
      updateAlignmentLinePreview(alignmentLineStartPoint, intersectPoint);
    }
    return;
  }
  
  // 测量模式预览
  if (isMeasuring && measureStartPoint) {
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查：防止天文数字坐标
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 测量预览坐标异常，跳过更新:', intersectPoint);
        return;
      }
      updateMeasureLine(intersectPoint);
    }
    return;
  }
  
  // 距离线模式预览
  if (isDistanceLineMode && isDistanceLineWaitingForEnd && distanceLineStartPoint) {
    console.log('【关键-debug】进入距离线预览逻辑');
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查：防止天文数字坐标
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 距离线预览坐标异常，跳过更新:', intersectPoint);
        return;
      }
      // 计算方向向量（从起点到鼠标位置）
      const direction = new THREE.Vector3().subVectors(intersectPoint, distanceLineStartPoint);
      direction.y = 0; // 确保水平方向
      console.log('【关键-debug】更新距离线预览，方向:', direction.x, direction.z);
      updateDistanceLinePreview(direction);
    }
    return;
  }
  
  // 移动模式（通过【移动】按钮触发）+ 吸附功能
  // 【重构】统一使用 moveSelectedObjects 处理所有移动逻辑
  if (isMoving && selectedObjects.length > 0) {
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    
    if (raycaster.ray.intersectPlane(groundPlane, intersectPoint)) {
      // 防御性检查
      if (Math.abs(intersectPoint.x) > 100000 || Math.abs(intersectPoint.z) > 100000) {
        console.error('❌ 移动模式坐标异常:', intersectPoint);
        return;
      }
      
      // 计算目标位置（对象中心跟随鼠标）
      const targetPosition = new THREE.Vector3(
        Math.round(intersectPoint.x * 10) / 10,
        0,
        Math.round(intersectPoint.z * 10) / 10
      );

      // 【重构】计算 delta 并调用统一的 moveSelectedObjects 函数
      // 不再直接操作 position，确保外墙标语等特殊对象能被正确处理
      const firstObj = selectedObjects[0];
      const delta = new THREE.Vector3(
        targetPosition.x - firstObj.position.x,
        0, // Y方向由 moveSelectedObjects 根据对象类型处理
        targetPosition.z - firstObj.position.z
      );
      
      console.log('【重构-移动】计算 delta:', { 
        targetX: targetPosition.x, 
        targetZ: targetPosition.z,
        currentX: firstObj.position.x,
        currentZ: firstObj.position.z,
        deltaX: delta.x,
        deltaZ: delta.z
      });
      
      // 调用统一的移动函数（内部处理吸附和特殊对象类型）
      moveSelectedObjects(delta);
    }
    return;
  }
  
  // 旋转模式
  if (isRotating && selectedObjects.length > 0 && rotationRing) {
    let totalX = 0, totalZ = 0;
    selectedObjects.forEach(obj => {
      totalX += obj.position.x;
      totalZ += obj.position.z;
    });
    const centerX = totalX / selectedObjects.length;
    const centerZ = totalZ / selectedObjects.length;
    const center = new THREE.Vector3(centerX, 0, centerZ);
    
    raycaster.setFromCamera(mouse, camera);
    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
      const dx = intersectPoint.x - center.x;
      const dz = intersectPoint.z - center.z;
      const currentAngle = Math.atan2(dz, dx);
      
      if (rotationStartAngle === null) {
        rotationStartAngle = currentAngle;
        return;
      }
      
      const deltaAngle = currentAngle - rotationStartAngle;
      
      selectedObjects.forEach(obj => {
        const startData = rotationStartPositions.get(obj);
        if (startData) {
          const relativeX = startData.position.x - centerX;
          const relativeZ = startData.position.z - centerZ;
          
          const cos = Math.cos(deltaAngle);
          const sin = Math.sin(deltaAngle);
          const newX = relativeX * cos - relativeZ * sin;
          const newZ = relativeX * sin + relativeZ * cos;
          
          obj.position.x = centerX + newX;
          obj.position.z = centerZ + newZ;
          
          // 只绕Y轴旋转（垂直旋转），保持原有的X和Z轴旋转
          obj.rotation.y = startData.rotation.y + deltaAngle;
        }
      });
      
      updateCornerMarkers();
      showRotationRing();
    }
    return;
  }
}

function onMouseDown(event) {
  // 检查是否点击了选中的对象
  const rect = container.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  
  // 注意：直接拖拽功能已禁用，只能通过【移动】按钮来移动对象
  // 这样可以避免与OrbitControls的左键旋转冲突
}

function onMouseUp() {
  if (isMoving) {
    isMoving = false;
    container.value.style.cursor = '';
    console.log('移动完成');

    // 移动完成时隐藏吸附提示
    hideSnapIndicator();

    // 移动完成时恢复对齐线颜色
    restoreAllAlignmentLineColors();
  }
  if (isRotating) {
    isRotating = false;
    hideRotationRing();
    container.value.style.cursor = '';
    console.log('旋转完成');
  }
}

function createRotationRing() {
  const ringGeometry = new THREE.RingGeometry(0.8, 1, 32);
  const ringMaterial = new THREE.MeshBasicMaterial({ 
    color: 0x4fc3f7, 
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.6
  });
  const ring = new THREE.Mesh(ringGeometry, ringMaterial);
  ring.rotation.x = -Math.PI / 2;
  return ring;
}

function showRotationRing() {
  hideRotationRing();
  
  if (selectedObjects.length > 0) {
    let totalX = 0, totalZ = 0;
    let maxSize = 0;
    
    selectedObjects.forEach(obj => {
      const box = new THREE.Box3().setFromObject(obj);
      const center = box.getCenter(new THREE.Vector3());
      totalX += center.x;
      totalZ += center.z;
      
      const size = box.getSize(new THREE.Vector3());
      maxSize = Math.max(maxSize, Math.max(size.x, size.z));
    });
    
    const centerX = totalX / selectedObjects.length;
    const centerZ = totalZ / selectedObjects.length;
    
    rotationRing = createRotationRing();
    rotationRing.position.set(centerX, 0.1, centerZ);
    rotationRing.scale.set(maxSize, maxSize, 1);
    
    scene.add(rotationRing);
  }
}

function hideRotationRing() {
  if (rotationRing) {
    scene.remove(rotationRing);
    rotationRing = null;
  }
}

function createCornerMarkers() {
  const markerGeometry = new THREE.SphereGeometry(0.08, 16, 16);
  const markerMaterial = new THREE.MeshBasicMaterial({ color: 0x4fc3f7 });
  
  for (let i = 0; i < 4; i++) {
    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
    scene.add(marker);
    cornerMarkers.push(marker);
  }
}

function updateCornerMarkers() {
  cornerMarkers.forEach(marker => scene.remove(marker));
  cornerMarkers = [];
  
  if (selectedObject) {
    const box = new THREE.Box3().setFromObject(selectedObject);
    const min = box.min;
    const max = box.max;
    
    const corners = [
      new THREE.Vector3(min.x, 0, min.z),
      new THREE.Vector3(max.x, 0, min.z),
      new THREE.Vector3(min.x, 0, max.z),
      new THREE.Vector3(max.x, 0, max.z)
    ];
    
    const markerGeometry = new THREE.SphereGeometry(0.08, 16, 16);
    const markerMaterial = new THREE.MeshBasicMaterial({ color: 0x4fc3f7 });
    
    corners.forEach(corner => {
      const marker = new THREE.Mesh(markerGeometry, markerMaterial);
      marker.position.copy(corner);
      scene.add(marker);
      cornerMarkers.push(marker);
    });
  }
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

// 强制渲染刷新（用于解决v-show切换后的渲染问题）
function forceRender() {
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
    console.log('强制渲染刷新');
  }
}

function clearBatchPreview() {
  batchPreviewObjects.forEach(preview => scene.remove(preview));
  batchPreviewObjects = [];
  console.log('清除预览对象');
}

function onDragOver(event) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'copy';
}

function onDrop(event) {
  event.preventDefault();
  
  // 计算鼠标在画布中的位置
  const rect = container.value.getBoundingClientRect();
  const mouseX = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  const mouseY = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  // 检查是否是门或窗
  const objectType = event.dataTransfer.getData('objectType');
  if (objectType === 'door' || objectType === 'liftDoor' || objectType === 'liftDoor27' || objectType === 'window') {
    // 检测墙体（支持仓库墙体和办公区墙体）
    raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
    const wallIntersects = raycaster.intersectObjects(
      sceneObjects.filter(obj => obj.userData.type === 'wall' || obj.userData.type === 'officeWall'),
      false
    );
    
    if (wallIntersects.length > 0) {
      const wall = wallIntersects[0].object;
      const wallIndex = wall.userData.wallIndex;
      const intersectPoint = wallIntersects[0].point;
      
      // 计算点击位置在墙体上的相对位置
      const wallCenter = wall.position.clone();
      const wallDirection = new THREE.Vector3(
        Math.cos(-wall.rotation.y),
        0,
        Math.sin(-wall.rotation.y)
      );
      
      const toIntersect = new THREE.Vector3().subVectors(intersectPoint, wallCenter);
      const position = toIntersect.dot(wallDirection) / 100; // 转换为米
      
      if (objectType === 'door' || objectType === 'liftDoor' || objectType === 'liftDoor27') {
        const width = parseFloat(event.dataTransfer.getData('doorWidth')) || 2;
        const height = parseFloat(event.dataTransfer.getData('doorHeight')) || 2.2;
        createDoor(wallIndex, position, { width, height }, wall.userData.type);
      } else if (objectType === 'window') {
        const width = parseFloat(event.dataTransfer.getData('windowWidth')) || 1.5;
        const height = parseFloat(event.dataTransfer.getData('windowHeight')) || 1.2;
        const sillHeight = parseFloat(event.dataTransfer.getData('windowSillHeight')) || 1.0;
        createWindow(wallIndex, position, { width, height, sillHeight }, wall.userData.type);
      }
    }
    return;
  }

  // 处理外墙标语
  if (objectType === 'wallSign') {
    // 发射射线检测墙体（使用递归模式检测子对象）
    raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
    const wallObjects = sceneObjects.filter(obj => obj.userData.type === 'wall');
    console.log('检测到的墙体数量:', wallObjects.length);
    const intersects = raycaster.intersectObjects(wallObjects, true);

    if (intersects.length > 0) {
      // 找到最近的墙体（可能是子对象，需要向上查找到墙体根对象）
      let wall = intersects[0].object;
      while (wall && wall.userData.type !== 'wall' && wall.parent) {
        wall = wall.parent;
      }
      
      if (wall && wall.userData.type === 'wall') {
        const intersectPoint = intersects[0].point;
        // 创建外墙标语
        createWallSign(wall, intersectPoint);
        console.log('外墙标语放置到墙体:', wall.userData.wallIndex);
      } else {
        console.warn('未找到有效的墙体对象');
      }
    } else {
      console.warn('未点击到墙体，无法放置外墙标语');
    }
    return;
  }

  // 处理立柱
  if (objectType === 'pillar') {
    // 发射射线检测地面
    raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersectPoint = new THREE.Vector3();

    if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
      // 对齐到网格
      intersectPoint.x = Math.round(intersectPoint.x * 10) / 10;
      intersectPoint.z = Math.round(intersectPoint.z * 10) / 10;

      // 创建立柱
      createPillar({ x: intersectPoint.x, z: intersectPoint.z });
      console.log('立柱放置到位置:', intersectPoint);
    }
    return;
  }

  // 处理普通模型
  const modelName = event.dataTransfer.getData('modelName');
  if (!modelName) return;
  
  // 发射射线检测地面
  raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  const intersectPoint = new THREE.Vector3();
  
  if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
    // 对齐到网格
    intersectPoint.x = Math.round(intersectPoint.x * 10) / 10;
    intersectPoint.z = Math.round(intersectPoint.z * 10) / 10;
    
    // 考虑仓库基准高度
    let yPosition = 0;
    if (warehouseConfig) {
      yPosition = warehouseConfig.baseHeight;
    }
    
    // 使用新的统一模型数据库添加模型
    const newModel = addModelInternal(modelName, {
      x: intersectPoint.x,
      y: yPosition,
      z: intersectPoint.z
    });
    
    if (!newModel) {
      console.error('添加模型失败:', modelName);
      return;
    }
    
    if (newModel) {
      console.log('模型放置到位置:', intersectPoint, '名称:', modelName);
    }
  }
}

// 内部使用的添加模型方法
function addModelInternal(modelName, position = null) {
  // 使用新的统一模型数据库获取模型信息
  const modelInfo = getModelInfo(modelName);
  
  if (!modelInfo) {
    console.error('未找到模型信息:', modelName);
    return null;
  }
  
  const shortId = modelInfo.shortId;
  const longId = modelInfo.longId;
  
  console.log('尝试添加模型:', modelName, '短ID:', shortId, '长ID:', longId, 'models中是否存在:', !!models[longId]);
  
  if (models[longId]) {
    const newModel = models[longId].clone();
    
    // 确保克隆后的模型保持原始缩放
    console.log('克隆模型，原始缩放:', models[longId].scale.x, models[longId].scale.y, models[longId].scale.z);
    console.log('克隆后缩放:', newModel.scale.x, newModel.scale.y, newModel.scale.z);
    
    // 【关键修复】强制计算几何体边界框，解决"幽灵模型"问题
    // 注意：必须总是重新计算，因为克隆后的模型缩放可能改变
    newModel.traverse((child) => {
      if (child.isMesh && child.geometry) {
        child.geometry.computeBoundingBox();
        child.geometry.computeBoundingSphere();
      }
    });
    
    newModel.traverse((child) => {
      if (child.material) {
        child.material = child.material.clone();
      }
    });
    
    // 记录对象类型和中文名称（统一使用短ID）
    newModel.userData.modelType = shortId; // 存储短ID
    newModel.userData.modelId = 'shelf_001';
    newModel.userData.type = modelInfo.params.type || 'shelf'; // 添加类型标识，用于射线检测
    newModel.userData.name = modelInfo.name; // 中文名称（从modelDatabase获取）
    newModel.userData.params = modelInfo.params; // 存储参数
    
    // 设置位置，考虑仓库基准高度
    // 注意：模型在loadModel中已经设置了offsetY使底部与Y=0平齐
    // 这里只需要加上仓库基准高度
    let yOffset = 0;
    if (warehouseConfig) {
      yOffset = warehouseConfig.baseHeight;
    }
    
    if (position) {
      newModel.position.x = position.x;
      newModel.position.z = position.z;
      // Y位置：使用传入的position.y（如果有），否则保持原始offsetY
      // 再加上仓库基准高度和2.0确保在区域平面(baseHeight+1)上方
      const baseY = position.y !== undefined ? position.y : 0;
      newModel.position.y = baseY + yOffset + 2.0;
    }
    
    scene.add(newModel);
    sceneObjects.push(newModel);
    
    // 调试信息：输出模型的实际位置和尺寸
    const box = new THREE.Box3().setFromObject(newModel);
    const size = box.getSize(new THREE.Vector3());
    
    // 检查模型的材质和可见性
    let materialInfo = '';
    newModel.traverse((child) => {
      if (child.isMesh) {
        materialInfo += `${child.name}: visible=${child.visible}, opacity=${child.material?.opacity || 'N/A'}, color=${child.material?.color?.getHexString?.() || 'N/A'}; `;
      }
    });
    
    console.log('模型添加到场景:', newModel.uuid, '类型:', modelName, 
                '位置:', newModel.position.x, newModel.position.y, newModel.position.z, 
                '尺寸:', size.x, size.y, size.z,
                'sceneObjects数量:', sceneObjects.length,
                '材质:', materialInfo);
    emit('model-added', newModel);
    
    return newModel;
  }
  return null;
}

// 对象库参数定义（从ModelLibrary.vue中提取）
const objectLibraryParams = {
  // 货架系统
  'shelf-beam-heavy': { length: 2700, width: 1000, height: 4500, levels: 4, type: 'shelf', color: 0xCC0000 },
  'shelf-beam-medium': { length: 2000, width: 800, height: 3500, levels: 4, type: 'shelf', color: 0x4169E1 },
  'shelf-drive-in': { length: 3600, width: 1500, height: 6000, depth: 5, type: 'shelf', color: 0x8B4513 },
  'shelf-flow-4level': { length: 900, width: 450, height: 1800, levels: 4, type: 'shelf', color: 0x98FB98 },
  'shelf-light-v2': { length: 1200, width: 400, height: 2000, levels: 4, type: 'shelf', color: 0x4169E1 },
  'shelf-beam-heavy-3level': { length: 2300, width: 1000, height: 4500, levels: 3, type: 'shelf', color: 0xCC0000 },
  'shelf-beam-heavy-4level': { length: 2300, width: 1000, height: 5000, levels: 4, type: 'shelf', color: 0xCC0000 },
  'shelf-beam-heavy-5level': { length: 2300, width: 1000, height: 6000, levels: 5, type: 'shelf', color: 0xCC0000 },
  'shelf-beam-medium-4level-2m': { length: 2000, width: 600, height: 3500, levels: 4, type: 'shelf', color: 0x4169E1 },
  'shelf-beam-medium-5level-2m': { length: 2000, width: 600, height: 4000, levels: 5, type: 'shelf', color: 0x4169E1 },
  'shelf-beam-light-4level-2m': { length: 2000, width: 500, height: 2500, levels: 4, type: 'shelf', color: 0x87CEEB },
  'shelf-beam-light-5level-2m': { length: 2000, width: 500, height: 3000, levels: 5, type: 'shelf', color: 0x87CEEB },
  // 轻型货架（A15系列）
  // 轻型货架（A15系列）- 只保留A15-4和配组
  'light-duty-A15-4': { length: 1520, width: 402, height: 2020, levels: 4, type: 'shelf', color: 0x4169E1 },
  'light-duty-A15-4-pair': { length: 1520, width: 802, height: 2020, levels: 4, type: 'shelf', color: 0x4169E1 },
  // 载具容器
  'pallet-wooden-1200': { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0xD2691E },
  'pallet-plastic-1200': { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0x4169E1 },
  'pallet-wood-1200x1000': { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0x8B4513 },
  'pallet-plastic-1200x1000': { length: 1200, width: 1000, height: 150, type: 'pallet', color: 0x4169E1 },
  'container-foldable': { length: 600, width: 400, height: 300, type: 'container', color: 0x32CD32 },
  'container-tote-600x400x300': { length: 600, width: 400, height: 300, type: 'container', color: 0x4169E1 },
  'container-tote-600x400x220': { length: 600, width: 400, height: 220, type: 'container', color: 0x4169E1 },
  'container-tote-400x300x150': { length: 400, width: 300, height: 150, type: 'container', color: 0x4169E1 },
  // 搬运设备
  'forklift-reach-2t': { length: 1200, width: 800, height: 2500, type: 'forklift', color: 0xFFD700 },
  'forklift-counterbalance-2.5t': { length: 2500, width: 1200, height: 2200, type: 'forklift', color: 0xFFD700 },
  'forklift-pallet-truck-electric': { length: 1500, width: 700, height: 1200, type: 'forklift', color: 0xFFD700 },
  'forklift-pallet-jack-manual': { length: 1200, width: 550, height: 1200, type: 'forklift', color: 0xFFD700 },
  'cart-picking-3tier': { length: 800, width: 600, height: 1000, type: 'cart', color: 0x32CD32 },
  'cart-cage-logistics-2tier': { length: 800, width: 600, height: 1500, type: 'cart', color: 0x32CD32 },
  // 中型货架（B20系列）- 立柱深蓝色
  'medium-duty-B20-4': { length: 2020, width: 602, height: 2020, levels: 4, type: 'shelf', color: 0x00008B },
  'medium-duty-B20-4-pair': { length: 2020, width: 1202, height: 2020, levels: 4, type: 'shelf', color: 0x00008B },
  // 高位货架（C23系列）- 立柱橙红色
  'high-duty-C23-3': { length: 2320, width: 1002, height: 3020, levels: 3, type: 'shelf', color: 0xFF4500 },
  'high-duty-C23-3-pair': { length: 2320, width: 2202, height: 3020, levels: 3, type: 'shelf', color: 0xFF4500 },
  // 输送设备
  'lift-cargo-hydraulic-3floor': { length: 2000, width: 1500, height: 8000, type: 'conveyor', color: 0xFF6347 },
  'conveyor-curve-90degree-600': { length: 1500, width: 1500, height: 800, type: 'conveyor', color: 0xFF6347 },
  'conveyor-roller-straight-600-red': { length: 2000, width: 600, height: 800, type: 'conveyor', color: 0xFF6347 },
  // 拣选设备
  'putwall-standard-16cell': { length: 1600, width: 500, height: 1800, type: 'picking', color: 0x9370DB },
  'station-packcheck-integrated-red': { length: 1800, width: 900, height: 2000, type: 'picking', color: 0xFF6347 },
  'weigher-automatic-check-600-red': { length: 1600, width: 700, height: 800, type: 'picking', color: 0xFF6347 },
  // 其他设备
  'guard-rack-heavy-redyellow': { length: 1500, width: 150, height: 400, type: 'guard', color: 0xFF4500 },
  'guard-column-protector-redyellow': { length: 120, width: 120, height: 400, type: 'guard', color: 0xFF4500 },
  // 人员
  'person-warehouse-admin-red': { length: 450, width: 300, height: 1750, type: 'person', color: 0xFF69B4 },
};

// 创建详细的3D模型（根据对象类型和参数）
function createDetailedModel(modelName, position) {
  const group = new THREE.Group();
  
  // 使用新的统一模型数据库获取模型信息
  const modelInfo = getModelInfo(modelName);
  
  if (!modelInfo) {
    console.error('createDetailedModel: 未找到模型信息:', modelName);
    return null;
  }
  
  const params = modelInfo.params;
  const { length, width, height, levels, type, color } = params;
  const lengthM = length / 100; // mm to cm (Three.js单位)
  const widthM = width / 100;
  const heightM = height / 100;
  
  // 根据类型创建不同的3D模型
  switch (type) {
    case 'shelf':
      createShelfModel(group, lengthM, widthM, heightM, levels, color);
      break;
    case 'pallet':
      createPalletModel(group, lengthM, widthM, heightM, color);
      break;
    case 'container':
      createContainerModel(group, lengthM, widthM, heightM, color);
      break;
    case 'forklift':
      createForkliftModel(group, lengthM, widthM, heightM, color);
      break;
    case 'cart':
      createCartModel(group, lengthM, widthM, heightM, color);
      break;
    case 'conveyor':
      createConveyorModel(group, lengthM, widthM, heightM, color);
      break;
    case 'picking':
      createPickingModel(group, lengthM, widthM, heightM, color);
      break;
    case 'guard':
      createGuardModel(group, lengthM, widthM, heightM, color);
      break;
    case 'person':
      createPersonModel(group, lengthM, widthM, heightM, color);
      break;
    default:
      // 默认方块
      const geometry = new THREE.BoxGeometry(lengthM, heightM, widthM);
      const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.7, metalness: 0.3 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.y = heightM / 2;
      group.add(mesh);
  }
  
  // 设置位置
  group.position.set(position.x, position.y, position.z);
  
  // 存储对象信息（使用短ID）
  group.userData = {
    type: 'model',
    modelType: modelInfo.shortId,
    modelId: modelInfo.shortId,
    name: modelInfo.name,
    params: params,
    isDetailedModel: true
  };
  
  scene.add(group);
  sceneObjects.push(group);
  
  console.log('创建详细模型:', modelName, '类型:', type, 'sceneObjects数量:', sceneObjects.length);
  emit('model-added', group);
  
  return group;
}

// 创建货架模型
function createShelfModel(group, length, width, height, levels, color) {
  const levelCount = levels || 4;
  const uprightWidth = 5; // 立柱宽度 5cm
  const beamHeight = 8; // 横梁高度 8cm
  const levelHeight = height / levelCount;
  
  // 材质
  const uprightMaterial = new THREE.MeshStandardMaterial({ color: 0x4169E1, roughness: 0.5, metalness: 0.6 }); // 蓝色立柱
  const beamMaterial = new THREE.MeshStandardMaterial({ color: 0xFF8C00, roughness: 0.5, metalness: 0.6 }); // 橙色横梁
  const deckMaterial = new THREE.MeshStandardMaterial({ color: 0xF5F5DC, roughness: 0.8, metalness: 0.1 }); // 米色层板
  
  // 创建4个立柱
  const uprightPositions = [
    { x: -length/2 + uprightWidth/2, z: -width/2 + uprightWidth/2 },
    { x: length/2 - uprightWidth/2, z: -width/2 + uprightWidth/2 },
    { x: -length/2 + uprightWidth/2, z: width/2 - uprightWidth/2 },
    { x: length/2 - uprightWidth/2, z: width/2 - uprightWidth/2 }
  ];
  
  uprightPositions.forEach(pos => {
    const uprightGeo = new THREE.BoxGeometry(uprightWidth, height, uprightWidth);
    const upright = new THREE.Mesh(uprightGeo, uprightMaterial);
    upright.position.set(pos.x, height/2, pos.z);
    group.add(upright);
  });
  
  // 创建横梁和层板
  for (let i = 0; i <= levelCount; i++) {
    const y = i * levelHeight;
    
    // 前后横梁
    const frontBeamGeo = new THREE.BoxGeometry(length, beamHeight, 3);
    const frontBeam = new THREE.Mesh(frontBeamGeo, beamMaterial);
    frontBeam.position.set(0, y, -width/2 + 5);
    group.add(frontBeam);
    
    const backBeamGeo = new THREE.BoxGeometry(length, beamHeight, 3);
    const backBeam = new THREE.Mesh(backBeamGeo, beamMaterial);
    backBeam.position.set(0, y, width/2 - 5);
    group.add(backBeam);
    
    // 左右横梁
    const leftBeamGeo = new THREE.BoxGeometry(3, beamHeight, width - 10);
    const leftBeam = new THREE.Mesh(leftBeamGeo, beamMaterial);
    leftBeam.position.set(-length/2 + 5, y, 0);
    group.add(leftBeam);
    
    const rightBeamGeo = new THREE.BoxGeometry(3, beamHeight, width - 10);
    const rightBeam = new THREE.Mesh(rightBeamGeo, beamMaterial);
    rightBeam.position.set(length/2 - 5, y, 0);
    group.add(rightBeam);
    
    // 层板（除了最顶层）
    if (i < levelCount) {
      const deckGeo = new THREE.BoxGeometry(length - 10, 2, width - 10);
      const deck = new THREE.Mesh(deckGeo, deckMaterial);
      deck.position.set(0, y + levelHeight/2, 0);
      group.add(deck);
    }
  }
}

// 创建托盘模型
function createPalletModel(group, length, width, height, color) {
  const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.8, metalness: 0.1 });
  
  // 底部板
  const bottomGeo = new THREE.BoxGeometry(length, height/3, width);
  const bottom = new THREE.Mesh(bottomGeo, material);
  bottom.position.y = height/6;
  group.add(bottom);
  
  // 中间支撑块
  const blockSize = 10;
  const blockGeo = new THREE.BoxGeometry(blockSize, height/3, blockSize);
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const block = new THREE.Mesh(blockGeo, material);
      block.position.set(
        -length/2 + length/4 * (i + 1),
        height/2,
        -width/2 + width/4 * (j + 1)
      );
      group.add(block);
    }
  }
  
  // 顶部板
  const topGeo = new THREE.BoxGeometry(length, height/3, width);
  const top = new THREE.Mesh(topGeo, material);
  top.position.y = height * 5/6;
  group.add(top);
}

// 创建容器模型
function createContainerModel(group, length, width, height, color) {
  const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.6, metalness: 0.2 });
  const wallThickness = 2;
  
  // 底板
  const bottomGeo = new THREE.BoxGeometry(length, wallThickness, width);
  const bottom = new THREE.Mesh(bottomGeo, material);
  bottom.position.y = wallThickness/2;
  group.add(bottom);
  
  // 四壁
  const frontGeo = new THREE.BoxGeometry(length, height, wallThickness);
  const front = new THREE.Mesh(frontGeo, material);
  front.position.set(0, height/2, -width/2 + wallThickness/2);
  group.add(front);
  
  const backGeo = new THREE.BoxGeometry(length, height, wallThickness);
  const back = new THREE.Mesh(backGeo, material);
  back.position.set(0, height/2, width/2 - wallThickness/2);
  group.add(back);
  
  const leftGeo = new THREE.BoxGeometry(wallThickness, height, width - wallThickness*2);
  const left = new THREE.Mesh(leftGeo, material);
  left.position.set(-length/2 + wallThickness/2, height/2, 0);
  group.add(left);
  
  const rightGeo = new THREE.BoxGeometry(wallThickness, height, width - wallThickness*2);
  const right = new THREE.Mesh(rightGeo, material);
  right.position.set(length/2 - wallThickness/2, height/2, 0);
  group.add(right);
}

// 创建叉车模型
function createForkliftModel(group, length, width, height, color) {
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: color, roughness: 0.4, metalness: 0.5 });
  const blackMaterial = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.8, metalness: 0.2 });
  const silverMaterial = new THREE.MeshStandardMaterial({ color: 0xC0C0C0, roughness: 0.3, metalness: 0.8 });
  
  // 车身
  const bodyGeo = new THREE.BoxGeometry(length * 0.6, height * 0.5, width);
  const body = new THREE.Mesh(bodyGeo, bodyMaterial);
  body.position.set(-length * 0.2, height * 0.25, 0);
  group.add(body);
  
  // 驾驶室
  const cabGeo = new THREE.BoxGeometry(length * 0.3, height * 0.8, width * 0.8);
  const cab = new THREE.Mesh(cabGeo, bodyMaterial);
  cab.position.set(-length * 0.35, height * 0.4, 0);
  group.add(cab);
  
  // 门架
  const mastGeo = new THREE.BoxGeometry(5, height * 0.9, width * 0.1);
  const mastLeft = new THREE.Mesh(mastGeo, blackMaterial);
  mastLeft.position.set(length * 0.3, height * 0.45, -width * 0.2);
  group.add(mastLeft);
  
  const mastRight = new THREE.Mesh(mastGeo, blackMaterial);
  mastRight.position.set(length * 0.3, height * 0.45, width * 0.2);
  group.add(mastRight);
  
  // 货叉
  const forkGeo = new THREE.BoxGeometry(length * 0.4, 3, 8);
  const forkLeft = new THREE.Mesh(forkGeo, silverMaterial);
  forkLeft.position.set(length * 0.5, height * 0.1, -width * 0.15);
  group.add(forkLeft);
  
  const forkRight = new THREE.Mesh(forkGeo, silverMaterial);
  forkRight.position.set(length * 0.5, height * 0.1, width * 0.15);
  group.add(forkRight);
  
  // 轮子
  const wheelGeo = new THREE.CylinderGeometry(8, 8, 5, 16);
  wheelGeo.rotateZ(Math.PI / 2);
  const wheelPositions = [
    { x: -length * 0.3, z: -width * 0.4 },
    { x: -length * 0.3, z: width * 0.4 },
    { x: length * 0.1, z: -width * 0.4 },
    { x: length * 0.1, z: width * 0.4 }
  ];
  wheelPositions.forEach(pos => {
    const wheel = new THREE.Mesh(wheelGeo, blackMaterial);
    wheel.position.set(pos.x, 8, pos.z);
    group.add(wheel);
  });
}

// 创建推车模型
function createCartModel(group, length, width, height, color) {
  // 修改：为不同部件定义不同材质
  const postMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xFF0000,  // 红色立柱
    roughness: 0.5, 
    metalness: 0.4 
  });
  const deckMaterial = new THREE.MeshStandardMaterial({ 
    color: 0xFFA500,  // 橙黄色层板
    roughness: 0.5, 
    metalness: 0.4 
  });
  const wheelMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x000000,  // 黑色轮子
    roughness: 0.8, 
    metalness: 0.2 
  });
  
  // 层板 - 使用橙黄色材质
  const levels = 3;
  for (let i = 0; i < levels; i++) {
    const y = (i + 1) * height / (levels + 1);
    const deckGeo = new THREE.BoxGeometry(length, 2, width);
    const deck = new THREE.Mesh(deckGeo, deckMaterial);
    deck.position.y = y;
    group.add(deck);
  }
  
  // 立柱 - 使用红色材质
  const postGeo = new THREE.BoxGeometry(3, height, 3);
  const postPositions = [
    { x: -length/2 + 5, z: -width/2 + 5 },
    { x: length/2 - 5, z: -width/2 + 5 },
    { x: -length/2 + 5, z: width/2 - 5 },
    { x: length/2 - 5, z: width/2 - 5 }
  ];
  postPositions.forEach(pos => {
    const post = new THREE.Mesh(postGeo, postMaterial);
    post.position.set(pos.x, height/2, pos.z);
    group.add(post);
  });
  
  // 轮子 - 使用黑色材质
  const wheelGeo = new THREE.CylinderGeometry(5, 5, 3, 16);
  wheelGeo.rotateZ(Math.PI / 2);
  postPositions.forEach(pos => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMaterial);
    wheel.position.set(pos.x, 5, pos.z);
    group.add(wheel);
  });
}

// 创建输送设备模型
function createConveyorModel(group, length, width, height, color) {
  const frameMaterial = new THREE.MeshStandardMaterial({ color: color, roughness: 0.5, metalness: 0.4 });
  const rollerMaterial = new THREE.MeshStandardMaterial({ color: 0xC0C0C0, roughness: 0.3, metalness: 0.8 });
  
  // 机架
  const frameHeight = 10;
  const frameGeo = new THREE.BoxGeometry(length, frameHeight, width);
  const frame = new THREE.Mesh(frameGeo, frameMaterial);
  frame.position.y = frameHeight/2;
  group.add(frame);
  
  // 滚筒
  const rollerCount = Math.floor(length / 15);
  const rollerGeo = new THREE.CylinderGeometry(3, 3, width - 4, 16);
  rollerGeo.rotateX(Math.PI / 2);
  
  for (let i = 0; i < rollerCount; i++) {
    const roller = new THREE.Mesh(rollerGeo, rollerMaterial);
    roller.position.set(
      -length/2 + (i + 0.5) * length/rollerCount,
      frameHeight + 3,
      0
    );
    group.add(roller);
  }
  
  // 支撑腿
  const legGeo = new THREE.BoxGeometry(5, height - frameHeight, 5);
  const legPositions = [
    { x: -length/2 + 10, z: -width/2 + 5 },
    { x: -length/2 + 10, z: width/2 - 5 },
    { x: length/2 - 10, z: -width/2 + 5 },
    { x: length/2 - 10, z: width/2 - 5 }
  ];
  legPositions.forEach(pos => {
    const leg = new THREE.Mesh(legGeo, frameMaterial);
    leg.position.set(pos.x, frameHeight + (height - frameHeight)/2, pos.z);
    group.add(leg);
  });
}

// 创建拣选设备模型
function createPickingModel(group, length, width, height, color) {
  const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.5, metalness: 0.3 });
  
  // 主体
  const bodyGeo = new THREE.BoxGeometry(length, height, width);
  const body = new THREE.Mesh(bodyGeo, material);
  body.position.y = height/2;
  group.add(body);
  
  // 顶部工作面
  const topGeo = new THREE.BoxGeometry(length + 10, 5, width + 10);
  const top = new THREE.Mesh(topGeo, new THREE.MeshStandardMaterial({ color: 0xFFFFFF }));
  top.position.y = height + 2.5;
  group.add(top);
}

// 创建防护设施模型
function createGuardModel(group, length, width, height, color) {
  const material = new THREE.MeshStandardMaterial({ color: color, roughness: 0.6, metalness: 0.2 });
  const stripeMaterial = new THREE.MeshStandardMaterial({ color: 0xFFFF00, roughness: 0.6, metalness: 0.2 }); // 黄色条纹
  
  // 主体
  const bodyGeo = new THREE.BoxGeometry(length, height, width);
  const body = new THREE.Mesh(bodyGeo, material);
  body.position.y = height/2;
  group.add(body);
  
  // 黄色警示条纹
  const stripeCount = 3;
  for (let i = 0; i < stripeCount; i++) {
    const stripeGeo = new THREE.BoxGeometry(length + 1, height/stripeCount/2, width + 1);
    const stripe = new THREE.Mesh(stripeGeo, stripeMaterial);
    stripe.position.y = (i + 0.5) * height/stripeCount;
    group.add(stripe);
  }
}

// 创建人员模型
function createPersonModel(group, length, width, height, color) {
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: color, roughness: 0.7, metalness: 0.1 });
  const vestMaterial = new THREE.MeshStandardMaterial({ color: 0xFFD700, roughness: 0.8, metalness: 0.1 }); // 黄色反光背心
  const helmetMaterial = new THREE.MeshStandardMaterial({ color: 0xFF0000, roughness: 0.4, metalness: 0.3 }); // 红色安全帽
  
  // 身体
  const bodyGeo = new THREE.CylinderGeometry(length/3, length/2.5, height * 0.6, 16);
  const body = new THREE.Mesh(bodyGeo, vestMaterial);
  body.position.y = height * 0.3;
  group.add(body);
  
  // 头
  const headGeo = new THREE.SphereGeometry(length/3, 16, 16);
  const head = new THREE.Mesh(headGeo, bodyMaterial);
  head.position.y = height * 0.75;
  group.add(head);
  
  // 安全帽
  const helmetGeo = new THREE.SphereGeometry(length/2.8, 16, 16, 0, Math.PI * 2, 0, Math.PI/2);
  const helmet = new THREE.Mesh(helmetGeo, helmetMaterial);
  helmet.position.y = height * 0.8;
  group.add(helmet);
  
  // 腿
  const legGeo = new THREE.CylinderGeometry(length/6, length/6, height * 0.35, 16);
  const legLeft = new THREE.Mesh(legGeo, bodyMaterial);
  legLeft.position.set(-length/4, height * 0.175, 0);
  group.add(legLeft);
  
  const legRight = new THREE.Mesh(legGeo, bodyMaterial);
  legRight.position.set(length/4, height * 0.175, 0);
  group.add(legRight);
}

// 创建占位对象（优先使用GLB模型，如果没有则使用详细几何体）
function createPlaceholderObject(modelName, position) {
  // 获取模型信息
  const modelInfo = getModelInfo(modelName);
  
  if (!modelInfo) {
    console.error('createPlaceholderObject: 未找到模型信息:', modelName);
    return null;
  }
  
  const longId = modelInfo.longId;
  
  // 首先尝试使用预加载的GLB模型
  if (models[longId]) {
    const newModel = models[longId].clone();
    
    newModel.traverse((child) => {
      if (child.material) {
        child.material = child.material.clone();
      }
    });
    
    // 记录对象信息（使用短ID）
    newModel.userData.modelType = modelInfo.shortId;
    newModel.userData.modelId = modelInfo.shortId;
    newModel.userData.name = modelInfo.name;
    newModel.userData.params = modelInfo.params;
    newModel.userData.isGLBModel = true;
    
    // 设置位置
    let yPosition = 0;
    if (warehouseConfig) {
      yPosition = warehouseConfig.baseHeight;
    }
    
    newModel.position.set(position.x, yPosition, position.z);
    
    scene.add(newModel);
    sceneObjects.push(newModel);
    
    console.log('GLB模型添加到场景:', modelInfo.shortId, 'sceneObjects数量:', sceneObjects.length);
    emit('model-added', newModel);
    
    return newModel;
  }
  
  // 如果没有GLB模型，使用详细几何体生成
  console.log('GLB模型未加载，使用详细几何体:', modelInfo.shortId);
  return createDetailedModel(modelName, position);
}

// 初始化区域材质
function initZoneMaterials() {
  for (const [type, color] of Object.entries(zoneTypeColors)) {
    zoneMaterials[type] = new THREE.MeshStandardMaterial({
      color: color,
      transparent: true,
      opacity: 0.15, // 透明度15%，与地面网格叠加后更通透
      side: THREE.DoubleSide,
      roughness: 0.8,
      metalness: 0.1
    });
  }
  console.log('区域材质初始化完成');
}

// 开始绘制区域
function startDrawZone(toolType, zoneType) {
  currentDrawTool = toolType;
  currentZoneType = zoneType;
  isDrawingZone = true;
  currentZonePoints = [];
  
  if (currentZoneMesh) {
    scene.remove(currentZoneMesh);
    currentZoneMesh = null;
  }
  
  console.log('开始绘制区域:', toolType, '类型:', zoneType);
}

// 取消绘制区域
function cancelDrawZone() {
  isDrawingZone = false;
  currentDrawTool = null;
  currentZonePoints = [];
  
  if (currentZoneMesh) {
    scene.remove(currentZoneMesh);
    currentZoneMesh = null;
  }
  
  console.log('取消绘制区域');
}

// 处理鼠标点击事件（用于区域绘制）
function handleZoneClick(event) {
  if (!isDrawingZone) return;
  
  const rect = container.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  const intersectPoint = new THREE.Vector3();
  
  if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
    // 对齐到网格
    intersectPoint.x = Math.round(intersectPoint.x * 10) / 10;
    intersectPoint.z = Math.round(intersectPoint.z * 10) / 10;
    
    currentZonePoints.push(intersectPoint.clone());
    
    // 实时更新绘制预览
    updateZonePreview();
    
    // 如果是矩形工具且已经有2个点，完成绘制
    if (currentDrawTool === 'rectangle' && currentZonePoints.length === 2) {
      finishDrawZone();
    }
  }
}

// 更新区域绘制预览
function updateZonePreview() {
  if (currentZoneMesh) {
    scene.remove(currentZoneMesh);
    currentZoneMesh = null;
  }
  
  if (currentZonePoints.length < 2) return;
  
  let geometry;
  if (currentDrawTool === 'rectangle' && currentZonePoints.length === 2) {
    // 矩形
    const p1 = currentZonePoints[0];
    const p2 = currentZonePoints[1];
    const width = Math.abs(p2.x - p1.x);
    const height = Math.abs(p2.z - p1.z);
    const centerX = (p1.x + p2.x) / 2;
    const centerZ = (p1.z + p2.z) / 2;
    
    geometry = new THREE.PlaneGeometry(width, height);
    currentZoneMesh = new THREE.Mesh(geometry, zoneMaterials[currentZoneType]);
    currentZoneMesh.position.set(centerX, 0.01, centerZ);
    currentZoneMesh.rotation.x = -Math.PI / 2;
  } else if (currentDrawTool === 'polygon' && currentZonePoints.length >= 3) {
    // 多边形
    geometry = new THREE.BufferGeometry();
    const vertices = [];
    
    currentZonePoints.forEach(point => {
      vertices.push(point.x, 0, point.z);
    });
    
    // 计算面
    const indices = [];
    for (let i = 1; i < currentZonePoints.length - 1; i++) {
      indices.push(0, i, i + 1);
    }
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    
    currentZoneMesh = new THREE.Mesh(geometry, zoneMaterials[currentZoneType]);
  }
  
  if (currentZoneMesh) {
    scene.add(currentZoneMesh);
  }
}

// 完成区域绘制
function finishDrawZone() {
  if (currentZonePoints.length < 2) {
    cancelDrawZone();
    return;
  }
  
  // 创建区域对象
  const zoneId = `zone_${Date.now()}`;
  const zoneName = getZoneTypeName(currentZoneType);
  
  let geometry, position, rotation;
  
  if (currentDrawTool === 'rectangle' && currentZonePoints.length === 2) {
    // 矩形
    const p1 = currentZonePoints[0];
    const p2 = currentZonePoints[1];
    const width = Math.abs(p2.x - p1.x);
    const height = Math.abs(p2.z - p1.z);
    const centerX = (p1.x + p2.x) / 2;
    const centerZ = (p1.z + p2.z) / 2;
    
    geometry = new THREE.PlaneGeometry(width, height);
    position = new THREE.Vector3(centerX, 0.01, centerZ);
    rotation = new THREE.Euler(-Math.PI / 2, 0, 0);
  } else if (currentDrawTool === 'polygon' && currentZonePoints.length >= 3) {
    // 多边形
    geometry = new THREE.BufferGeometry();
    const vertices = [];
    
    currentZonePoints.forEach(point => {
      vertices.push(point.x, 0, point.z);
    });
    
    // 计算面
    const indices = [];
    for (let i = 1; i < currentZonePoints.length - 1; i++) {
      indices.push(0, i, i + 1);
    }
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    
    // 计算中心点
    const center = new THREE.Vector3();
    currentZonePoints.forEach(point => {
      center.add(point);
    });
    center.divideScalar(currentZonePoints.length);
    
    position = new THREE.Vector3(center.x, 0.01, center.z);
    rotation = new THREE.Euler(0, 0, 0);
  }
  
  if (geometry) {
    const zoneMesh = new THREE.Mesh(geometry, zoneMaterials[currentZoneType]);
    zoneMesh.position.copy(position);
    zoneMesh.rotation.copy(rotation);
    zoneMesh.userData = {
      type: 'zone',
      zoneId: zoneId,
      zoneType: currentZoneType,
      zoneName: zoneName,
      points: currentZonePoints.map(p => ({ x: p.x, z: p.z }))
    };
    
    scene.add(zoneMesh);
    zones.push({
      id: zoneId,
      name: zoneName,
      type: currentZoneType,
      color: zoneTypeColors[currentZoneType],
      mesh: zoneMesh
    });
    
    console.log('区域绘制完成:', zoneName, '类型:', currentZoneType);
  }
  
  // 重置绘制状态
  isDrawingZone = false;
  currentDrawTool = null;
  currentZonePoints = [];
  
  if (currentZoneMesh) {
    scene.remove(currentZoneMesh);
    currentZoneMesh = null;
  }
}

// 获取区域类型名称
function getZoneTypeName(zoneType) {
  const typeNames = {
    receiving: '收货区',
    storage: '存储区',
    shipping: '出库区',
    picking: '拣选区',
    packing: '打包区',
    office: '办公区',
    charging: '充电区',
    other: '其他区'
  };
  return typeNames[zoneType] || '未知区域';
}

// 清空所有区域
function clearAllZones() {
  zones.forEach(zone => {
    if (zone.mesh) {
      scene.remove(zone.mesh);
    }
  });
  zones = [];
  
  // 清理办公区墙体及其门/窗
  const officeWallsToRemove = sceneObjects.filter(obj => 
    obj.userData.type === 'officeWall'
  );
  
  officeWallsToRemove.forEach(wall => {
    // 清理墙体上的门/窗
    if (wall.userData.openings && wall.userData.openings.length > 0) {
      wall.userData.openings.forEach(opening => {
        if (opening.mesh) {
          scene.remove(opening.mesh);
          const openingIndex = sceneObjects.indexOf(opening.mesh);
          if (openingIndex > -1) {
            sceneObjects.splice(openingIndex, 1);
          }
        }
      });
    }
    // 清理墙体
    scene.remove(wall);
    const wallIndex = sceneObjects.indexOf(wall);
    if (wallIndex > -1) {
      sceneObjects.splice(wallIndex, 1);
    }
  });
  
  console.log('清空所有区域，清理了', officeWallsToRemove.length, '个办公区墙体');
}

// 删除指定区域
function deleteZone(zoneId) {
  console.log('ThreeScene.deleteZone 被调用:', zoneId, 'zones数组长度:', zones.length);
  console.log('zones数组内容:', zones.map(z => ({ id: z.id, name: z.name })));
  
  const index = zones.findIndex(zone => zone.id === zoneId);
  console.log('找到的索引:', index);
  
  if (index > -1) {
    const zone = zones[index];
    console.log('找到功能区:', zone.name, 'mesh:', !!zone.mesh);
    
    if (zone.mesh) {
      scene.remove(zone.mesh);
      console.log('已删除功能区 mesh');
    }
    zones.splice(index, 1);
    
    // 删除关联的名称标签
    const labelsToRemove = sceneObjects.filter(obj => 
      obj.userData.type === 'zoneLabel' && obj.userData.zoneId === zoneId
    );
    console.log('找到', labelsToRemove.length, '个需要删除的名称标签');
    
    labelsToRemove.forEach(label => {
      scene.remove(label);
      const labelIndex = sceneObjects.indexOf(label);
      if (labelIndex > -1) {
        sceneObjects.splice(labelIndex, 1);
      }
      console.log('已删除名称标签:', label.userData.text);
    });
    
    // 删除关联的办公区墙体及其门/窗
    const officeWallsToRemove = sceneObjects.filter(obj => 
      obj.userData.type === 'officeWall' && obj.userData.zoneId === zoneId
    );
    console.log('找到', officeWallsToRemove.length, '个需要删除的办公区墙体');
    
    officeWallsToRemove.forEach(wall => {
      // 清理墙体上的门/窗
      if (wall.userData.openings && wall.userData.openings.length > 0) {
        wall.userData.openings.forEach(opening => {
          if (opening.mesh) {
            scene.remove(opening.mesh);
            const openingIndex = sceneObjects.indexOf(opening.mesh);
            if (openingIndex > -1) {
              sceneObjects.splice(openingIndex, 1);
            }
          }
        });
      }
      // 清理墙体
      scene.remove(wall);
      const wallIndex = sceneObjects.indexOf(wall);
      if (wallIndex > -1) {
        sceneObjects.splice(wallIndex, 1);
      }
    });
    
    console.log('删除区域完成:', zoneId, '同时删除', labelsToRemove.length, '个名称标签和', officeWallsToRemove.length, '个办公区墙体');
  } else {
    console.warn('未找到功能区:', zoneId);
  }
}

// 获取场景对象
function getSceneObjects() {
  // 从 sceneObjects 获取基础对象（包含墙体、门、窗、立柱、标语）
  const baseObjects = sceneObjects.filter(obj => obj.userData.modelType || obj.userData.modelName ||
                                     obj.userData.type === 'door' || obj.userData.type === 'window' ||
                                     obj.userData.type === 'pillar' || obj.userData.type === 'wallSign');
  
  // 【调试日志】记录外墙标语对象的数据
  const wallSigns = baseObjects.filter(obj => obj.userData.type === 'wallSign');
  if (wallSigns.length > 0) {
    console.log('【getSceneObjects-外墙标语检查】', wallSigns.map(obj => ({
      uuid: obj.uuid,
      text: obj.userData.text,
      wallIndex: obj.userData.wallIndex,
      offsetAlongWall: obj.userData.offsetAlongWall,
      position: { x: obj.position.x, y: obj.position.y, z: obj.position.z }
    })));
  }

  return baseObjects;
}

// 获取选中对象数量
function getSelectedObjectsCount() {
  return selectedObjects.length;
}

// 获取场景对象数量
function getObjectsCount() {
  return sceneObjects.filter(obj => obj.userData.modelType || obj.userData.type === 'door' || obj.userData.type === 'window').length;
}

// 获取选中对象数组（用于保存前同步数据）
function getSelectedObjects() {
  return selectedObjects;
}

// 同步选中对象数据到场景对象（兜底保险）
function syncSelectedObjects() {
  console.log('【同步检查】选中对象数量:', selectedObjects.length);
  let syncCount = 0;

  selectedObjects.forEach(selectedObj => {
    // 在 sceneObjects 中查找对应的对象
    const sceneObj = sceneObjects.find(o => o.uuid === selectedObj.uuid);
    
    // 【调试日志】记录引用对比情况
    const isSameRef = sceneObj === selectedObj;
    console.log('【syncSelectedObjects-检查】', {
      uuid: selectedObj.uuid,
      type: selectedObj.userData?.type,
      foundInScene: !!sceneObj,
      isSameReference: isSameRef,
      selectedOffset: selectedObj.userData?.offsetAlongWall,
      sceneOffset: sceneObj?.userData?.offsetAlongWall
    });
    
    if (sceneObj && sceneObj !== selectedObj) {
      // 如果找到的对象引用不一致，同步关键数据
      console.log('【同步数据】对象引用不一致，同步数据:', selectedObj.uuid, selectedObj.userData.type);

      // 同步外墙标语的 offsetAlongWall
      if (selectedObj.userData.type === 'wallSign' &&
          selectedObj.userData.offsetAlongWall !== undefined) {
        const oldSceneOffset = sceneObj.userData.offsetAlongWall;
        sceneObj.userData.offsetAlongWall = selectedObj.userData.offsetAlongWall;
        console.log('【同步数据】同步 offsetAlongWall:', {
          uuid: selectedObj.uuid,
          oldValue: oldSceneOffset,
          newValue: selectedObj.userData.offsetAlongWall
        });
        syncCount++;
      }

      // 同步位置信息
      if (selectedObj.position) {
        sceneObj.position.copy(selectedObj.position);
      }
    } else if (sceneObj && isSameRef) {
      // 【调试日志】引用一致的情况
      console.log('【syncSelectedObjects-引用一致】无需同步，引用相同:', {
        uuid: selectedObj.uuid,
        type: selectedObj.userData?.type,
        offsetAlongWall: selectedObj.userData?.offsetAlongWall
      });
    }
  });

  console.log('【同步完成】同步了', syncCount, '个对象的数据');
  return syncCount;
}

// 计算对象尺寸
function calculateObjectDimensions(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  const size = box.getSize(new THREE.Vector3());
  // 转换为厘米并格式化
  const length = Math.round(size.x * 10);
  const width = Math.round(size.z * 10);
  const height = Math.round(size.y * 10);
  return `${length}×${width}×${height}cm`;
}

// 更新货架
function updateShelf(shelf, config) {
  // 这里可以实现货架参数更新逻辑
  console.log('更新货架:', config);
}

// 更新输送线
function updateConveyor(conveyor, config) {
  // 这里可以实现输送线参数更新逻辑
  console.log('更新输送线:', config);
}

// 导出场景图片
function exportImage() {
  renderer.setPixelRatio(window.devicePixelRatio);
  const dataURL = renderer.domElement.toDataURL('image/png');
  
  const link = document.createElement('a');
  link.href = dataURL;
  link.download = `warehouse_scene_${Date.now()}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  console.log('场景图片已导出');
}

// 添加模型
function addModel(modelName) {
  // 默认位置
  const defaultPosition = new THREE.Vector3(0, 0, 0);
  const newModel = addModelInternal(modelName, defaultPosition);
  if (newModel) {
    emit('model-added', newModel);
    console.log('添加模型成功:', modelName);
  } else {
    console.error('添加模型失败:', modelName);
  }
}

// 创建仓库
function createWarehouse(config) {
  // 清除现有场景前，先清除选中状态
  clearSelection();

  // 清除现有场景
  sceneObjects.forEach(obj => scene.remove(obj));
  sceneObjects = [];
  emit('object-deselected');
  
  // 转换单位：m -> cm
  const length = config.length * 100;
  const width = config.width * 100;
  const height = config.height * 100;
  const baseHeight = config.baseHeight * 100;
  const wallThickness = config.wallThickness;
  const wallOpacity = config.wallOpacity;
  
  // 保存仓库配置
  warehouseConfig = {
    ...config,
    length: length,
    width: width,
    height: height,
    baseHeight: baseHeight
  };
  
  // 创建网格地面（使用GridHelper替代实体地面，更清晰显示坐标）
  // 使用固定网格参数：每格1米，总共100×100米
  const gridHelper = new THREE.GridHelper(GRID_TOTAL_SIZE, GRID_DIVISIONS, 0x888888, 0xcccccc);
  gridHelper.position.y = baseHeight;
  gridHelper.position.x = 0; // 与仓库中心对齐（矩形仓库中心在原点）
  gridHelper.position.z = 0; // 与仓库中心对齐
  gridHelper.userData.type = 'floor';

  // 设置GridHelper材质为透明
  gridHelper.material.transparent = true;
  gridHelper.material.opacity = 0.1; // 设置透明度为10%，让地面更通透

  scene.add(gridHelper);
  sceneObjects.push(gridHelper);
  
  // 创建墙体
  const wallMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x888888, 
    transparent: true,
    opacity: wallOpacity,
    roughness: 0.9,
    metalness: 0.1
  });
  
  // 墙体厚度转换为cm
  const thickness = wallThickness;
  
  // 计算墙体位置
  const halfLength = length / 2;
  const halfWidth = width / 2;
  
  // 四面墙
  const walls = [
    // 前墙（Z正方向）
    {
      geometry: new THREE.BoxGeometry(length, height, thickness),
      position: [0, baseHeight + height / 2, halfWidth + thickness / 2],
      type: 'front'
    },
    // 后墙（Z负方向）
    {
      geometry: new THREE.BoxGeometry(length, height, thickness),
      position: [0, baseHeight + height / 2, -halfWidth - thickness / 2],
      type: 'back'
    },
    // 左墙（X负方向）
    {
      geometry: new THREE.BoxGeometry(thickness, height, width + thickness * 2),
      position: [-halfLength - thickness / 2, baseHeight + height / 2, 0],
      type: 'left'
    },
    // 右墙（X正方向）
    {
      geometry: new THREE.BoxGeometry(thickness, height, width + thickness * 2),
      position: [halfLength + thickness / 2, baseHeight + height / 2, 0],
      type: 'right'
    }
  ];
  
  walls.forEach((wall, index) => {
    const wallMesh = new THREE.Mesh(wall.geometry, wallMaterial);
    wallMesh.position.set(...wall.position);
    wallMesh.userData.type = 'wall';
    wallMesh.userData.wallIndex = index;
    wallMesh.userData.wallType = wall.type;
    wallMesh.userData.openings = []; // 存储门窗
    scene.add(wallMesh);
    sceneObjects.push(wallMesh);
  });
  
  // 更新网格辅助线
  const existingGridHelper = scene.getObjectByName('gridHelper');
  if (existingGridHelper) {
    scene.remove(existingGridHelper);
  }

  // 使用固定网格参数：每格1米，总共100×100米
  const newGridHelper = new THREE.GridHelper(GRID_TOTAL_SIZE, GRID_DIVISIONS, 0xaaaaaa, 0xdddddd);
  newGridHelper.name = 'gridHelper';
  newGridHelper.position.y = baseHeight;
  newGridHelper.position.x = 0; // 与仓库中心对齐
  newGridHelper.position.z = 0; // 与仓库中心对齐
  scene.add(newGridHelper);
  
  console.log('仓库创建成功:', config);
}

// 根据2D轮廓点生成多边形3D墙体
function createWarehouseFromShape(shapePoints, config, zones = [], textLabels = []) {
  console.log('createWarehouseFromShape 被调用', shapePoints, config);

  // 检查scene是否已初始化
  if (!scene) {
    console.error('Scene 未初始化！');
    return;
  }

  // 清除现有场景前，先清除选中状态
  clearSelection();

  // 清除现有场景
  sceneObjects.forEach(obj => scene.remove(obj));
  sceneObjects = [];
  
  if (!shapePoints || shapePoints.length < 3) {
    console.error('仓库形状点不足，需要至少3个点');
    return;
  }
  
  // 转换单位：像素 -> cm (1像素 = 0.1米 = 10cm)
  const scaleFactor = 10; // 1像素 = 10cm
  const height = (config.height || 5) * 100; // 米 -> cm
  const baseHeight = (config.baseHeight || 0) * 100; // 米 -> cm
  const wallThickness = config.wallThickness || 20; // cm
  const wallOpacity = config.wallOpacity !== undefined ? config.wallOpacity : 0.8;
  
  // 计算仓库边界和中心
  const bounds = calculateBounds(shapePoints);
  const centerX = (bounds.minX + bounds.maxX) / 2 * scaleFactor;
  const centerZ = (bounds.minY + bounds.maxY) / 2 * scaleFactor;
  const boundsWidth = (bounds.maxX - bounds.minX) * scaleFactor;
  const boundsDepth = (bounds.maxY - bounds.minY) * scaleFactor;

  // 保存仓库配置（包含中心位置）
  warehouseConfig = {
    ...config,
    height: height,
    baseHeight: baseHeight,
    shapePoints: shapePoints,
    centerX: centerX,
    centerZ: centerZ,
    length: boundsWidth,
    width: boundsDepth
  };

  // 创建网格地面（使用固定网格参数）
  // 每格1米，总共100×100米，中心与仓库中心对齐
  const gridHelper = new THREE.GridHelper(GRID_TOTAL_SIZE, GRID_DIVISIONS, 0x888888, 0xcccccc);
  gridHelper.position.y = baseHeight;
  gridHelper.position.x = centerX; // 与仓库中心对齐
  gridHelper.position.z = centerZ; // 与仓库中心对齐
  gridHelper.userData.type = 'floor';

  // 设置GridHelper材质为透明
  gridHelper.material.transparent = true;
  gridHelper.material.opacity = 0.1; // 设置透明度为10%，让地面更通透

  scene.add(gridHelper);
  sceneObjects.push(gridHelper);
  
  // 创建墙体材质
  const wallMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x888888, 
    transparent: true,
    opacity: wallOpacity,
    roughness: 0.9,
    metalness: 0.1
  });
  
  // 根据轮廓点生成墙体
  // shapePoints是2D点数组，需要转换为3D墙体
  // 2D坐标系: X向右, Y向下 (画布坐标)
  // 3D坐标系: X向右, Z向下 (对应2D的Y)
  const walls = [];
  for (let i = 0; i < shapePoints.length - 1; i++) {
    const p1 = shapePoints[i];
    const p2 = shapePoints[i + 1];
    
    // 计算墙体参数
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const length = Math.sqrt(dx * dx + dy * dy) * scaleFactor;
    const angle = Math.atan2(dy, dx);
    
    // 墙体中心点 (2D的Y对应3D的Z，但需要取反因为2D的Y向下而3D的Z向上)
    const centerX = (p1.x + p2.x) / 2 * scaleFactor;
    const centerZ = (p1.y + p2.y) / 2 * scaleFactor;
    
    // 创建墙体几何体
    const wallGeometry = new THREE.BoxGeometry(length, height, wallThickness);
    const wallMesh = new THREE.Mesh(wallGeometry, wallMaterial);
    
    // 设置位置和旋转
    // 注意：2D的Y轴向下，3D的Z轴向上，所以需要取反Z坐标
    wallMesh.position.set(centerX, baseHeight + height / 2, centerZ);
    // 旋转角度：2D的atan2(dy,dx)需要转换为3D的Y轴旋转
    // 由于2D的Y向下，3D的Z向上，旋转方向相反
    wallMesh.rotation.y = -angle;
    
    // 计算墙体类型（基于角度）
    // 角度是墙体的方向，需要转换为墙体法线方向（面向仓库内部）
    let wallType = 'front';
    const angleDeg = (angle * 180 / Math.PI) % 360;
    const normalizedAngle = angleDeg < 0 ? angleDeg + 360 : angleDeg;
    
    // 根据角度判断墙体类型
    // 角度0°：墙体沿X轴正方向（从起点到终点是向右），这是前墙（面向Z负方向）
    // 角度90°：墙体沿Z轴正方向（从起点到终点是向下），这是右墙（面向X负方向）
    // 角度180°：墙体沿X轴负方向（从起点到终点是向左），这是后墙（面向Z正方向）
    // 角度-90°/270°：墙体沿Z轴负方向（从起点到终点是向上），这是左墙（面向X正方向）
    if (normalizedAngle >= 45 && normalizedAngle < 135) {
      // 角度90°左右 - 墙体沿Z轴，这是右墙
      wallType = 'right';
    } else if (normalizedAngle >= 135 && normalizedAngle < 225) {
      // 角度180°左右 - 墙体沿X轴负方向，这是后墙
      wallType = 'back';
    } else if (normalizedAngle >= 225 && normalizedAngle < 315) {
      // 角度270°左右 - 墙体沿Z轴负方向，这是左墙
      wallType = 'left';
    } else {
      // 角度0°左右 - 墙体沿X轴正方向，这是前墙
      wallType = 'front';
    }
    
    // 存储墙体信息
    wallMesh.userData.type = 'wall';
    wallMesh.userData.wallType = wallType;
    wallMesh.userData.wallIndex = i;
    wallMesh.userData.startPoint = p1;
    wallMesh.userData.endPoint = p2;
    wallMesh.userData.length = length;
    wallMesh.userData.baseHeight = baseHeight; // 存储基础高度，供门窗使用
    wallMesh.userData.openings = []; // 存储门窗等开口
    
    scene.add(wallMesh);
    sceneObjects.push(wallMesh);
    walls.push(wallMesh);
    
    console.log(`创建墙体 ${i}: 长度=${(length/100).toFixed(2)}m, 角度=${(angle * 180 / Math.PI).toFixed(2)}°`);
  }
  
  // 更新网格辅助线
  const existingGridHelper2 = scene.getObjectByName('gridHelper');
  if (existingGridHelper2) {
    scene.remove(existingGridHelper2);
  }

  // 使用固定网格参数：每格1米，总共100×100米
  const newGridHelper = new THREE.GridHelper(GRID_TOTAL_SIZE, GRID_DIVISIONS, 0xaaaaaa, 0xdddddd);
  newGridHelper.name = 'gridHelper';
  newGridHelper.position.y = baseHeight;
  newGridHelper.position.x = (bounds.minX + bounds.maxX) / 2 * scaleFactor; // 与仓库中心对齐
  newGridHelper.position.z = (bounds.minY + bounds.maxY) / 2 * scaleFactor; // 与仓库中心对齐
  scene.add(newGridHelper);

  // 调整相机位置以适应仓库大小
  // 使用前面已定义的centerX, centerZ, boundsWidth, boundsDepth
  const maxSize = Math.max(boundsWidth, boundsDepth);

  // 调试信息
  console.log('仓库边界:', bounds);
  console.log('仓库中心:', { x: centerX, z: centerZ });
  console.log('仓库尺寸:', maxSize, 'cm');
  console.log('墙体高度:', height, 'cm');

  // 更新坐标轴位置到仓库中心
  updateDirectionLabels(centerX, baseHeight + 10, centerZ, maxSize);
  
  // 设置相机位置 - 使用更合理的距离
  const cameraDistance = maxSize * 1.2; // 1.2倍仓库尺寸
  camera.position.set(
    centerX + cameraDistance,
    Math.max(maxSize * 0.6, height * 1.2),
    centerZ + cameraDistance
  );
  camera.lookAt(centerX, baseHeight + height / 2, centerZ);
  camera.updateProjectionMatrix(); // 更新投影矩阵
  
  if (controls) {
    controls.target.set(centerX, baseHeight + height / 2, centerZ);
    controls.update();
  }
  
  console.log('相机位置:', camera.position);
  console.log('多边形仓库创建成功，墙体数量:', walls.length);
  
  // 创建功能区域
  if (zones && zones.length > 0) {
    createZonesIn3D(zones, baseHeight, scaleFactor);
  }
  
  // 创建文字标注
  if (textLabels && textLabels.length > 0) {
    createTextLabelsIn3D(textLabels, baseHeight, scaleFactor);
  }
  
  return walls;
}

// 创建立柱
function createPillar(position, pillarHeight = 500) {
  const width = 40;  // cm
  const depth = 30;  // cm
  const height = pillarHeight; // 默认500cm，可调整
  
  // 创建Group作为立柱根对象
  const pillarGroup = new THREE.Group();
  
  // 创建立柱主体几何体 - 红色
  const pillarGeometry = new THREE.BoxGeometry(width, height, depth);
  const pillarMaterial = new THREE.MeshStandardMaterial({
    color: 0xFF0000,  // 红色
    transparent: true,
    opacity: 0.9,
    roughness: 0.6,
    metalness: 0.2
  });
  const pillarMesh = new THREE.Mesh(pillarGeometry, pillarMaterial);
  pillarGroup.add(pillarMesh);
  
  // 创建白色棱廓线
  const edges = new THREE.EdgesGeometry(pillarGeometry);
  const lineMaterial = new THREE.LineBasicMaterial({ color: 0xFFFFFF, linewidth: 2 });
  const wireframe = new THREE.LineSegments(edges, lineMaterial);
  pillarGroup.add(wireframe);
  
  // 设置位置 - 底部对齐地面
  const baseHeight = warehouseConfig?.baseHeight || 0;
  pillarGroup.position.set(position.x, baseHeight + height / 2, position.z);
  
  // 设置 userData
  pillarGroup.userData.type = 'pillar';
  pillarGroup.userData.modelType = 'pillar';
  pillarGroup.userData.name = '立柱';
  pillarGroup.userData.width = width;
  pillarGroup.userData.height = height;
  pillarGroup.userData.depth = depth;
  pillarGroup.userData.editableHeight = true;  // 标记可编辑高度
  pillarGroup.userData.baseHeight = baseHeight;
  
  // 添加到场景
  scene.add(pillarGroup);
  sceneObjects.push(pillarGroup);
  
  console.log('创建立柱成功:', { x: position.x, z: position.z, width, height, depth });
  
  return pillarGroup;
}

// 更新立柱高度
function updatePillarHeight(pillar, newHeight) {
  if (!pillar || pillar.userData.type !== 'pillar') {
    console.error('无效的立柱对象');
    return false;
  }
  
  // 高度范围限制：300cm - 1200cm
  const minHeight = 300;
  const maxHeight = 1200;
  const clampedHeight = Math.max(minHeight, Math.min(maxHeight, newHeight));
  
  const width = pillar.userData.width || 40;
  const depth = pillar.userData.depth || 30;
  const baseHeight = pillar.userData.baseHeight || 0;
  
  // 清除旧的子对象
  while (pillar.children.length > 0) {
    const child = pillar.children[0];
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
    pillar.remove(child);
  }
  
  // 创建新的主体几何体
  const pillarGeometry = new THREE.BoxGeometry(width, clampedHeight, depth);
  const pillarMaterial = new THREE.MeshStandardMaterial({
    color: 0xFF0000,
    transparent: true,
    opacity: 0.9,
    roughness: 0.6,
    metalness: 0.2
  });
  const pillarMesh = new THREE.Mesh(pillarGeometry, pillarMaterial);
  pillar.add(pillarMesh);
  
  // 创建新的棱廓线
  const edges = new THREE.EdgesGeometry(pillarGeometry);
  const lineMaterial = new THREE.LineBasicMaterial({ color: 0xFFFFFF, linewidth: 2 });
  const wireframe = new THREE.LineSegments(edges, lineMaterial);
  pillar.add(wireframe);
  
  // 更新位置和userData
  pillar.position.y = baseHeight + clampedHeight / 2;
  pillar.userData.height = clampedHeight;
  
  console.log('立柱高度更新成功:', { newHeight: clampedHeight });
  return true;
}

// 创建外墙标语
function createWallSign(wallObject, referencePoint, config = {}) {
  // 直接使用传入的墙体对象
  const wall = wallObject;
  if (!wall) {
    console.error('未提供墙体对象');
    return null;
  }
  
  // 从墙体对象获取信息
  const wallIndex = wall.userData.wallIndex;
  const wallType = wall.userData.wallType;
  
  const defaultConfig = {
    text: '外墙标语',
    fontSize: 24,
    textColor: '#FFFFFF',
    bgColor: '#0066CC',
    signHeight: 150  // 默认离地高度1.5米
  };
  
  const signConfig = { ...defaultConfig, ...config };
  const baseHeight = warehouseConfig?.baseHeight || 0;
  
  // 使用Canvas创建文字纹理
  function createSignTexture(text, fontSize, textColor, bgColor) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // 计算文字尺寸
    ctx.font = `bold ${fontSize}px Arial`;
    const textMetrics = ctx.measureText(text);
    const textWidth = textMetrics.width;
    const textHeight = fontSize * 1.2;
    
    // 添加边距
    const padding = fontSize * 0.5;
    const width = Math.max(textWidth + padding * 2, 100);
    const height = textHeight + padding;
    
    canvas.width = width;
    canvas.height = height;
    
    // 绘制背景
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, width, height);
    
    // 绘制文字
    ctx.font = `bold ${fontSize}px Arial`;
    ctx.fillStyle = textColor;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, width / 2, height / 2);
    
    return {
      texture: new THREE.CanvasTexture(canvas),
      width: width / 10 * 30, // 转换为3D单位，放大30倍
      height: height / 10 * 30
    };
  }
  
  const { texture, width, height } = createSignTexture(
    signConfig.text,
    signConfig.fontSize,
    signConfig.textColor,
    signConfig.bgColor
  );
  
  // 创建标语平面
  const geometry = new THREE.PlaneGeometry(width, height);
  const material = new THREE.MeshBasicMaterial({
    map: texture,
    transparent: true,
    side: THREE.DoubleSide,
    polygonOffset: true,
    polygonOffsetFactor: -10,  // 确保标语在墙体前方渲染，解决 Z-fighting
    polygonOffsetUnits: -10
  });
  
  const signMesh = new THREE.Mesh(geometry, material);
  
  // 获取墙体信息
  const wallCenter = wall.position.clone();
  const wallRotation = wall.rotation.y;
  const wallLength = wall.userData.length;
  
  // 计算墙体方向向量（沿墙体长度方向）
  const wallDirection = new THREE.Vector3(
    Math.cos(-wallRotation),
    0,
    Math.sin(-wallRotation)
  );
  
  // 计算墙体法向量（垂直于墙体，指向外侧）
  const wallNormal = new THREE.Vector3(
    Math.sin(-wallRotation),
    0,
    -Math.cos(-wallRotation)
  );
  
  // 计算沿墙体方向的偏移量
  // 如果提供了有效的偏移配置，使用配置值；否则默认放在墙体中心（偏移为0）
  let offsetAlongWall = 0;
  if (config.offsetAlongWall !== undefined) {
    // 使用配置中的偏移值（用于更新标语位置）
    offsetAlongWall = config.offsetAlongWall;
  }
  // 否则偏移为0，即放在墙体中心
  
  // 注意：不限制标语在墙体范围内，允许悬空放置
  
  // 标语位置 = 墙体中心 + 沿墙体方向的偏移 + 法向量偏移（向外10cm，确保不被墙体遮挡）
  const signPosition = wallCenter.clone()
    .add(wallDirection.clone().multiplyScalar(offsetAlongWall))
    .add(wallNormal.clone().multiplyScalar(10)); // 向外偏移10cm，避免被墙体遮挡
  
  // 设置Y坐标（使用配置的signHeight，不再随字体大小变化）
  const signHeightConfig = signConfig.signHeight !== undefined ? signConfig.signHeight : 150;
  signPosition.y = baseHeight + signHeightConfig; // 基础高度 + 配置的离地高度
  
  // 设置userData（在添加到墙体之前设置，避免被转换）
  signMesh.userData.type = 'wallSign';
  signMesh.userData.modelType = 'wallSign';
  signMesh.userData.name = '外墙标语';
  signMesh.userData.text = signConfig.text;
  signMesh.userData.fontSize = signConfig.fontSize;
  signMesh.userData.textColor = signConfig.textColor;
  signMesh.userData.bgColor = signConfig.bgColor;
  signMesh.userData.wallType = wallType;
  signMesh.userData.wallIndex = wallIndex;
  signMesh.userData.offsetAlongWall = offsetAlongWall;
  signMesh.userData.width = width;
  signMesh.userData.height = height;
  signMesh.userData.signHeight = signHeightConfig;  // 保存离地高度配置

  // 将标语添加到场景（而非墙体children），保持世界坐标
  // 父子级关联会导致坐标转换问题，改为通过wallIndex在保存/加载时重新关联
  signMesh.position.copy(signPosition);
  // 标语旋转 = 墙体旋转 + 180度（让标语面向外侧）
  signMesh.rotation.y = wallRotation + Math.PI;
  scene.add(signMesh);
  sceneObjects.push(signMesh);

  console.log('创建外墙标语成功:', {
    text: signConfig.text,
    wallType,
    wallIndex,
    position: signPosition,
    offsetAlongWall
  });

  return signMesh;
}

// 更新外墙标语
function updateWallSign(sign, config) {
  if (!sign || sign.userData.type !== 'wallSign') {
    console.error('无效的标语对象');
    return false;
  }
  
  // 获取当前配置，保留原有的 offsetAlongWall 和 signHeight
  const currentConfig = {
    text: sign.userData.text,
    fontSize: sign.userData.fontSize,
    textColor: sign.userData.textColor,
    bgColor: sign.userData.bgColor,
    wallType: sign.userData.wallType,
    offsetAlongWall: sign.userData.offsetAlongWall, // 保留原有偏移
    signHeight: sign.userData.signHeight !== undefined ? sign.userData.signHeight : 150, // 保留原有高度
    ...config
  };
  
  // 从场景中移除旧标语
  scene.remove(sign);
  const index = sceneObjects.indexOf(sign);
  if (index > -1) {
    sceneObjects.splice(index, 1);
  }
  
  // 释放资源
  if (sign.material.map) sign.material.map.dispose();
  if (sign.material) sign.material.dispose();
  if (sign.geometry) sign.geometry.dispose();
  
  // 查找原来的墙体对象
  const wallIndex = sign.userData.wallIndex;
  const wall = sceneObjects.find(obj => obj.userData.type === 'wall' && obj.userData.wallIndex === wallIndex);
  
  if (!wall) {
    console.error('更新标语时未找到原墙体:', wallIndex);
    return false;
  }
  
  // 创建新标语 - 使用墙体对象和配置（包含 offsetAlongWall）
  const newSign = createWallSign(wall, null, currentConfig);
  
  // 选中新标语
  if (newSign) {
    selectObject(newSign);
    console.log('外墙标语更新成功:', currentConfig);
    return true;
  }
  
  return false;
}

// 移动外墙标语（限制在墙面）
function moveWallSign(sign, delta) {
  if (!sign || sign.userData.type !== 'wallSign') {
    console.error('无效的标语对象');
    return false;
  }

  const wallType = sign.userData.wallType;
  const wallIndex = sign.userData.wallIndex;
  
  // 保存当前Y坐标，确保移动时高度不变
  const currentY = sign.position.y;
  
  // 【调试日志】记录移动前的状态
  const oldOffset = sign.userData.offsetAlongWall;
  console.log('【moveWallSign-开始】', {
    uuid: sign.uuid,
    oldOffsetAlongWall: oldOffset,
    position: { x: sign.position.x, y: sign.position.y, z: sign.position.z },
    delta: { x: delta.x, y: delta.y, z: delta.z }
  });

  // 查找对应的墙体对象
  const wall = sceneObjects.find(obj =>
    obj.userData.type === 'wall' && obj.userData.wallIndex === wallIndex
  );

  if (!wall) {
    console.error('未找到墙体对象:', wallIndex);
    return false;
  }

  // 计算墙体信息
  const wallCenter = wall.position.clone();
  const wallRotation = wall.rotation.y;
  const wallLength = wall.userData.length;
  const wallDirection = new THREE.Vector3(
    Math.cos(-wallRotation), 0, Math.sin(-wallRotation)
  );
  const wallNormal = new THREE.Vector3(
    Math.sin(-wallRotation), 0, -Math.cos(-wallRotation)
  );

  // 计算当前位置相对于墙体的偏移量
  const relativePos = sign.position.clone().sub(wallCenter);
  let offsetAlongWall = relativePos.dot(wallDirection);

  // 将delta投影到墙体方向，计算沿墙体的位移
  const deltaVector = new THREE.Vector3(delta.x, 0, delta.z);
  const movementAlongWall = deltaVector.dot(wallDirection);
  console.log('移动前:', { offsetAlongWall, delta: { x: delta.x, z: delta.z }, movementAlongWall, wallType });
  offsetAlongWall += movementAlongWall;

  // 注意：不限制标语在墙体范围内，允许悬空放置

  // 更新标语位置（始终贴合墙面）
  sign.position.copy(wallCenter)
    .add(wallDirection.clone().multiplyScalar(offsetAlongWall))
    .add(wallNormal.clone().multiplyScalar(5)); // 向外偏移5cm

  // Y方向保持当前高度（不再随鼠标移动改变，改为通过编辑功能调整）
  // 保留原有的Y坐标，确保移动时高度不变
  sign.position.y = currentY;

  // 更新userData中的偏移量
  sign.userData.offsetAlongWall = offsetAlongWall;

  // 【调试日志】记录移动后的状态
  console.log('【moveWallSign-完成】', {
    uuid: sign.uuid,
    oldOffsetAlongWall: oldOffset,
    newOffsetAlongWall: offsetAlongWall,
    deltaOffset: offsetAlongWall - (oldOffset || 0),
    position: { x: sign.position.x, y: sign.position.y, z: sign.position.z },
    wallIndex: wallIndex,
    wallType: wallType
  });
  return true;
}

// 在3D场景中创建功能区域
function createZonesIn3D(zonesData, baseHeight, scaleFactor) {
  // 清空现有的zones数组并重新填充
  zones = [];
  
  // 获取仓库墙体高度和材质参数
  const wallHeight = warehouseConfig?.height || 500; // 默认5米
  const wallThickness = warehouseConfig?.wallThickness || 20; // 默认20cm
  const wallOpacity = warehouseConfig?.wallOpacity !== undefined ? warehouseConfig.wallOpacity : 0.8;
  
  // 创建墙体材质（与仓库墙体相同）
  const wallMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x888888, 
    transparent: true,
    opacity: wallOpacity,
    roughness: 0.9,
    metalness: 0.1
  });
  
  zonesData.forEach((zone, index) => {
    if (!zone.points || zone.points.length < 3) return;
    
    // 计算功能区的中心点和尺寸
    const bounds = calculateBounds(zone.points);
    const width = (bounds.maxX - bounds.minX) * scaleFactor;
    const depth = (bounds.maxY - bounds.minY) * scaleFactor;
    const centerX = (bounds.minX + bounds.maxX) / 2 * scaleFactor;
    const centerZ = (bounds.minY + bounds.maxY) / 2 * scaleFactor;
    
    // 创建功能区地面 - 使用更淡的背景色
    const zoneGeometry = new THREE.PlaneGeometry(width, depth);
    const zoneMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xffffff, // 白色背景
      transparent: true,
      opacity: 0.15, // 更透明
      roughness: 0.8,
      metalness: 0.2,
      side: THREE.DoubleSide
    });
    const zoneMesh = new THREE.Mesh(zoneGeometry, zoneMaterial);
    zoneMesh.rotation.x = -Math.PI / 2;
    zoneMesh.position.set(centerX, baseHeight + 1, centerZ);
    zoneMesh.userData.type = 'zone';
    zoneMesh.userData.zoneId = zone.id;
    zoneMesh.userData.zoneName = zone.name;
    scene.add(zoneMesh);
    sceneObjects.push(zoneMesh);
    
    // 将功能区添加到模块级的zones数组
    zones.push({
      id: zone.id,
      name: zone.name,
      mesh: zoneMesh
    });
    
    // 创建虚线边框 - 使用更明显的方式
    const borderColor = zone.color || 0x4fc3f7;
    createDashedBorder(width, depth, centerX, baseHeight + 2, centerZ, borderColor);
    
    // 创建功能区名称标签 - 字体大小根据区域尺寸自动调整
    const minDimension = Math.min(width, depth);
    const fontSize = Math.max(48, Math.min(96, minDimension / 5)); // 根据区域大小自动调整字体
    createZoneLabel(zone.name, centerX, baseHeight + Math.max(200, minDimension / 3), centerZ, borderColor, fontSize, width, depth, zone.id);
    
    // 为办公区生成墙体
    if (zone.type === 'office' && zone.points && zone.points.length >= 3) {
      createOfficeZoneWalls(zone, zone.points, baseHeight, scaleFactor, wallHeight, wallThickness, wallMaterial);
    }
    
    console.log(`创建功能区 ${index}: ${zone.name}, 类型: ${zone.type || 'unknown'}, 尺寸: ${(width/100).toFixed(1)}m x ${(depth/100).toFixed(1)}m, 字体: ${fontSize}px`);
  });
}

// 为办公区创建墙体
function createOfficeZoneWalls(zone, points, baseHeight, scaleFactor, wallHeight, wallThickness, wallMaterial) {
  console.log(`为办公区 ${zone.name} 创建墙体，点数: ${points.length}`);
  
  // 确保点是闭合的（首尾相连）
  let wallPoints = [...points];
  if (wallPoints.length > 0) {
    const firstPoint = wallPoints[0];
    const lastPoint = wallPoints[wallPoints.length - 1];
    // 如果首尾不相连，添加闭合点
    if (firstPoint.x !== lastPoint.x || firstPoint.y !== lastPoint.y) {
      wallPoints.push(firstPoint);
    }
  }
  
  // 为每条边创建墙体
  for (let i = 0; i < wallPoints.length - 1; i++) {
    const p1 = wallPoints[i];
    const p2 = wallPoints[i + 1];
    
    // 计算墙体参数
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const length = Math.sqrt(dx * dx + dy * dy) * scaleFactor;
    const angle = Math.atan2(dy, dx);
    
    // 墙体中心点
    const centerX = (p1.x + p2.x) / 2 * scaleFactor;
    const centerZ = (p1.y + p2.y) / 2 * scaleFactor;
    
    // 创建墙体几何体
    const wallGeometry = new THREE.BoxGeometry(length, wallHeight, wallThickness);
    const wallMesh = new THREE.Mesh(wallGeometry, wallMaterial);
    
    // 设置位置和旋转
    wallMesh.position.set(centerX, baseHeight + wallHeight / 2, centerZ);
    wallMesh.rotation.y = -angle;
    
    // 存储墙体信息
    wallMesh.userData.type = 'officeWall';
    wallMesh.userData.zoneId = zone.id;
    wallMesh.userData.wallIndex = i;
    wallMesh.userData.startPoint = p1;
    wallMesh.userData.endPoint = p2;
    wallMesh.userData.length = length;
    wallMesh.userData.baseHeight = baseHeight;
    wallMesh.userData.height = wallHeight;
    wallMesh.userData.openings = []; // 存储门窗等开口
    
    scene.add(wallMesh);
    sceneObjects.push(wallMesh);
    
    console.log(`创建办公区墙体 ${i}: 长度=${(length/100).toFixed(2)}m, 角度=${(angle * 180 / Math.PI).toFixed(2)}°`);
  }
}

// 创建虚线边框 - 水平躺在地面上
function createDashedBorder(width, depth, x, y, z, color) {
  const material = new THREE.LineDashedMaterial({
    color: color,
    linewidth: 3,
    scale: 1,
    dashSize: 30, // 虚线段长度
    gapSize: 20,  // 虚线间隔
  });
  
  // 创建矩形边框的点 - 直接在地面上（Y=0）
  const points = [];
  const halfWidth = width / 2;
  const halfDepth = depth / 2;
  
  // 矩形四个角 - XZ平面（水平）
  points.push(new THREE.Vector3(x - halfWidth, y, z - halfDepth));
  points.push(new THREE.Vector3(x + halfWidth, y, z - halfDepth));
  points.push(new THREE.Vector3(x + halfWidth, y, z + halfDepth));
  points.push(new THREE.Vector3(x - halfWidth, y, z + halfDepth));
  points.push(new THREE.Vector3(x - halfWidth, y, z - halfDepth));
  
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const line = new THREE.Line(geometry, material);
  line.computeLineDistances(); // 必须调用以显示虚线
  
  scene.add(line);
  sceneObjects.push(line);
  
  // 同时添加一个实线边框增强可见性
  const solidMaterial = new THREE.LineBasicMaterial({ 
    color: color, 
    linewidth: 4,
    transparent: true,
    opacity: 0.6
  });
  const solidLine = new THREE.Line(geometry.clone(), solidMaterial);
  solidLine.position.y = y + 1; // 稍微抬高一点避免重叠
  
  scene.add(solidLine);
  sceneObjects.push(solidLine);
}

// 创建功能区名称标签
function createZoneLabel(text, x, y, z, color, fontSize = 48, zoneWidth = 300, zoneDepth = 300, zoneId = null) {
  // 创建画布 - 根据区域大小调整画布尺寸
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  
  // 根据区域大小动态调整画布尺寸
  const minZoneSize = Math.min(zoneWidth, zoneDepth);
  const scale = Math.max(1, minZoneSize / 500); // 根据区域大小调整缩放
  canvas.width = Math.min(1024, Math.max(512, minZoneSize * 1.5));
  canvas.height = Math.min(256, Math.max(128, minZoneSize * 0.4));
  
  // 绘制背景 - 使用更醒目的颜色
  context.fillStyle = 'rgba(255, 255, 255, 0.95)';
  context.fillRect(0, 0, canvas.width, canvas.height);
  
  // 绘制粗边框
  context.strokeStyle = '#' + new THREE.Color(color).getHexString();
  context.lineWidth = 8;
  context.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);
  
  // 绘制内部阴影效果
  context.fillStyle = '#' + new THREE.Color(color).getHexString() + '20'; // 20%透明度的颜色
  context.fillRect(8, 8, canvas.width - 16, canvas.height - 16);
  
  // 绘制文字 - 根据区域大小调整字体
  const adjustedFontSize = Math.min(fontSize * scale, canvas.height * 0.5);
  context.font = `bold ${adjustedFontSize}px Arial, sans-serif`;
  context.fillStyle = '#222222';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  
  // 创建纹理
  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  
  // 创建精灵 - 根据区域大小调整缩放
  const spriteMaterial = new THREE.SpriteMaterial({ 
    map: texture,
    transparent: true,
    opacity: 0.98
  });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.position.set(x, y, z);
  
  // 根据区域大小动态调整标签尺寸
  const labelWidth = Math.min(500, Math.max(200, minZoneSize * 0.8));
  const labelHeight = labelWidth * (canvas.height / canvas.width);
  sprite.scale.set(labelWidth, labelHeight, 1);
  
  sprite.userData.type = 'zoneLabel';
  sprite.userData.text = text;
  sprite.userData.zoneWidth = zoneWidth;
  sprite.userData.zoneDepth = zoneDepth;
  sprite.userData.zoneId = zoneId; // 存储关联的功能区ID
  
  scene.add(sprite);
  sceneObjects.push(sprite);
}

// 在3D场景中创建文字标注
function createTextLabelsIn3D(textLabels, baseHeight, scaleFactor) {
  textLabels.forEach((label, index) => {
    if (!label.x || !label.y) return;
    
    const x = label.x * scaleFactor;
    const z = label.y * scaleFactor; // 2D的Y对应3D的Z
    
    // 创建文字标签
    createTextLabel(label.text, x, baseHeight + 150, z, label.size || 14);
    
    console.log(`创建文字标注 ${index}: ${label.text}`);
  });
}

// 创建文字标签
function createTextLabel(text, x, y, z, size) {
  // 创建画布
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = 512;
  canvas.height = 128;
  
  // 绘制背景
  context.fillStyle = 'rgba(255, 255, 255, 0.8)';
  context.fillRect(0, 0, canvas.width, canvas.height);
  
  // 绘制文字
  context.font = `bold ${Math.max(32, size * 2)}px Arial, sans-serif`;
  context.fillStyle = '#333333';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(text, canvas.width / 2, canvas.height / 2);
  
  // 创建纹理
  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  
  // 创建精灵
  const spriteMaterial = new THREE.SpriteMaterial({ 
    map: texture,
    transparent: true,
    opacity: 0.9
  });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.position.set(x, y, z);
  sprite.scale.set(250, 62.5, 1);
  sprite.userData.type = 'textLabel';
  sprite.userData.text = text;
  
  scene.add(sprite);
  sceneObjects.push(sprite);
}

// 计算轮廓边界框
function calculateBounds(points) {
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;
  
  points.forEach(p => {
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  });
  
  return { minX, maxX, minY, maxY };
}

// 创建门并吸附到墙体
function createDoor(wallIndex, position, config = {}, wallType = 'wall') {
  // 支持普通墙体和办公区墙体
  const wall = sceneObjects.find(obj => obj.userData.type === wallType && obj.userData.wallIndex === wallIndex);
  if (!wall) {
    console.error('未找到指定墙体:', wallIndex, '类型:', wallType);
    return null;
  }

  // 门的默认参数
  const doorWidth = (config.width || 2) * 100; // 米 -> cm，默认2米
  const doorHeight = (config.height || 2.2) * 100; // 米 -> cm，默认2.2米
  const doorColor = config.color || 0x8B4513; // 默认棕色

  // 获取墙体信息
  const wallLength = wall.userData.length;
  const wallHeight = wall.geometry.parameters.height;
  const wallThickness = wall.geometry.parameters.depth;

  // 限制门的位置在墙体范围内
  const maxOffset = (wallLength - doorWidth) / 2;
  const clampedPosition = Math.max(-maxOffset, Math.min(maxOffset, position * 100)); // position为米，转换为cm

  // 创建门框
  const frameGeometry = new THREE.BoxGeometry(doorWidth + 10, doorHeight + 5, wallThickness + 5);
  const frameMaterial = new THREE.MeshStandardMaterial({ color: 0x666666 });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);

  // 创建门板
  const doorGeometry = new THREE.BoxGeometry(doorWidth, doorHeight, wallThickness);
  const doorMaterial = new THREE.MeshStandardMaterial({
    color: doorColor,  // 默认棕色
    roughness: 0.6,
    metalness: 0.1
  });
  const door = new THREE.Mesh(doorGeometry, doorMaterial);

  // 创建门组
  const doorGroup = new THREE.Group();
  doorGroup.add(frame);
  doorGroup.add(door);

  // 计算门在墙体上的位置
  // 墙体中心点
  const wallCenter = wall.position.clone();
  // 墙体方向向量（沿墙体长度方向）
  const wallDirection = new THREE.Vector3(
    Math.cos(-wall.rotation.y),
    0,
    Math.sin(-wall.rotation.y)
  );

  // 门的位置 = 墙体中心 + 沿墙体方向的偏移
  const doorPosition = wallCenter.clone().add(wallDirection.multiplyScalar(clampedPosition));
  // 调整高度：门底部对齐地面
  doorPosition.y = wall.userData.baseHeight + doorHeight / 2;

  doorGroup.position.copy(doorPosition);
  // 门的旋转与墙体一致
  doorGroup.rotation.y = wall.rotation.y;

  // 存储门的信息
  doorGroup.userData = {
    type: 'door',
    wallType: wallType,
    wallIndex: wallIndex,
    position: clampedPosition,
    width: doorWidth,
    height: doorHeight,
    wallDirection: wallDirection.clone()
  };

  scene.add(doorGroup);
  sceneObjects.push(doorGroup);

  // 在墙体上标记开口
  if (!wall.userData.openings) {
    wall.userData.openings = [];
  }
  wall.userData.openings.push({
    type: 'door',
    position: clampedPosition,
    width: doorWidth,
    height: doorHeight,
    object: doorGroup
  });

  console.log('创建门成功:', { wallIndex, position: clampedPosition, width: doorWidth, height: doorHeight });
  return doorGroup;
}

// 创建窗并吸附到墙体
function createWindow(wallIndex, position, config = {}, wallType = 'wall') {
  // 支持普通墙体和办公区墙体
  const wall = sceneObjects.find(obj => obj.userData.type === wallType && obj.userData.wallIndex === wallIndex);
  if (!wall) {
    console.error('未找到指定墙体:', wallIndex, '类型:', wallType);
    return null;
  }

  // 窗的默认参数
  const windowWidth = (config.width || 1.5) * 100; // 米 -> cm，默认1.5米
  const windowHeight = (config.height || 1.2) * 100; // 米 -> cm，默认1.2米
  const windowSillHeight = (config.sillHeight || 1.0) * 100; // 离地高度，默认1米
  const windowColor = config.color || 0x87CEEB; // 默认浅蓝色（玻璃色）

  // 获取墙体信息
  const wallLength = wall.userData.length;
  const wallHeight = wall.geometry.parameters.height;

  // 限制窗的位置在墙体范围内
  const maxOffset = (wallLength - windowWidth) / 2;
  const clampedPosition = Math.max(-maxOffset, Math.min(maxOffset, position * 100));

  // 创建窗框
  const frameThickness = 8;
  const frameGeometry = new THREE.BoxGeometry(windowWidth + frameThickness, windowHeight + frameThickness, 15);
  const frameMaterial = new THREE.MeshStandardMaterial({ color: 0x666666 });
  const frame = new THREE.Mesh(frameGeometry, frameMaterial);

  // 创建玻璃
  const glassGeometry = new THREE.BoxGeometry(windowWidth, windowHeight, 5);
  const glassMaterial = new THREE.MeshStandardMaterial({
    color: windowColor,  // 默认浅蓝色
    transparent: true,
    opacity: 0.6,
    roughness: 0.1,
    metalness: 0.9
  });
  const glass = new THREE.Mesh(glassGeometry, glassMaterial);

  // 创建窗组
  const windowGroup = new THREE.Group();
  windowGroup.add(frame);
  windowGroup.add(glass);

  // 计算窗在墙体上的位置
  const wallCenter = wall.position.clone();
  const wallDirection = new THREE.Vector3(
    Math.cos(-wall.rotation.y),
    0,
    Math.sin(-wall.rotation.y)
  );

  // 窗的位置
  const windowPosition = wallCenter.clone().add(wallDirection.multiplyScalar(clampedPosition));
  // 设置高度：窗台高度 + 窗高/2
  windowPosition.y = wall.userData.baseHeight + windowSillHeight + windowHeight / 2;

  windowGroup.position.copy(windowPosition);
  windowGroup.rotation.y = wall.rotation.y;

  // 存储窗的信息
  windowGroup.userData = {
    type: 'window',
    wallType: wallType,
    wallIndex: wallIndex,
    position: clampedPosition,
    width: windowWidth,
    height: windowHeight,
    sillHeight: windowSillHeight,
    wallDirection: wallDirection.clone()
  };

  scene.add(windowGroup);
  sceneObjects.push(windowGroup);

  // 在墙体上标记开口
  if (!wall.userData.openings) {
    wall.userData.openings = [];
  }
  wall.userData.openings.push({
    type: 'window',
    position: clampedPosition,
    width: windowWidth,
    height: windowHeight,
    sillHeight: windowSillHeight,
    object: windowGroup
  });

  console.log('创建窗成功:', { wallIndex, position: clampedPosition, width: windowWidth, height: windowHeight, sillHeight: windowSillHeight });
  return windowGroup;
}

// 删除门窗
function deleteOpening(openingObject) {
  if (!openingObject || !openingObject.userData) return;

  const wallIndex = openingObject.userData.wallIndex;
  const wallType = openingObject.userData.wallType || 'wall';
  const wall = sceneObjects.find(obj => obj.userData.type === wallType && obj.userData.wallIndex === wallIndex);
  
  if (wall && wall.userData.openings) {
    // 从墙体的开口列表中移除
    wall.userData.openings = wall.userData.openings.filter(o => o.object !== openingObject);
  }

  // 从场景中移除
  scene.remove(openingObject);
  
  // 从场景对象列表中移除
  const index = sceneObjects.indexOf(openingObject);
  if (index > -1) {
    sceneObjects.splice(index, 1);
  }

  console.log('删除开口:', openingObject.userData.type);
}

// 批量放置模式
let isBatchPlaceMode = false;
let batchPlaceCount = 3;
let batchPlaceSpacing = 2;
let batchPlaceDirection = 'horizontal';

function enableBatchPlaceMode(count, spacing, direction) {
  isBatchPlaceMode = true;
  batchPlaceCount = count;
  batchPlaceSpacing = spacing;
  batchPlaceDirection = direction;
  console.log('启用批量放置模式:', { count, spacing, direction });
}

function disableBatchPlaceMode() {
  isBatchPlaceMode = false;
  console.log('禁用批量放置模式');
}

// 移动对象（通过【移动】按钮触发）
function moveObject(enable) {
  isMoving = enable;
  if (enable) {
    console.log('开始移动对象（按钮触发）');
  } else {
    console.log('结束移动对象');
    // 移动结束时恢复对齐线颜色
    restoreAllAlignmentLineColors();
  }
}

// 旋转对象
function startRotate() {
  if (selectedObjects.length === 0) return;
  isRotating = true;
  rotationStartAngle = null;
  rotationStartPositions.clear();
  
  // 保存每个对象的初始旋转
  selectedObjects.forEach(obj => {
    rotationStartPositions.set(obj, {
      rotation: obj.rotation.clone(),
      position: obj.position.clone()
    });
  });
  
  showRotationRing();
  console.log('开始旋转模式');
}

function endRotate() {
  isRotating = false;
  rotationStartAngle = null;
  rotationStartPositions.clear();
  hideRotationRing();
  console.log('结束旋转模式');
}

// 预览旋转角度（实时）
// angle: 旋转角度（弧度），顺时针为正，以白线方向（+Z）为0°基准
function previewRotation(angle) {
  if (selectedObjects.length === 0) return;
  
  const obj = selectedObjects[0];
  // 白线方向为+Z，对应Three.js中Y轴旋转为0
  // 顺时针旋转为正，所以直接使用angle
  obj.rotation.y = angle;
  
  console.log('预览旋转角度:', angle * 180 / Math.PI, '度');
}

// 应用旋转角度
function applyRotation(angle) {
  if (selectedObjects.length === 0) return;
  
  const obj = selectedObjects[0];
  // 应用旋转
  obj.rotation.y = angle;
  
  // 保存旋转角度到对象数据
  if (obj.userData) {
    obj.userData.rotationY = angle;
  }
  
  console.log('应用旋转角度:', angle * 180 / Math.PI, '度');
}

// 清空场景
function clearScene() {
  // 清除选中状态
  clearSelection();

  // 删除所有非墙体对象
  const objectsToRemove = sceneObjects.filter(obj => obj.userData.type !== 'wall' && obj.userData.type !== 'floor');
  objectsToRemove.forEach(obj => {
    scene.remove(obj);
    const index = sceneObjects.indexOf(obj);
    if (index > -1) {
      sceneObjects.splice(index, 1);
    }
  });

  // 清除墙体上的开口
  sceneObjects.filter(obj => obj.userData.type === 'wall').forEach(wall => {
    if (wall.userData.openings) {
      wall.userData.openings = [];
    }
  });

  console.log('场景已清空');
}

// 保存布局
function saveLayout() {
  const layout = {
    version: '1.0',
    timestamp: new Date().toISOString(),
    objects: sceneObjects
      .filter(obj => obj.userData.type && obj.userData.type !== 'floor')
      .map(obj => ({
        type: obj.userData.type,
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
        },
        userData: { ...obj.userData }
      }))
  };
  console.log('布局已保存');
  return layout;
}

// 加载布局
function loadLayout(layout) {
  if (!layout || !layout.objects) return;
  
  // 清空现有对象（保留墙体和地面）
  clearScene();
  
  // 重新创建对象
  layout.objects.forEach(objData => {
    if (objData.type === 'wall' || objData.type === 'floor') return; // 跳过墙体和地面
    
    // 这里简化处理，实际应该根据类型创建对应的对象
    // 目前只支持简单的模型加载
    if (objData.userData && objData.userData.modelType) {
      const newObj = addModelInternal(objData.userData.modelType, objData.position);
      if (newObj) {
        newObj.rotation.set(objData.rotation.x, objData.rotation.y, objData.rotation.z);
        newObj.scale.set(objData.scale.x, objData.scale.y, objData.scale.z);
      }
    }
  });
  
  console.log('布局已加载');
}

// 批量复制预览变量已在第37行定义
// let batchPreviewObjects = [];
// let isBatchPreviewMode = false;
// let batchPreviewConfig = null;

function startBatchPreview(config) {
  if (selectedObjects.length === 0) return;

  // 先清除之前的预览（不重置isBatchPreviewMode）
  // 注意：cancelBatchPreview会设置isBatchPreviewMode = false，所以我们需要在之后重新设置
  const objectsToRemove = batchPreviewObjects.filter(obj => obj.userData.isPreview);
  objectsToRemove.forEach(obj => scene.remove(obj));
  batchPreviewObjects = batchPreviewObjects.filter(obj => !obj.userData.isPreview);

  isBatchPreviewMode = true;
  batchPreviewConfig = config;
  const originalObj = selectedObjects[0];
  
  // 第一步：先收集原始材质（在任何修改之前）
  const originalMaterials = new Map();
  originalObj.traverse((child) => {
    if (child.isMesh && child.material) {
      // 保存原始材质的克隆，避免引用问题
      if (Array.isArray(child.material)) {
        originalMaterials.set(child.uuid, child.material.map(m => m.clone()));
      } else {
        originalMaterials.set(child.uuid, child.material.clone());
      }
    }
  });
  
  // 第二步：清除原始对象的选中高亮
  originalObj.traverse((child) => {
    if (child.isMesh && child.material) {
      if (child.material.emissive) {
        child.material.emissive.setHex(0x000000);
      }
    }
  });
  
  // 创建预览对象（半透明）
  const { rows, cols, rowSpacing, colSpacing, rotation } = config;
  
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (r === 0 && c === 0) continue; // 跳过原始对象位置
      
      const previewObj = originalObj.clone();
      previewObj.traverse((child) => {
        if (child.isMesh && child.material) {
          // 使用原始材质克隆
          const origMat = originalMaterials.get(child.uuid) || child.material;
          if (origMat && typeof origMat.clone === 'function') {
            child.material = origMat.clone();
          }
          child.material.transparent = true;
          child.material.opacity = 0.5;
        }
      });
      
      // 计算方向向量（基于原始对象的旋转角度）
      const objRotation = originalObj.rotation.y;
      const { rowDirection = 'forward', colDirection = 'left' } = config;
      
      // 获取方向向量（考虑对象当前旋转）
      const rowDirVector = getDirectionVector(rowDirection, objRotation);
      const colDirVector = getDirectionVector(colDirection, objRotation);
      
      // 计算位置偏移（使用本地尺寸，不受旋转影响）
      // 行方向（前后）使用本地深度（Z尺寸），列方向（左右）使用本地宽度（X尺寸）
      const rowOffset = r * (getObjectLocalDepth(originalObj) + rowSpacing * 100);
      const colOffset = c * (getObjectLocalWidth(originalObj) + colSpacing * 100);
      
      // 应用方向向量计算实际偏移
      const offsetX = colOffset * colDirVector.x + rowOffset * rowDirVector.x;
      const offsetZ = colOffset * colDirVector.z + rowOffset * rowDirVector.z;
      
      previewObj.position.x = originalObj.position.x + offsetX;
      previewObj.position.z = originalObj.position.z + offsetZ;
      previewObj.position.y = originalObj.position.y;
      
      // 应用旋转（保持与原始对象相同朝向）
      previewObj.rotation.y = originalObj.rotation.y;
      
      previewObj.userData.isPreview = true;
      scene.add(previewObj);
      batchPreviewObjects.push(previewObj);
    }
  }
  
  console.log('批量复制预览:', rows, '行', cols, '列', '共', batchPreviewObjects.length, '个预览对象');
}

// 获取对象宽度（世界坐标系）
function getObjectWidth(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  return box.max.x - box.min.x;
}

// 获取对象深度（世界坐标系）
function getObjectDepth(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  return box.max.z - box.min.z;
}

// 获取对象本地宽度（不考虑旋转，获取模型本身的X尺寸）
function getObjectLocalWidth(obj) {
  // 克隆对象并清除旋转，测量本地尺寸
  const clonedObj = obj.clone();
  clonedObj.rotation.set(0, 0, 0);
  const box = new THREE.Box3().setFromObject(clonedObj);
  return box.max.x - box.min.x;
}

// 获取对象本地深度（不考虑旋转，获取模型本身的Z尺寸）
function getObjectLocalDepth(obj) {
  // 克隆对象并清除旋转，测量本地尺寸
  const clonedObj = obj.clone();
  clonedObj.rotation.set(0, 0, 0);
  const box = new THREE.Box3().setFromObject(clonedObj);
  return box.max.z - box.min.z;
}

// 根据方向和对象旋转计算方向向量
// direction: 'forward' | 'backward' | 'left' | 'right'
// objRotation: 对象的Y轴旋转角度（弧度）
// 返回: { x, z } 单位方向向量
function getDirectionVector(direction, objRotation) {
  // 基础方向向量（对象朝向+Z方向时的方向）
  let baseVector;
  switch (direction) {
    case 'forward':
      baseVector = { x: 0, z: 1 };  // +Z方向
      break;
    case 'backward':
      baseVector = { x: 0, z: -1 }; // -Z方向
      break;
    case 'left':
      baseVector = { x: -1, z: 0 }; // -X方向
      break;
    case 'right':
      baseVector = { x: 1, z: 0 };  // +X方向
      break;
    default:
      baseVector = { x: 0, z: 1 };
  }
  
  // 应用对象旋转（逆时针旋转坐标系）
  const cos = Math.cos(objRotation);
  const sin = Math.sin(objRotation);
  
  return {
    x: baseVector.x * cos - baseVector.z * sin,
    z: baseVector.x * sin + baseVector.z * cos
  };
}

function confirmBatchPlace() {
  console.log('confirmBatchPlace: 进入函数, isBatchPreviewMode:', isBatchPreviewMode, 'batchPreviewObjects数量:', batchPreviewObjects.length);
  if (!isBatchPreviewMode || batchPreviewObjects.length === 0) {
    console.log('confirmBatchPlace: 提前返回, 条件不满足');
    return;
  }

  // 将预览对象转为正式对象
  batchPreviewObjects.forEach(obj => {
    obj.traverse((child) => {
      if (child.isMesh && child.material) {
        // 从预览材质恢复：复制属性但移除透明效果
        const currentMaterial = child.material;
        if (Array.isArray(currentMaterial)) {
          // 处理材质数组
          child.material = currentMaterial.map(m => {
            const newMat = m.clone();
            newMat.transparent = false;
            newMat.opacity = 1;
            return newMat;
          });
        } else {
          // 单一材质
          child.material = currentMaterial.clone();
          child.material.transparent = false;
          child.material.opacity = 1;
        }
      }
    });
    obj.userData.isPreview = false;
    sceneObjects.push(obj);
  });

  console.log('批量复制完成:', batchPreviewObjects.length, '个对象');

  // 强制渲染刷新以确保材质更新
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }

  // 清理预览状态
  batchPreviewObjects = [];
  isBatchPreviewMode = false;
  batchPreviewConfig = null;

  // 取消原始对象的选中状态
  console.log('confirmBatchPlace: 清除选中状态前, selectedObjects数量:', selectedObjects.length);
  clearSelection();
  console.log('confirmBatchPlace: 清除选中状态后, selectedObjects数量:', selectedObjects.length);
}

function cancelBatchPreview() {
  // 删除所有预览对象
  batchPreviewObjects.forEach(obj => {
    scene.remove(obj);
  });
  batchPreviewObjects = [];
  isBatchPreviewMode = false;
  batchPreviewConfig = null;
  console.log('取消批量复制预览');
}

// 对齐工具
function alignObjects(alignType) {
  if (selectedObjects.length < 2) {
    console.log('对齐需要至少2个对象');
    return;
  }
  
  // 以第一个对象为基准
  const baseObj = selectedObjects[0];
  const baseBox = new THREE.Box3().setFromObject(baseObj);
  
  selectedObjects.slice(1).forEach(obj => {
    const objBox = new THREE.Box3().setFromObject(obj);
    
    switch (alignType) {
      case 'left':
        obj.position.x = baseObj.position.x - (baseBox.max.x - baseBox.min.x) / 2 + (objBox.max.x - objBox.min.x) / 2;
        break;
      case 'right':
        obj.position.x = baseObj.position.x + (baseBox.max.x - baseBox.min.x) / 2 - (objBox.max.x - objBox.min.x) / 2;
        break;
      case 'center':
        obj.position.x = baseObj.position.x;
        break;
    }
  });
  
  console.log('对齐完成:', alignType);
}

// 等距分布
function distributeObjects(distributeType) {
  if (selectedObjects.length < 3) {
    console.log('等距分布需要至少3个对象');
    return;
  }
  
  // 按位置排序
  const sorted = [...selectedObjects].sort((a, b) => {
    return distributeType === 'horizontal' ? a.position.x - b.position.x : a.position.z - b.position.z;
  });
  
  const first = sorted[0];
  const last = sorted[sorted.length - 1];
  
  if (distributeType === 'horizontal') {
    const totalWidth = last.position.x - first.position.x;
    const step = totalWidth / (sorted.length - 1);
    sorted.forEach((obj, index) => {
      obj.position.x = first.position.x + step * index;
    });
  } else {
    const totalDepth = last.position.z - first.position.z;
    const step = totalDepth / (sorted.length - 1);
    sorted.forEach((obj, index) => {
      obj.position.z = first.position.z + step * index;
    });
  }
  
  console.log('等距分布完成:', distributeType);
}

// 3D视图控制方法
function zoomIn() {
  if (camera && controls) {
    // 向前移动相机（放大）
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    camera.position.add(direction.multiplyScalar(50));
    controls.update();
    console.log('3D放大');
  }
}

function zoomOut() {
  if (camera && controls) {
    // 向后移动相机（缩小）
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    camera.position.sub(direction.multiplyScalar(50));
    controls.update();
    console.log('3D缩小');
  }
}

function resetView() {
  if (camera && controls) {
    if (warehouseConfig) {
      // 使用仓库配置中的实际中心位置
      const centerX = warehouseConfig.centerX || 0;
      const centerZ = warehouseConfig.centerZ || 0;
      const baseHeight = warehouseConfig.baseHeight || 0;
      const height = warehouseConfig.height || 500;

      // 计算合适的相机距离
      const maxDimension = Math.max(warehouseConfig.length || 2000, warehouseConfig.width || 2000);
      const distance = maxDimension * 0.8;

      camera.position.set(centerX + distance, baseHeight + height / 2 + distance * 0.5, centerZ + distance);
      camera.lookAt(centerX, baseHeight + height / 2, centerZ);
      controls.target.set(centerX, baseHeight + height / 2, centerZ);
      console.log('3D视图重置到仓库中心:', centerX, centerZ);
    } else {
      // 没有仓库时，重置到默认位置
      camera.position.set(500, 400, 500);
      camera.lookAt(0, 0, 0);
      controls.target.set(0, 0, 0);
      console.log('3D视图重置到默认位置');
    }
    controls.update();
  }
}

// 暴露方法
  defineExpose({
    // 暴露获取相机的方法
    getCamera: () => camera,
    // 暴露控制器
    getControls: () => controls,
    createWarehouse,
    createWarehouseFromShape,
    createDoor,
    createWindow,
    createPillar,
    updatePillarHeight,
    deleteOpening,
    addModel,
    addModelInternal,
    getSceneObjects,
    getSelectedObjectsCount,
    getObjectsCount,
    getSelectedObjects,
    syncSelectedObjects,
    updateShelf,
    updateConveyor,
    startDrawZone,
    cancelDrawZone,
    clearAllZones,
    deleteZone,
    exportImage,
    enableBatchPlaceMode,
    disableBatchPlaceMode,
    moveObject,
    startRotate,
    endRotate,
    previewRotation,
    applyRotation,
    deleteSelectedObjects,
    copySelectedObject,
    startBatchPreview,
    confirmBatchPlace,
    cancelBatchPreview,
    alignObjects,
    distributeObjects,
    clearScene,
    saveLayout,
    loadLayout,
    zoomIn,
    zoomOut,
    resetView,
    forceRender,
    handleResize, // 暴露resize方法供父组件调用
    // 对齐线相关方法
    getAlignmentLines: serializeAlignmentLines,
    setAlignmentLines: deserializeAlignmentLines,
    addAlignmentLine,
    removeAlignmentLine,
    updateAlignmentLine,
    getAlignmentLine,
    getAllAlignmentLines,
    clearAlignmentLines,
    // 对齐线绘制相关方法
    startDrawingAlignmentLine,
    stopDrawingAlignmentLine,
    cancelDrawingAlignmentLine,
    // 测量工具相关方法
    startMeasuring,
    stopMeasuring,
    cancelMeasuring,
    // 对象边界计算相关方法
    getObjectBounds,
    getObjectEdges,
    // 参考线生成相关方法
    generateReferenceLines,
    filterReferenceLines,
    // 对齐线高亮方法
    highlightAlignmentLine,
    // 子任务5.1: 距离计算与吸附逻辑相关方法
    calculateDistance,
    calculateDistanceToInfiniteLine,
    findClosestAlignmentLine,
    applySnap,
    getSnapState,
    setSnapConfig,
    getSnapConfig,
    // 子任务5.2: 吸附优先级与边界处理相关方法
    calculateSnapPriority,
    updateUserIntent,
    resetUserIntent,
    handleBoundarySnap,
    cancelSnap,
    isSnapDisabled,
    enableSnap,
    // 子任务5.3: 对齐辅助提示相关方法
    createSnapIndicator,
    updateSnapIndicator,
    hideSnapIndicator,
    destroySnapIndicator,
    // 外墙标语相关方法
    createWallSign,
    updateWallSign,
    moveWallSign,
    // 获取墙体方法（用于导入时查找墙体）
    getWallByIndex: (index) => sceneObjects.find(obj => obj.userData.type === 'wall' && obj.userData.wallIndex === index),
    // 距离线相关方法
    startDistanceLineMode,
    stopDistanceLineMode,
    setDistanceLineValue,
    clearAllDistanceLines
  });
</script>

<style scoped>
.three-container {
  width: 100%;
  height: 100%;
  background: #f0f0e6;
  /* 使用亮紫色自定义十字光标，确保在各种背景下都可见 */
  cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath stroke='%23E040FB' stroke-width='2' d='M12 0v24M0 12h24'/%3E%3Ccircle cx='12' cy='12' r='2' fill='%23E040FB'/%3E%3C/svg%3E") 12 12, crosshair;
}
</style>