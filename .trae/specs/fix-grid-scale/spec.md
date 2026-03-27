# 3D网格坐标轴单位统一修复 Spec

## Why
当前3D画布的网格坐标轴单位不统一，网格生成逻辑使用 `gridDivisions = Math.floor(gridSize / 10)`，导致：
- 不同大小的仓库，网格的视觉尺寸不同
- 用户无法通过网格直观判断1米的距离
- 影响对象放置时的空间感和距离估算

## What Changes
- **网格单元格**: 固定为1米（100cm），不随仓库大小变化
- **网格范围**: 固定为100米×100米（100×100个单元格）
- **网格中心**: 与仓库中心对齐
- **坐标轴刻度**: 固定1米间隔，添加刻度标签

## Impact
- **Affected files**:
  - `frontend/src/components/3d/ThreeScene.vue` - 网格生成函数（3处）
  - `frontend/src/components/3d/ThreeScene.vue` - 坐标轴指示器函数

- **Risk level**: 低（仅修改网格显示参数，不影响业务逻辑）

## ADDED Requirements

### Requirement: 固定尺寸网格
The system SHALL provide a fixed-size grid in the 3D canvas.

#### Scenario: 矩形仓库网格
- **WHEN** 创建矩形仓库时调用 `createWarehouse()`
- **THEN** 网格单元格大小固定为100cm×100cm
- **AND** 网格总大小固定为10000cm×10000cm（100m×100m）
- **AND** 网格中心与仓库中心对齐
- **AND** 网格透明度保持10%

#### Scenario: 多边形仓库网格
- **WHEN** 创建多边形仓库时调用 `createWarehouseFromShape()`
- **THEN** 网格单元格大小固定为100cm×100cm
- **AND** 网格总大小固定为10000cm×10000cm（100m×100m）
- **AND** 网格中心与仓库中心对齐

#### Scenario: 坐标轴刻度
- **WHEN** 创建或更新坐标轴指示器
- **THEN** X轴和Z轴每100cm显示一个刻度标记
- **AND** 每1000cm（10米）显示一个刻度标签（如"10m", "20m"）
- **AND** 刻度标签位于坐标轴正方向

## MODIFIED Requirements

### Requirement: 网格生成参数
**File**: `ThreeScene.vue`

**Current Implementation**:
```javascript
// 矩形仓库
createWarehouse() {
  const gridSize = Math.max(length, width);
  const gridDivisions = Math.floor(gridSize / 10); // 每10cm一个网格
  const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, ...);
}

// 多边形仓库
createWarehouseFromShape() {
  const gridSize = Math.max(boundsWidth, boundsDepth);
  const gridDivisions = Math.floor(gridSize / 10); // 每10cm一个网格
  const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, ...);
}
```

**Modified Implementation**:
```javascript
// 统一固定参数
const GRID_CELL_SIZE = 100; // 1米 = 100cm
const GRID_TOTAL_SIZE = 10000; // 100米 = 10000cm
const GRID_DIVISIONS = 100; // 100×100个单元格

// 矩形仓库和多边形仓库统一使用
const gridHelper = new THREE.GridHelper(GRID_TOTAL_SIZE, GRID_DIVISIONS, ...);
gridHelper.position.x = centerX; // 与仓库中心对齐
gridHelper.position.z = centerZ; // 与仓库中心对齐
```

### Requirement: 坐标轴指示器刻度
**File**: `ThreeScene.vue`

**Current Implementation**:
- 只有X+/X-/Z+/Z-四个方向标识
- 无刻度标记和刻度标签

**Modified Implementation**:
- 每1米（100cm）显示一个短刻度线
- 每10米（1000cm）显示一个长刻度线+数字标签
- 标签格式: "10m", "20m", "30m"...
- 标签位于X+和Z+方向

## REMOVED Requirements
无

## Implementation Notes

### 修改点清单
1. **Line 4415-4417**: `createWarehouse()` 中的网格生成
2. **Line 4490-4491**: `createWarehouse()` 中的网格辅助线更新
3. **Line 4548-4550**: `createWarehouseFromShape()` 中的网格生成
4. **Line 4626-4627**: `createWarehouseFromShape()` 中的网格辅助线更新
5. **Line 2313-2423**: `createDirectionLabels()` 添加刻度
6. **Line 2428-2500**: `updateDirectionLabels()` 添加刻度

### 常量定义
```javascript
// 在 ThreeScene.vue 顶部添加常量
const GRID_CELL_SIZE = 100; // 1米 (cm)
const GRID_TOTAL_SIZE = 10000; // 100米 (cm)
const GRID_DIVISIONS = 100; // 100×100网格
```

### 测试验证
1. 创建10m×10m小仓库 → 网格单元格应为1米
2. 创建100m×100m大仓库 → 网格单元格仍应为1米
3. 使用测量工具测量网格边长 → 应显示1.00米
4. 检查坐标轴刻度 → 每1米应有刻度，每10米应有标签
