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

      // 处理材质 - 使用顶点颜色
      let meshCount = 0;
      model.traverse((child) => {
        if (child.isMesh) {
          meshCount++;
          child.castShadow = false;
          child.receiveShadow = false;
          
          // 检查是否有顶点颜色
          const hasVertexColors = child.geometry && child.geometry.attributes.color;
          console.log(`Mesh ${meshCount}:`, child.name, '有顶点颜色:', !!hasVertexColors);
          
          if (hasVertexColors) {
            // 有顶点颜色，使用MeshBasicMaterial显示
            const basicMaterial = new THREE.MeshBasicMaterial({
              vertexColors: true
            });
            child.material = basicMaterial;
          } else if (child.material) {
            // 没有顶点颜色，使用默认材质
            child.material = new THREE.MeshBasicMaterial({
              color: 0x888888
            });
          }
        }
      });
      console.log('总共处理了', meshCount, '个Mesh');

      scene.add(model);

      // 调整相机位置以适应模型
      const maxDim = Math.max(size.x, size.y, size.z);
      const distance = maxDim * 2;
      camera.position.set(distance, distance * 0.8, distance);
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
