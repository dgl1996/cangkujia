<template>
  <div ref="container" class="model-preview-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载模型中...</p>
    </div>
    <div v-if="error" class="error-overlay">
      <p>模型加载失败</p>
      <button @click="retryLoad">重试</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const props = defineProps({
  modelUrl: {
    type: String,
    required: true
  },
  autoRotate: {
    type: Boolean,
    default: true
  },
  customColors: {
    type: Object,
    default: null
  }
});

const container = ref(null);
const loading = ref(true);
const error = ref(false);

let scene, camera, renderer, controls, model;

const initThree = () => {
  if (!container.value) return;

  // 场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf5f7fa);

  // 相机
  const width = container.value.clientWidth;
  const height = container.value.clientHeight;
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 10000);
  camera.position.set(3000, 2500, 3000);

  // 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.shadowMap.enabled = false; // 禁用阴影避免纹理问题
  container.value.appendChild(renderer.domElement);

  // 控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.autoRotate = props.autoRotate;
  controls.autoRotateSpeed = 2;

  // 灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(1000, 2000, 1000);
  directionalLight.castShadow = false; // 禁用阴影
  scene.add(directionalLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
  fillLight.position.set(-1000, 1000, -1000);
  scene.add(fillLight);

  // 网格地面
  const gridHelper = new THREE.GridHelper(5000, 20, 0xcccccc, 0xe5e5e5);
  scene.add(gridHelper);

  // 开始渲染循环
  animate();
};

const loadModel = () => {
  if (!props.modelUrl) return;
  
  loading.value = true;
  error.value = false;

  const loader = new GLTFLoader();
  loader.load(
    props.modelUrl,
    (gltf) => {
      // 移除旧模型
      if (model) {
        scene.remove(model);
      }

      model = gltf.scene;
      
      // 调试信息
      console.log('模型加载成功:', props.modelUrl);
      console.log('模型类型:', model.type);
      console.log('子对象数量:', model.children.length);

      // 计算模型边界
      const box = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      
      console.log('模型尺寸:', size.x, size.y, size.z);

      // 居中模型
      model.position.x = -center.x;
      model.position.y = -box.min.y; // 放在地面上
      model.position.z = -center.z;

      // 颜色名称到RGB的映射
      const colorMap = {
        '红色': 0xDC2626,      // 红色
        '橙红': 0xEA580C,      // 橙红色
        '淡蓝色': 0x60A5FA,    // 淡蓝色
        '白色': 0xFFFFFF,      // 白色
        '蓝色': 0x3B82F6,      // 蓝色
        '橙色': 0xF97316,      // 橙色
        '灰色': 0x9CA3AF       // 灰色
      };
      
      // 处理材质 - 使用顶点颜色或自定义颜色
      let meshCount = 0;
      model.traverse((child) => {
        if (child.isMesh) {
          meshCount++;
          child.castShadow = false;
          child.receiveShadow = false;
          
          // 检查是否有顶点颜色
          const hasVertexColors = child.geometry && child.geometry.attributes.color;
          console.log(`Mesh ${meshCount}:`, child.name, '有顶点颜色:', !!hasVertexColors, '原材质:', child.material ? child.material.type : 'none');
          
          // 如果有自定义颜色配置，根据mesh名称应用颜色
          if (props.customColors) {
            let meshColor = null;
            const meshName = child.name.toLowerCase();
            
            // 根据mesh名称判断部件类型
            if (meshName.includes('upright') || meshName.includes('part_0') || meshName.includes('part_1') || meshName.includes('part_2') || meshName.includes('part_3') || meshName.includes('diag')) {
              // 立柱和斜拉支撑
              meshColor = colorMap[props.customColors.upright] || colorMap['蓝色'];
            } else if (meshName.includes('beam') || meshName.includes('part_4') || meshName.includes('part_5') || meshName.includes('part_6') || meshName.includes('part_7')) {
              // 横梁
              meshColor = colorMap[props.customColors.beam] || colorMap['橙色'];
            } else if (meshName.includes('deck') || meshName.includes('part_8') || meshName.includes('part_9') || meshName.includes('part_10')) {
              // 层板
              meshColor = colorMap[props.customColors.deck] || colorMap['白色'];
            } else if (meshName.includes('foot')) {
              // 脚垫使用横梁颜色
              meshColor = colorMap[props.customColors.beam] || colorMap['橙色'];
            }
            
            if (meshColor) {
              child.material = new THREE.MeshBasicMaterial({ color: meshColor });
            } else if (hasVertexColors) {
              child.material = new THREE.MeshBasicMaterial({ vertexColors: true });
            } else {
              child.material = new THREE.MeshBasicMaterial({ color: 0x888888 });
            }
          } else if (hasVertexColors) {
            // 没有自定义颜色，使用顶点颜色
            child.material = new THREE.MeshBasicMaterial({ vertexColors: true });
          } else {
            child.material = new THREE.MeshBasicMaterial({ color: 0x888888 });
          }
        }
      });
      console.log('总共处理了', meshCount, '个Mesh');

      scene.add(model);

      // 调整相机位置以适应模型
      const maxDim = Math.max(size.x, size.y, size.z);
      console.log('Max dimension:', maxDim);
      
      // 根据模型大小调整相机距离 - 放大比例让模型更容易看到
      let distance;
      if (maxDim < 3000) {
        distance = maxDim * 1.5;  // 小模型 - 更近
      } else if (maxDim < 8000) {
        distance = maxDim * 1.2;  // 中型模型 - 更近
      } else {
        distance = maxDim * 1.0;  // 大模型 - 正常距离
      }
      
      console.log('Camera distance:', distance);
      
      // 设置相机位置，确保模型在视野中央且大小合适
      camera.position.set(distance, distance * 0.6, distance);
      camera.lookAt(0, size.y / 2, 0);
      controls.target.set(0, size.y / 2, 0);
      controls.update();

      loading.value = false;
    },
    (progress) => {
      console.log('加载进度:', (progress.loaded / progress.total * 100) + '%');
    },
    (err) => {
      console.error('模型加载失败:', err);
      error.value = true;
      loading.value = false;
    }
  );
};

const retryLoad = () => {
  loadModel();
};

const animate = () => {
  if (!renderer) return;
  
  requestAnimationFrame(animate);
  
  if (controls) {
    controls.update();
  }
  
  renderer.render(scene, camera);
};

const handleResize = () => {
  if (!container.value || !camera || !renderer) return;
  
  const width = container.value.clientWidth;
  const height = container.value.clientHeight;
  
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};

onMounted(() => {
  initThree();
  loadModel();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  
  if (renderer) {
    renderer.dispose();
    if (container.value && renderer.domElement) {
      container.value.removeChild(renderer.domElement);
    }
  }
  
  if (controls) {
    controls.dispose();
  }
});

watch(() => props.modelUrl, () => {
  loadModel();
});
</script>

<style scoped>
.model-preview-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(248, 249, 255, 0.9);
  color: #4a4a68;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e8ecff;
  border-top-color: #4361ee;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-overlay button {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}

.error-overlay button:hover {
  opacity: 0.9;
}
</style>
