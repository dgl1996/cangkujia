<template>
  <div ref="container" class="three-container" tabindex="0"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
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
  }
});

const emit = defineEmits(['model-added', 'object-selected', 'object-deselected', 'zone-selected', 'save-project', 'add-door', 'add-window']);

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
    container.value.removeEventListener('mousemove', onMouseMove);
    container.value.removeEventListener('mouseup', onMouseUp);
    container.value.removeEventListener('dragover', onDragOver);
    container.value.removeEventListener('drop', onDrop);
  }
});

function handleResize() {
  if (camera && renderer && container.value) {
    camera.aspect = container.value.clientWidth / container.value.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  }
}

// 模型文件名映射（对象ID -> GLB文件名）
const modelFileMap = {
  // 货架系统
  'shelf-beam-heavy': 'shelf-beam-heavy.glb',
  'shelf-beam-medium': 'shelf-beam-medium.glb',
  'shelf-drive-in': 'shelf-drive-in.glb',
  'shelf-flow-4level': 'shelf-flow-4level.glb',
  'shelf-light-v2': 'shelf-light-v2.glb',
  'shelf-beam-heavy-3level': 'shelf-beam-heavy-3level.glb',
  'shelf-beam-heavy-4level': 'shelf-beam-heavy-4level.glb',
  'shelf-beam-heavy-5level': 'shelf-beam-heavy-5level.glb',
  'shelf-beam-medium-4level-2m': 'shelf-beam-medium-4level-2m.glb',
  'shelf-beam-medium-5level-2m': 'shelf-beam-medium-5level-2m.glb',
  'shelf-beam-light-4level-2m': 'shelf-beam-light-4level.glb',
  'shelf-beam-light-5level-2m': 'shelf-beam-light-5level.glb',
  // 载具容器
  'pallet-wooden-1200': 'pallet-wooden-1200.glb',
  'pallet-plastic-1200': 'pallet-plastic-1200.glb',
  'pallet-wood-1200x1000': 'pallet-wood-1200x1000.glb',
  'pallet-plastic-1200x1000': 'pallet-plastic-1200x1000.glb',
  'container-foldable': 'container-foldable.glb',
  'container-tote-600x400x300': 'container-tote-600x400.glb',
  'container-tote-600x400x220': 'container-tote-600x400-low.glb',
  'container-tote-400x300x150': 'container-tote-400x300.glb',
  // 搬运设备
  'forklift-reach-2t': 'forklift-reach-2t.glb',
  'forklift-counterbalance-2.5t': 'forklift-counterbalance-2.5t.glb',
  'forklift-pallet-truck-electric': 'forklift-pallet-truck-electric.glb',
  'forklift-pallet-jack-manual': 'forklift-pallet-jack-manual.glb',
  'cart-picking-3tier': 'cart-picking-3tier.glb',
  'cart-cage-logistics-2tier': 'cart-cage-logistics-2tier.glb',
  // 输送设备
  'lift-cargo-hydraulic-3floor': 'lift-cargo-hydraulic-3floor.glb',
  'conveyor-curve-90degree-600': 'conveyor-curve-90degree-600.glb',
  'conveyor-roller-straight-600-red': 'conveyor-roller-straight-600-red.glb',
  // 拣选设备
  'putwall-standard-16cell': 'putwall-standard-16cell.glb',
  'station-packcheck-integrated-red': 'station-packcheck-integrated-red.glb',
  'weigher-automatic-check-600-red': 'weigher-automatic-check-600-red.glb',
  // 其他设备
  'guard-rack-heavy-redyellow': 'guard-rack-heavy-redyellow.glb',
  'guard-column-protector-redyellow': 'guard-column-protector-redyellow.glb',
  // 人员
  'person-warehouse-admin-red': 'person-warehouse-admin-red.glb',
  // 默认模型
  'shelf': '../shelf_with_pallet.glb'
};

// 加载所有模型
function loadAllModels() {
  loader = new GLTFLoader();
  
  Object.entries(modelFileMap).forEach(([modelId, fileName]) => {
    loadModel(modelId, fileName);
  });
}

