# 仓库家 V1.1 项目状态

## 更新时间
2026-03-08

## 项目架构

### 前端 (Frontend)
- **框架**: Vue 3 + Vite
- **3D引擎**: Three.js
- **UI组件**: 自定义组件
- **端口**: 5173

### 后端 (Backend)
- **框架**: FastAPI
- **语言**: Python
- **端口**: 8000

## 核心功能页面

### P1: 核心功能页 (CoreFunction.vue)
**当前菜单结构 (4步流程):**

#### NO1: 创建仓库
- 创建新仓库（层高、水平高度设置）
- 绘制工具（开始绘制、编辑、清空、完成）
- 快捷生成矩形仓库
- 保存仓库
- 导入仓库

#### NO2: 功能区规划
- 功能区操作（创建、编辑、删除选中）
- 功能区类型（12种）:
  - 收货区、收货暂存区
  - 存储区、生产区
  - 发货区、发货暂存区
  - 办公区、厕所
  - 叉车充电区、辅助功能区
- 文字标注（添加、编辑、删除）
- 生成3D仓库

#### NO3: 添加物流模型
**9大分类，40个对象:**

1. **仓库附属设施** (2个): 门、窗
2. **货架系统** (12个): A101-A112
3. **载具容器** (8个): C101-C108
4. **搬运设备** (6个): B101-B106
5. **输送设备** (3个): D101-D103
6. **拣选设备** (3个): E101-E103
7. **分拣设备** (2个): H101-H102 ⭐新增
8. **其他设备** (2个): F101-F102
9. **人员** (1个): G101

**对象操作:**
- 移动、旋转、删除、复制
- 批量复制（行数、列数、行间距、列间距、旋转角度、预览、生成）
- 对齐工具（左对齐、右对齐、居中对齐、水平等距、垂直等距）
- 保存和导出

## 3D模型系统

### 模型加载
- **格式**: GLB (GLTF二进制格式)
- **数量**: 40个模型文件
- **位置**: `/frontend/public/assets/models/`
- **生成工具**: Python + Trimesh

### 坐标系
- **Three.js**: Y轴向上
- **Trimesh**: Z轴向上
- **转换**: -90度绕X轴旋转
- **单位**: cm (1 Three.js单位 = 1cm)

### 材质处理
- 使用 MeshBasicMaterial 显示顶点颜色
- GLB模型已包含顶点颜色信息

## 关键功能实现

### 批量复制
```javascript
// 参数
rows: 行数 (1-10)
cols: 列数 (1-10)
rowSpacing: 行间距/通道宽度 (1-10m)
colSpacing: 列间距 (0-5m)
rotation: 旋转角度 (0-360°)

// 操作
1. 选中对象
2. 设置参数
3. 点击"预览"（半透明对象随鼠标移动）
4. ESC取消 或 点击"批量生成"
```

### 对齐工具
- 左对齐: 以第一个对象为基准左对齐
- 右对齐: 以第一个对象为基准右对齐
- 居中对齐: 以第一个对象为基准居中对齐
- 水平等距: 在第一个和最后一个对象之间等距分布
- 垂直等距: 在第一个和最后一个对象之间等距分布

### 键盘快捷键
- **ESC**: 取消当前操作（线段编辑、批量预览等）
- **Delete/Backspace**: 删除选中的功能区

## 项目文件结构

```
cangkujia V1.1/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── views/
│   │   │   ├── CoreFunction.vue    # 核心功能页
│   │   │   ├── Home.vue            # 首页
│   │   │   └── ModelLibrary.vue    # 模型库页
│   │   ├── components/
│   │   │   ├── 3d/
│   │   │   │   └── ThreeScene.vue  # 3D场景组件
│   │   │   └── 2d/
│   │   │       └── Warehouse2D.vue # 2D绘制组件
│   │   └── ...
│   └── public/
│       └── assets/
│           └── models/       # 40个GLB模型文件
├── backend/                  # 后端项目
│   └── main.py
├── scripts/                  # 工具脚本
│   └── model_generator_template.py  # 模型生成模板
└── docs/                     # 文档
```

## 模型生成脚本

### 位置
`scripts/model_generator_template.py`

### 功能
- 使用 Trimesh 生成3D模型
- 支持顶点颜色
- 自动坐标转换
- 导出GLB格式

### 使用示例
```python
from model_generator_template import generate_shelf, COLORS

scene, metadata = generate_shelf(
    length=2300,      # mm
    width=1000,       # mm
    height=4500,      # mm
    levels=4,
    colors={
        'upright': COLORS['blue'],
        'beam': COLORS['orange'],
        'deck': COLORS['gray']
    }
)
```

## 开发经验总结

### 1. 坐标系处理（关键！）
```python
# Trimesh Z轴向上 → Three.js Y轴向上
rotation_matrix = trimesh.transformations.rotation_matrix(
    angle=-np.pi / 2,
    direction=[1, 0, 0],
    point=[0, 0, 0]
)
```

### 2. 颜色设置（顶点颜色法）
```python
def set_mesh_color(mesh, color_rgb):
    color_255 = [int(c * 255) for c in color_rgb] + [255]
    if hasattr(mesh.visual, 'vertex_colors'):
        mesh.visual.vertex_colors = color_255
    return mesh
```

### 3. 前端材质处理
```javascript
model.traverse((child) => {
  if (child.isMesh) {
    if (child.geometry.attributes.color) {
      child.material = new THREE.MeshBasicMaterial({ vertexColors: true });
    }
  }
});
```

### 4. 比例尺转换
- GLB导出使用 mm 单位
- Three.js 使用 cm 单位
- 加载时缩放: `model.scale.set(0.1, 0.1, 0.1)`

## 最近更新 (2026-03-08)

### 新增功能
1. ✅ 分拣设备分类（2个对象）
2. ✅ 批量复制功能（行列、间距、旋转、预览）
3. ✅ 对齐工具（左/右/居中、等距分布）
4. ✅ 功能区删除功能
5. ✅ 文字标注编辑/删除功能
6. ✅ ESC取消批量预览

### 菜单重构
- NO5 完成项目 已删除
- 保存/导出功能移动到 NO3
- 生成3D仓库功能合并到 NO2

### 界面优化
- 当前步骤高亮显示
- 步骤完成状态标记
- 菜单分组更清晰

## 待办事项

### 高优先级
- [ ] 测试所有40个3D模型的加载和显示
- [ ] 验证批量复制功能的准确性
- [ ] 测试对齐工具的各种场景

### 中优先级
- [ ] 添加更多分拣设备模型
- [ ] 优化模型加载性能（懒加载）
- [ ] 添加对象属性编辑功能

### 低优先级
- [ ] 框选多对象功能
- [ ] 撤销/重做功能
- [ ] 项目报告生成功能

## 已知问题

暂无

## 联系方式

项目维护: RMF (AI Assistant)
