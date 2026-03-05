<template>
  <div ref="container" class="three-container" tabindex="0"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const container = ref(null);
const emit = defineEmits(['model-added', 'object-selected', 'object-deselected', 'save-project']);

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
let rotationStartAngle = 0;
let rotationStartPositions = new Map();

onMounted(() => {
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0e6);

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    35,
    container.value.clientWidth / container.value.clientHeight,
    0.1,
    1000
  );
  camera.position.set(10, 8, 10);

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

  // 添加网格辅助线
  const gridHelper = new THREE.GridHelper(20, 20, 0xaaaaaa, 0xdddddd);
  scene.add(gridHelper);

  // 添加方向标识
  createDirectionLabels();

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

  // 加载模型
  loadModel('shelf_with_pallet.glb');

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

function loadModel(modelName) {
  if (models[modelName]) {
    return models[modelName];
  }

  loader = new GLTFLoader();
  loader.load(
    `/assets/${modelName}`,
    (gltf) => {
      const model = gltf.scene;
      
      // 旋转模型使其站立
      model.rotation.x = -Math.PI / 2;
      
      // 计算模型的边界框
      const box = new THREE.Box3().setFromObject(model);
      
      // 调整模型位置，使底部与地面平齐（Y=0）
      const offsetY = -box.min.y;
      model.position.y = offsetY;
      
      models[modelName] = model;
      console.log('模型加载成功:', modelName);
    },
    (xhr) => {
      console.log((xhr.loaded / xhr.total * 100) + '% loaded');
    },
    (error) => {
      console.error('模型加载失败:', error);
    }
  );
}