function loadModel(modelId, fileName) {
  if (models[modelId]) {
    return models[modelId];
  }

  loader.load(
    `/assets/models/${fileName}`,
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
      
      // 计算模型的边界框
      const box = new THREE.Box3().setFromObject(model);
      
      // 调整模型位置，使底部与地面平齐（Y=0）
      const offsetY = -box.min.y;
      model.position.y = offsetY;
      
      // 缩放模型（GLB导出时使用mm单位，Three.js使用cm单位，需要缩小10倍）
      model.scale.set(0.1, 0.1, 0.1);
      
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

  console.log('方向标识已创建，范围:', axisLength, 'cm');
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
  console.log('方向标识已更新到仓库中心:', { x: centerX, z: centerZ });
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
  
  // Esc取消选择
  if (event.key === 'Escape') {
    clearSelection();
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
  
  if (isMoving && selectedObjects.length > 0) {
    if (raycaster.ray.intersectPlane(movePlane, moveIntersectPoint)) {
      moveSelectedObjects(moveIntersectPoint.sub(moveOffset));
    }
    return;
  }
  
  const intersects = raycaster.intersectObjects(sceneObjects, true);
  
  console.log('点击检测:', intersects.length, '个对象', 'sceneObjects数量:', sceneObjects.length);
  
  if (intersects.length > 0) {
    const closestObject = intersects[0].object;
    console.log('最近对象:', closestObject.uuid, '类型:', closestObject.userData.type || '未知');
    let rootObject = closestObject;
    while (rootObject.parent && rootObject.parent !== scene) {
      rootObject = rootObject.parent;
    }
    
    console.log('根对象:', rootObject.uuid, '类型:', rootObject.userData.type || '未知');
    
    if (event.ctrlKey || event.metaKey) {
      toggleObjectSelection(rootObject);
    } else {
      clearSelection();
      selectObject(rootObject);
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
  
  selectedObject = obj;
  selectedObjects.push(obj);
  
  obj.traverse((child) => {
    if (child.material && child.material.emissive) {
      child.material.emissive.setHex(0x4fc3f7);
      child.material.emissiveIntensity = 0.3;
    }
  });
  
  // 构建选中对象的信息
  const objectInfo = {
    uuid: obj.uuid,
    name: obj.userData.name || obj.userData.modelType || obj.userData.type || '未命名对象',
    type: obj.userData.type || obj.userData.modelType || 'unknown',
    position: obj.position,
    rotation: obj.rotation.y,
    dimensions: obj.userData.dimensions || calculateObjectDimensions(obj)
  };
  
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
  selectedObjects.forEach(obj => {
    obj.position.add(delta);
  });
  updateCornerMarkers();
}

function onMouseMove(event) {
  const rect = container.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  
  // 移动模式
  if (isMoving && selectedObjects.length > 0) {
    if (raycaster.ray.intersectPlane(movePlane, moveIntersectPoint)) {
      const targetPosition = moveIntersectPoint.sub(moveOffset);
      targetPosition.x = Math.round(targetPosition.x * 10) / 10;
      targetPosition.z = Math.round(targetPosition.z * 10) / 10;
      
      const firstObj = selectedObjects[0];
      const deltaX = targetPosition.x - firstObj.position.x;
      const deltaZ = targetPosition.z - firstObj.position.z;
      
      selectedObjects.forEach(obj => {
        obj.position.x += deltaX;
        obj.position.z += deltaZ;
      });
    }
    updateCornerMarkers();
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

function onMouseUp() {
  if (isMoving) {
    isMoving = false;
    container.value.style.cursor = '';
    console.log('移动完成');
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
  if (objectType === 'door' || objectType === 'window') {
    // 检测墙体
    raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
    const wallIntersects = raycaster.intersectObjects(
      sceneObjects.filter(obj => obj.userData.type === 'wall'),
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
      
      if (objectType === 'door') {
        const width = parseFloat(event.dataTransfer.getData('doorWidth')) || 2;
        const height = parseFloat(event.dataTransfer.getData('doorHeight')) || 2.2;
        createDoor(wallIndex, position, { width, height });
      } else if (objectType === 'window') {
        const width = parseFloat(event.dataTransfer.getData('windowWidth')) || 1.5;
        const height = parseFloat(event.dataTransfer.getData('windowHeight')) || 1.2;
        const sillHeight = parseFloat(event.dataTransfer.getData('windowSillHeight')) || 1.0;
        createWindow(wallIndex, position, { width, height, sillHeight });
      }
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
    
    // 检查模型是否存在，如果不存在则创建占位对象
    let newModel;
    if (models[modelName]) {
      // 使用已加载的模型
      newModel = addModelInternal(modelName, {
        x: intersectPoint.x,
        y: yPosition,
        z: intersectPoint.z
      });
    } else {
      // 创建占位对象（彩色方块）
      newModel = createPlaceholderObject(modelName, {
        x: intersectPoint.x,
        y: yPosition,
        z: intersectPoint.z
      });
    }
    
    if (newModel) {
      console.log('模型放置到位置:', intersectPoint, '名称:', modelName);
    }
  }
}

// 内部使用的添加模型方法
function addModelInternal(modelName, position = null) {
  if (models[modelName]) {
    const newModel = models[modelName].clone();
    
    newModel.traverse((child) => {
      if (child.material) {
        child.material = child.material.clone();
      }
    });
    
    // 记录对象类型
    newModel.userData.modelType = modelName;
    newModel.userData.modelId = 'shelf_001';
    
    // 设置位置，考虑仓库基准高度
    let yPosition = 0;
    if (warehouseConfig) {
      yPosition = warehouseConfig.baseHeight;
    }
    
    if (position) {
      newModel.position.set(position.x, yPosition, position.z);
    } else {
      newModel.position.set(0, yPosition, 0);
    }
    
    scene.add(newModel);
    sceneObjects.push(newModel);
    
    console.log('模型添加到场景:', newModel.uuid, '类型:', modelName, 'sceneObjects数量:', sceneObjects.length);
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
  
  // 获取对象参数
  let params = objectLibraryParams[modelName];
  if (!params) {
    // 尝试匹配短ID（如A101）
    const shortIdMatch = modelName.match(/(A|B|C|D|E|F|G)\d{3}/);
    if (shortIdMatch) {
      const shortId = shortIdMatch[0];
      params = Object.values(objectLibraryParams).find(p => p.shortId === shortId);
    }
  }
  
  // 如果还是没有找到，使用默认参数
  if (!params) {
    params = { length: 1000, width: 1000, height: 1000, type: 'default', color: 0x888888 };
  }
  
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
  
  // 存储对象信息
  group.userData = {
    type: 'model',
    modelType: modelName,
    modelId: modelName,
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
  const frameMaterial = new THREE.MeshStandardMaterial({ color: color, roughness: 0.5, metalness: 0.4 });
  const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.8, metalness: 0.2 });
  
  // 层板
  const levels = 3;
  for (let i = 0; i < levels; i++) {
    const y = (i + 1) * height / (levels + 1);
    const deckGeo = new THREE.BoxGeometry(length, 2, width);
    const deck = new THREE.Mesh(deckGeo, frameMaterial);
    deck.position.y = y;
    group.add(deck);
  }
  
  // 立柱
  const postGeo = new THREE.BoxGeometry(3, height, 3);
  const postPositions = [
    { x: -length/2 + 5, z: -width/2 + 5 },
    { x: length/2 - 5, z: -width/2 + 5 },
    { x: -length/2 + 5, z: width/2 - 5 },
    { x: length/2 - 5, z: width/2 - 5 }
  ];
  postPositions.forEach(pos => {
    const post = new THREE.Mesh(postGeo, frameMaterial);
    post.position.set(pos.x, height/2, pos.z);
    group.add(post);
  });
  
  // 轮子
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
  // 首先尝试使用预加载的GLB模型
  if (models[modelName]) {
    const newModel = models[modelName].clone();
    
    newModel.traverse((child) => {
      if (child.material) {
        child.material = child.material.clone();
      }
    });
    
    // 记录对象信息
    newModel.userData.modelType = modelName;
    newModel.userData.modelId = modelName;
    newModel.userData.isGLBModel = true;
    
    // 设置位置
    let yPosition = 0;
    if (warehouseConfig) {
      yPosition = warehouseConfig.baseHeight;
    }
    
    newModel.position.set(position.x, yPosition, position.z);
    
    scene.add(newModel);
    sceneObjects.push(newModel);
    
    console.log('GLB模型添加到场景:', modelName, 'sceneObjects数量:', sceneObjects.length);
    emit('model-added', newModel);
    
    return newModel;
  }
  
  // 如果没有GLB模型，使用详细几何体生成
  console.log('GLB模型未加载，使用详细几何体:', modelName);
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
  console.log('清空所有区域');
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
    
    console.log('删除区域完成:', zoneId, '同时删除', labelsToRemove.length, '个名称标签');
  } else {
    console.warn('未找到功能区:', zoneId);
  }
}

// 获取场景对象
function getSceneObjects() {
  return sceneObjects.filter(obj => obj.userData.modelType || obj.userData.type);
}

// 获取选中对象数量
function getSelectedObjectsCount() {
  return selectedObjects.length;
}

// 获取场景对象数量
function getObjectsCount() {
  return sceneObjects.filter(obj => obj.userData.modelType || obj.userData.type === 'door' || obj.userData.type === 'window').length;
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
  addModelInternal(modelName, defaultPosition);
  emit('model-added', modelName);
  console.log('添加模型:', modelName);
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
  const gridSize = Math.max(length, width);
  const gridDivisions = Math.floor(gridSize / 10); // 每10cm一个网格
  const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, 0x888888, 0xcccccc);
  gridHelper.position.y = baseHeight;
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

  // 网格尺寸应该与仓库尺寸匹配（cm单位）
  const updateGridSize = Math.max(length, width);
  const newGridHelper = new THREE.GridHelper(updateGridSize, 20, 0xaaaaaa, 0xdddddd);
  newGridHelper.name = 'gridHelper';
  newGridHelper.position.y = baseHeight;
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

  // 创建网格地面（根据轮廓的边界框）
  const gridSize = Math.max(boundsWidth, boundsDepth);
  const gridDivisions = Math.floor(gridSize / 10); // 每10cm一个网格
  const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, 0x888888, 0xcccccc);
  gridHelper.position.y = baseHeight;
  gridHelper.position.x = centerX;
  gridHelper.position.z = centerZ;
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
    
    // 存储墙体信息
    wallMesh.userData.type = 'wall';
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

  // 网格尺寸应该与仓库尺寸匹配（已经是cm单位，不需要再除以100）
  const maxDimension = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY);
  const updateGridSize2 = maxDimension * scaleFactor;
  const newGridHelper = new THREE.GridHelper(updateGridSize2, 20, 0xaaaaaa, 0xdddddd);
  newGridHelper.name = 'gridHelper';
  newGridHelper.position.y = baseHeight;
  newGridHelper.position.x = (bounds.minX + bounds.maxX) / 2 * scaleFactor;
  newGridHelper.position.z = (bounds.minY + bounds.maxY) / 2 * scaleFactor;
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

// 在3D场景中创建功能区域
function createZonesIn3D(zonesData, baseHeight, scaleFactor) {
  // 清空现有的zones数组并重新填充
  zones = [];
  
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
    
    console.log(`创建功能区 ${index}: ${zone.name}, 尺寸: ${(width/100).toFixed(1)}m x ${(depth/100).toFixed(1)}m, 字体: ${fontSize}px`);
  });
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
function createDoor(wallIndex, position, config = {}) {
  const wall = sceneObjects.find(obj => obj.userData.type === 'wall' && obj.userData.wallIndex === wallIndex);
  if (!wall) {
    console.error('未找到指定墙体:', wallIndex);
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
    color: doorColor,
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
function createWindow(wallIndex, position, config = {}) {
  const wall = sceneObjects.find(obj => obj.userData.type === 'wall' && obj.userData.wallIndex === wallIndex);
  if (!wall) {
    console.error('未找到指定墙体:', wallIndex);
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
    color: windowColor,
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
  const wall = sceneObjects.find(obj => obj.userData.type === 'wall' && obj.userData.wallIndex === wallIndex);
  
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

// 移动对象
function moveObject(enable) {
  isMoving = enable;
  if (enable && selectedObjects.length > 0) {
    // 创建移动平面
    const firstObj = selectedObjects[0];
    movePlane.setFromNormalAndCoplanarPoint(
      new THREE.Vector3(0, 1, 0),
      firstObj.position
    );
    console.log('开始移动对象');
  } else {
    console.log('结束移动对象');
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
      
      // 计算位置偏移
      const offsetX = c * (getObjectWidth(originalObj) + colSpacing * 100); // cm
      const offsetZ = r * (getObjectDepth(originalObj) + rowSpacing * 100); // cm
      
      previewObj.position.x = originalObj.position.x + offsetX;
      previewObj.position.z = originalObj.position.z + offsetZ;
      previewObj.position.y = originalObj.position.y;
      
      // 应用旋转
      if (rotation) {
        previewObj.rotation.y = originalObj.rotation.y + (rotation * Math.PI / 180);
      }
      
      previewObj.userData.isPreview = true;
      scene.add(previewObj);
      batchPreviewObjects.push(previewObj);
    }
  }
  
  console.log('批量复制预览:', rows, '行', cols, '列', '共', batchPreviewObjects.length, '个预览对象');
}

// 获取对象宽度
function getObjectWidth(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  return box.max.x - box.min.x;
}

// 获取对象深度
function getObjectDepth(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  return box.max.z - box.min.z;
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
  createWarehouse,
  createWarehouseFromShape,
  createDoor,
  createWindow,
  deleteOpening,
  addModel,
  addModelInternal,
  getSceneObjects,
  getSelectedObjectsCount,
  getObjectsCount,
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
  handleResize // 暴露resize方法供父组件调用
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