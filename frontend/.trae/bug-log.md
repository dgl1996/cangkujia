# Bug 日志

## 记录格式
- 日期: YYYY-MM-DD
- 问题描述: 简明描述
- 根本原因: 技术分析
- 解决方案: 修复方法
- 状态: 已修复/待修复/重复出现
- 相关文件: 涉及的文件路径

---

## 2025-03-12

### Bug #1: 自定义货架点击放置后看不见
**问题描述**: P1页点击"自定义轻型货架"按钮，选择规格确认后，模型添加到场景但用户看不见

**根本原因**: 
1. 相机位置太远（约11000单位），模型在相机前方500单位，但模型尺寸相对太小
2. 模型Y位置太低（y=0.02），被zone平面（y=1）遮挡
3. 射线检测不到货架，因为货架在zone下方

**解决方案**: 
1. 将货架Y位置提高到2.0（在zone上方）
2. 添加`userData.type = 'shelf'`用于射线检测识别
3. 强制计算几何体边界框

**状态**: 已修复（但后续发现新问题）

**相关文件**: 
- `CoreFunction.vue`
- `ThreeScene.vue`

---

### Bug #2: 自定义货架模型只有一个点/看不见（重复出现）
**问题描述**: 从"我的模型"拖拽自定义货架到画布，模型只有一个点那么大，几乎看不见

**根本原因**: 
1. `modelUrl`是完整路径`/assets/models/shelf-beam-medium.glb`
2. 但`ThreeScene.vue`的`models`对象中使用的是模型ID`shelf-beam-medium`
3. 导致`createPlaceholderObject`函数找不到预加载的GLB模型，使用默认的小立方体代替

**解决方案**: 
在`onCustomModelDragStart`函数中，从`modelUrl`提取模型ID：
```javascript
const match = model.modelUrl.match(/\/([^\/]+)\.glb$/);
if (match) {
  modelIdentifier = match[1]; // 提取出 shelf-beam-medium
}
```

**状态**: 待验证

**相关文件**: 
- `CoreFunction.vue` - `onCustomModelDragStart`函数
- `ThreeScene.vue` - `createPlaceholderObject`函数

**历史记录**: 
- 类似症状在Bug #1中出现过，但原因不同（那次是边界框为0）
- 本次是模型ID不匹配导致加载失败

---

## 待记录问题

### 问题: 自定义货架生成机制
**描述**: 当前P2页生成的自定义货架使用现有GLB模型（如shelf-beam-medium.glb）作为基础，而不是根据用户参数生成真正的自定义几何体

**影响**: 用户看到的模型与填写的参数（长度、宽度、高度、层数）不匹配

**建议**: 
方案A: 使用程序化几何体根据参数实时生成货架（复杂，需要大量3D编程）
方案B: 预生成多种规格的GLB文件，根据用户选择加载对应规格（推荐，已实现）
方案C: 使用现有模型，但通过缩放变换近似匹配用户参数（简单，但不精确）

**状态**: 已实现方案B，使用预生成的light-duty系列模型

---

### Bug #3: 配组货架模型"躺着"且只有一组
**问题描述**: P2页预览配组货架时，模型是"躺着"的（横放），而且看起来只有一组而不是两组背靠背

**根本原因**: 
1. `generate_pair_shelf` 函数中，对几何体进行了两次旋转（`create_scene` 已经旋转一次，又手动旋转一次）
2. 两次旋转导致总共旋转-180度，模型"躺着"
3. 平移方向错误：沿Z轴平移，但旋转后Z轴变成了Y轴，导致两组货架重叠

**解决方案**: 
1. 移除 `generate_pair_shelf` 中的重复旋转（`create_scene` 已经处理了坐标转换）
2. 将平移方向从Z轴改为Y轴（`[0, 0, offset]` → `[0, offset, 0]`）

**状态**: 已修复

**相关文件**: 
- `scripts/model_generator_template.py` - `generate_pair_shelf` 函数

**历史记录**: 
- 类似问题在以往开发中多次出现，根本原因是Trimesh坐标系（Z轴向上）与Three.js坐标系（Y轴向上）的转换
- `create_scene` 函数已经统一处理了坐标转换，其他函数不应重复处理

**使用工具**: 3D对象生成工具 (`model_generator_template.py`)
- 单组货架: `generate_light_duty_shelf` 函数
- 配组货架: `generate_pair_shelf` 函数（调用单组函数×2 + 平移合并）

---

## 修复验证清单

- [ ] Bug #1 验证：自定义货架点击放置后可见
- [ ] Bug #2 验证：从"我的模型"拖拽后显示正常尺寸
- [ ] 预置货架拖拽功能未破坏
- [ ] P2页自定义货架保存功能正常
- [ ] P1/P2页"我的模型"同步正常