function createDirectionLabels() {
  // 创建箭头几何体
  const arrowShape = new THREE.Shape();
  arrowShape.moveTo(0, 0.3);
  arrowShape.lineTo(0.2, 0);
  arrowShape.lineTo(0.1, 0);
  arrowShape.lineTo(0.1, -0.3);
  arrowShape.lineTo(-0.1, -0.3);
  arrowShape.lineTo(-0.1, 0);
  arrowShape.lineTo(-0.2, 0);
  arrowShape.lineTo(0, 0.3);

  const arrowGeometry = new THREE.ShapeGeometry(arrowShape);

  // X轴方向箭头（红色）
  const xPosArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff0000 }));
  xPosArrow.position.set(10, 0.1, 0);
  xPosArrow.rotation.x = -Math.PI / 2;
  xPosArrow.rotation.z = -Math.PI / 2;
  scene.add(xPosArrow);

  const xNegArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0xff0000 }));
  xNegArrow.position.set(-10, 0.1, 0);
  xNegArrow.rotation.x = -Math.PI / 2;
  xNegArrow.rotation.z = Math.PI / 2;
  scene.add(xNegArrow);

  // Z轴方向箭头（蓝色）
  const zPosArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x0000ff }));
  zPosArrow.position.set(0, 0.1, 10);
  zPosArrow.rotation.x = -Math.PI / 2;
  zPosArrow.rotation.z = Math.PI;
  scene.add(zPosArrow);

  const zNegArrow = new THREE.Mesh(arrowGeometry, new THREE.MeshBasicMaterial({ color: 0x0000ff }));
  zNegArrow.position.set(0, 0.1, -10);
  zNegArrow.rotation.x = -Math.PI / 2;
  scene.add(zNegArrow);

  // 添加字母标识
  const labels = [
    { text: 'X', pos: [10.5, 0.5, 0], color: '#ff0000' },
    { text: '-X', pos: [-10.5, 0.5, 0], color: '#ff0000' },
    { text: 'Z', pos: [0, 0.5, 10.5], color: '#0000ff' },
    { text: '-Z', pos: [0, 0.5, -10.5], color: '#0000ff' }
  ];

  labels.forEach(label => {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 64;
    canvas.height = 64;

    context.fillStyle = 'rgba(255, 255, 255, 0)';
    context.fillRect(0, 0, 64, 64);

    context.font = 'bold 48px Arial';
    context.fillStyle = label.color;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(label.text, 32, 32);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(...label.pos);
    sprite.scale.set(1, 1, 1);

    scene.add(sprite);
  });

  console.log('方向标识已创建');
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
        if (child.material) {
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

function onClick(event) {
  const rect = container.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  
  if (isMoving && selectedObjects.length > 0) {
    if (raycaster.ray.intersectPlane(movePlane, moveIntersectPoint)) {
      moveSelectedObjects(moveIntersectPoint.sub(moveOffset));
    }
    return;
  }
  
  const intersects = raycaster.intersectObjects(sceneObjects, true);
  
  if (intersects.length > 0) {
    const closestObject = intersects[0].object;
    let rootObject = closestObject;
    while (rootObject.parent && rootObject.parent !== scene) {
      rootObject = rootObject.parent;
    }
    
    if (event.ctrlKey || event.metaKey) {
      toggleObjectSelection(rootObject);
    } else {
      clearSelection();
      selectObject(rootObject);
    }
  } else {
    if (!event.ctrlKey && !event.metaKey) {
      clearSelection();
    }
  }
}

function selectObject(obj) {
  selectedObject = obj;
  selectedObjects.push(obj);
  
  obj.traverse((child) => {
    if (child.material) {
      child.material.emissive.setHex(0x4fc3f7);
      child.material.emissiveIntensity = 0.3;
    }
  });
  
  emit('object-selected', obj);
  updateCornerMarkers();
}

function toggleObjectSelection(obj) {
  const index = selectedObjects.indexOf(obj);
  if (index > -1) {
    selectedObjects.splice(index, 1);
    obj.traverse((child) => {
      if (child.material) {
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
      if (child.material) {
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
          
          // 绕Y轴旋转
          const xRotation = -Math.PI / 2;
          const yRotation = startData.rotation.y + deltaAngle;
          
          const quaternion = new THREE.Quaternion();
          const xQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), xRotation);
          const yQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yRotation);
          quaternion.multiplyQuaternions(yQuat, xQuat);
          
          obj.rotation.setFromQuaternion(quaternion);
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
    container.value.style.cursor = 'crosshair';
    console.log('移动完成');
  }
  if (isRotating) {
    isRotating = false;
    hideRotationRing();
    container.value.style.cursor = 'crosshair';
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
  const modelName = event.dataTransfer.getData('modelName');
  if (!modelName || !models[modelName]) return;
  
  // 计算鼠标在画布中的位置
  const rect = container.value.getBoundingClientRect();
  const mouseX = ((event.clientX - rect.left) / container.value.clientWidth) * 2 - 1;
  const mouseY = -((event.clientY - rect.top) / container.value.clientHeight) * 2 + 1;
  
  // 发射射线检测地面
  raycaster.setFromCamera(new THREE.Vector2(mouseX, mouseY), camera);
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  const intersectPoint = new THREE.Vector3();
  
  if (raycaster.ray.intersectPlane(plane, intersectPoint)) {
    // 对齐到网格
    intersectPoint.x = Math.round(intersectPoint.x * 10) / 10;
    intersectPoint.z = Math.round(intersectPoint.z * 10) / 10;
    
    // 使用addModelInternal方法添加模型，确保类型信息被记录
    const newModel = addModelInternal(modelName, {
      x: intersectPoint.x,
      y: 0,
      z: intersectPoint.z
    });
    
    if (newModel) {
      console.log('模型放置到位置:', intersectPoint);
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
    
    // 设置位置
    if (position) {
      newModel.position.set(position.x, position.y, position.z);
    } else {
      newModel.position.set(0, 0, 0);
    }
    
    scene.add(newModel);
    sceneObjects.push(newModel);
    
    console.log('模型添加到场景:', newModel.uuid, '类型:', modelName, 'sceneObjects数量:', sceneObjects.length);
    emit('model-added', newModel);
    
    return newModel;
  }
  return null;
}

defineExpose({
  addModel(modelName, position = null) {
    return addModelInternal(modelName, position);
  },
  
  rotateObject(angle) {
    if (selectedObjects.length > 0) {
      const rad = -angle * Math.PI / 180;
      
      let totalX = 0, totalZ = 0;
      selectedObjects.forEach(obj => {
        totalX += obj.position.x;
        totalZ += obj.position.z;
      });
      const centerX = totalX / selectedObjects.length;
      const centerZ = totalZ / selectedObjects.length;
      
      selectedObjects.forEach(obj => {
        const relativePos = new THREE.Vector3(
          obj.position.x - centerX,
          0,
          obj.position.z - centerZ
        );
        
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        const newX = relativePos.x * cos - relativePos.z * sin;
        const newZ = relativePos.x * sin + relativePos.z * cos;
        
        obj.position.x = centerX + newX;
        obj.position.z = centerZ + newZ;
        
        // 保持货架的X轴旋转（-90度），只更新Y轴旋转
        const xRotation = -Math.PI / 2;
        const yRotation = rad;
        
        const quaternion = new THREE.Quaternion();
        const xQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), xRotation);
        const yQuat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yRotation);
        quaternion.multiplyQuaternions(yQuat, xQuat);
        
        obj.rotation.setFromQuaternion(quaternion);
      });
      
      updateCornerMarkers();
      if (rotationRing) {
        showRotationRing();
      }
    }
  },
  
  moveObject(startMoving) {
    if (startMoving && selectedObjects.length > 0) {
      isMoving = true;
      container.value.style.cursor = 'move';
      moveOffset.set(0, 0, 0);
    } else {
      isMoving = false;
      container.value.style.cursor = 'crosshair';
    }
  },
  
  startRotate() {
    if (selectedObjects.length > 0) {
      isRotating = true;
      
      rotationStartPositions.clear();
      selectedObjects.forEach(obj => {
        rotationStartPositions.set(obj, {
          position: obj.position.clone(),
          rotation: obj.rotation.clone()
        });
      });
      
      rotationStartAngle = null;
      
      showRotationRing();
      container.value.style.cursor = 'grab';
      console.log('进入旋转模式，选中对象数:', selectedObjects.length);
    }
  },
  
  deleteObject() {
    deleteSelectedObjects();
  },
  
  clearScene() {
    sceneObjects.forEach(obj => scene.remove(obj));
    sceneObjects = [];
    selectedObject = null;
    selectedObjects = [];
    isRotating = false;
    hideRotationRing();
    cornerMarkers.forEach(marker => scene.remove(marker));
    cornerMarkers = [];
    emit('object-deselected');
  },
  
  getSelectedObjectsCount() {
    return selectedObjects.length;
  },
  
  getSceneObjects() {
    return sceneObjects;
  },
  
  exportImage() {
    // 渲染场景
    renderer.render(scene, camera);
    
    // 获取canvas数据URL
    const dataURL = renderer.domElement.toDataURL('image/png');
    
    // 创建下载链接
    const link = document.createElement('a');
    link.href = dataURL;
    link.download = `仓酷家设计效果图_${new Date().toLocaleDateString('zh-CN')}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('效果图已导出');
    return true;
  },
  
  previewBatchCopyHorizontal(params) {
    clearBatchPreview();
    if (!selectedObject) return;
    
    const { totalGroups, direction } = params;
    const startPos = selectedObject.position.clone();
    const startRotation = selectedObject.rotation.z;
    
    const box = new THREE.Box3().setFromObject(selectedObject);
    const size = box.getSize(new THREE.Vector3());
    const shelfWidth = size.x;
    const spacing = shelfWidth + 0.1;
    
    for (let i = 1; i < totalGroups; i++) {
      const previewModel = selectedObject.clone();
      
      previewModel.traverse((child) => {
        if (child.material) {
          child.material = child.material.clone();
          child.material.transparent = true;
          child.material.opacity = 0.4;
          child.material.emissive = new THREE.Color(0x4fc3f7);
          child.material.emissiveIntensity = 0.2;
        }
      });
      
      let x = startPos.x;
      if (direction === 'positive') {
        x += i * spacing;
      } else {
        x -= i * spacing;
      }
      
      previewModel.position.set(x, startPos.y, startPos.z);
      previewModel.rotation.z = startRotation;
      
      scene.add(previewModel);
      batchPreviewObjects.push(previewModel);
    }
    
    console.log('横向复制预览:', totalGroups, '组, 间距:', spacing, '米');
  },
  
  confirmBatchCopyHorizontal(params) {
    if (!selectedObject) return;
    
    const { totalGroups, direction } = params;
    const startPos = selectedObject.position.clone();
    const startRotation = selectedObject.rotation.z;
    
    const box = new THREE.Box3().setFromObject(selectedObject);
    const size = box.getSize(new THREE.Vector3());
    const shelfWidth = size.x;
    const spacing = shelfWidth + 0.1;
    
    clearBatchPreview();
    
    for (let i = 1; i < totalGroups; i++) {
      const newModel = selectedObject.clone();
      
      newModel.traverse((child) => {
        if (child.material) {
          child.material = child.material.clone();
          child.material.transparent = false;
          child.material.opacity = 1.0;
          child.material.emissive = new THREE.Color(0x000000);
          child.material.emissiveIntensity = 0;
        }
      });
      
      // 继承原对象的类型信息
      newModel.userData.modelType = selectedObject.userData?.modelType;
      newModel.userData.modelId = selectedObject.userData?.modelId;
      
      let x = startPos.x;
      if (direction === 'positive') {
        x += i * spacing;
      } else {
        x -= i * spacing;
      }
      
      newModel.position.set(x, startPos.y, startPos.z);
      newModel.rotation.z = startRotation;
      
      scene.add(newModel);
      sceneObjects.push(newModel);
      emit('model-added', newModel);
    }
    
    console.log('横向复制完成:', totalGroups, '组, 间距:', spacing, '米');
  },
  
  previewBatchCopyVertical(params) {
    clearBatchPreview();
    if (!selectedObject) return;
    
    const { columns, groupsPerColumn, columnSpacing, direction } = params;
    const startPos = selectedObject.position.clone();
    const startRotation = selectedObject.rotation.z;
    
    const box = new THREE.Box3().setFromObject(selectedObject);
    const size = box.getSize(new THREE.Vector3());
    const shelfDepth = size.z;
    const shelfWidth = size.x;
    
    // 纵向复制逻辑（货架沿Z方向排列）：
    // - 每列内部（X方向，货架宽度方向）：货架宽度 + 10CM（紧密排列）
    // - 列与列之间（Z方向，货架深度方向）：用户设定的通道间距
    const colSpacing = columnSpacing; // 列间距（Z方向）= 用户设定的通道间距
    const rowSpacing = shelfWidth + 0.1; // 行间距（X方向）= 货架宽度 + 10CM
    
    for (let col = 0; col < columns; col++) {
      for (let row = 0; row < groupsPerColumn; row++) {
        if (col === 0 && row === 0) continue;
        
        const previewModel = selectedObject.clone();
        
        previewModel.traverse((child) => {
          if (child.material) {
            child.material = child.material.clone();
            child.material.transparent = true;
            child.material.opacity = 0.4;
            child.material.emissive = new THREE.Color(0x4fc3f7);
            child.material.emissiveIntensity = 0.2;
          }
        });
        
        let x = startPos.x;
        let z = startPos.z;
        
        // X方向：行偏移（货架宽度 + 10CM）
        x += row * rowSpacing;
        
        // Z方向：列偏移（用户设定的通道间距）
        if (direction === 'positive') {
          z += col * colSpacing;
        } else {
          z -= col * colSpacing;
        }
        
        previewModel.position.set(x, startPos.y, z);
        previewModel.rotation.z = startRotation;
        
        scene.add(previewModel);
        batchPreviewObjects.push(previewModel);
      }
    }
    
    console.log('纵向复制预览:', columns, '列,', groupsPerColumn, '组/列, 列间距:', colSpacing, '米, 行间距:', rowSpacing, '米');
  },
  
  confirmBatchCopyVertical(params) {
    if (!selectedObject) return;
    
    const { columns, groupsPerColumn, columnSpacing, direction } = params;
    const startPos = selectedObject.position.clone();
    const startRotation = selectedObject.rotation.z;
    
    const box = new THREE.Box3().setFromObject(selectedObject);
    const size = box.getSize(new THREE.Vector3());
    const shelfDepth = size.z;
    const shelfWidth = size.x;
    
    // 纵向复制逻辑（货架沿Z方向排列）：
    // - 每列内部（X方向，货架宽度方向）：货架宽度 + 10CM（紧密排列）
    // - 列与列之间（Z方向，货架深度方向）：用户设定的通道间距
    const colSpacing = columnSpacing; // 列间距（Z方向）= 用户设定的通道间距
    const rowSpacing = shelfWidth + 0.1; // 行间距（X方向）= 货架宽度 + 10CM
    
    clearBatchPreview();
    
    for (let col = 0; col < columns; col++) {
      for (let row = 0; row < groupsPerColumn; row++) {
        if (col === 0 && row === 0) continue;
        
        const newModel = selectedObject.clone();
        
        newModel.traverse((child) => {
          if (child.material) {
            child.material = child.material.clone();
            child.material.transparent = false;
            child.material.opacity = 1.0;
            child.material.emissive = new THREE.Color(0x000000);
            child.material.emissiveIntensity = 0;
          }
        });
        
        // 继承原对象的类型信息
        newModel.userData.modelType = selectedObject.userData?.modelType;
        newModel.userData.modelId = selectedObject.userData?.modelId;
        
        let x = startPos.x;
        let z = startPos.z;
        
        // X方向：行偏移（货架宽度 + 10CM）
        x += row * rowSpacing;
        
        // Z方向：列偏移（用户设定的通道间距）
        if (direction === 'positive') {
          z += col * colSpacing;
        } else {
          z -= col * colSpacing;
        }
        
        newModel.position.set(x, startPos.y, z);
        newModel.rotation.z = startRotation;
        
        scene.add(newModel);
        sceneObjects.push(newModel);
        emit('model-added', newModel);
      }
    }
    
    console.log('纵向复制完成:', columns, '列,', groupsPerColumn, '组/列, 列间距:', colSpacing, '米, 行间距:', rowSpacing, '米');
  },
  
  cancelBatchCopy() {
    clearBatchPreview();
  }
});
</script>

<style scoped>
.three-container {
  width: 100%;
  height: 100%;
  background: #f0f0e6;
  cursor: crosshair;
}
</style>