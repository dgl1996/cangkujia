# 统一移动逻辑 Spec

## Why
外墙标语移动后无法保存位置的问题根因已找到：`onMouseMove` 中存在两套移动逻辑，第二套直接操作 `position` 的逻辑被实际执行，但没有调用 `moveWallSign` 来更新 `offsetAlongWall`。本次重构统一使用 `moveSelectedObjects` 函数，确保所有对象类型的移动逻辑一致。

## What Changes
- 重构 `onMouseMove` 中的移动逻辑，统一使用 `moveSelectedObjects` 函数
- 将吸附逻辑整合到 `moveSelectedObjects` 中
- 确保外墙标语移动时正确更新 `offsetAlongWall`
- **不修改** `moveWallSign` 函数本身（只确保它被正确调用）
- **不修改** 保存/加载逻辑（已在其他 spec 中完成）

## Impact
- **Affected files**:
  - `frontend/src/components/3d/ThreeScene.vue` - 移动逻辑重构
- **Risk level**: 中（修改核心移动逻辑，需确保不影响其他对象类型）
- **受影响的功能**:
  - 所有3D对象的移动操作
  - 对齐线吸附功能
  - 外墙标语移动

## ADDED Requirements

### Requirement: 统一移动入口
The system SHALL use `moveSelectedObjects` as the single entry point for all object movement.

#### Scenario: 移动模式激活时统一处理
- **WHEN** 用户进入移动模式并拖动鼠标
- **THEN** 所有对象移动都通过 `moveSelectedObjects` 函数处理
- **AND** 不再存在直接操作 `position` 的第二套逻辑

### Requirement: 吸附逻辑整合
The system SHALL integrate alignment line snap logic into `moveSelectedObjects`.

#### Scenario: 移动时自动吸附
- **WHEN** 用户移动对象且有对齐线存在
- **THEN** `moveSelectedObjects` 内部调用吸附检测
- **AND** 根据对象类型应用不同的吸附策略

### Requirement: 外墙标语移动正确更新偏移量
The system SHALL ensure wall sign movement updates `offsetAlongWall`.

#### Scenario: 外墙标语移动
- **WHEN** 用户移动外墙标语
- **THEN** `moveWallSign` 函数被调用
- **AND** `offsetAlongWall` 被正确更新
- **AND** 保存时 `offsetAlongWall` 值正确

## MODIFIED Requirements

### Requirement: 鼠标移动处理
**原需求**: `onMouseMove` 中包含两套独立的移动逻辑
**修改后**: `onMouseMove` 只负责计算目标位置，统一调用 `moveSelectedObjects`

#### Scenario: 鼠标移动时
- **WHEN** `isMoving` 为 true 且 `selectedObjects` 不为空
- **THEN** 计算目标位置（考虑吸附）
- **AND** 调用 `moveSelectedObjects(delta)` 执行实际移动

## REMOVED Requirements
无

## Implementation Notes

### 技术方案
1. **保留** `moveSelectedObjects` 作为统一入口
2. **整合** 吸附逻辑到 `moveSelectedObjects` 中
3. **移除** `onMouseMove` 中的第二套直接操作 `position` 的逻辑
4. **确保** `moveWallSign` 被正确调用

### 现有代码结构分析
```
onMouseMove (当前)
├── 对齐线绘制预览
├── 测量模式预览
├── 移动模式 (第一套逻辑 - 未被执行)
│   └── moveSelectedObjects(delta)
├── 旋转模式
└── 直接拖拽模式 (第二套逻辑 - 实际被执行)
    └── 直接修改 position.x/position.z
```

### 重构后代码结构
```
onMouseMove (重构后)
├── 对齐线绘制预览
├── 测量模式预览
├── 移动模式 (统一逻辑)
│   ├── 计算目标位置
│   ├── 检测吸附
│   ├── 计算 delta
│   └── moveSelectedObjects(delta)
└── 旋转模式
```

### 关键修改点
1. **移除** `onMouseMove` 中约第3200-3247行的直接拖拽逻辑
2. **增强** `moveSelectedObjects` 函数，添加吸附检测
3. **确保** 吸附后的位置变化正确传递给 `moveSelectedObjects`

### 避坑指南
- **不要** 修改 `moveWallSign` 函数本身，只确保它被调用
- **不要** 修改保存/加载逻辑
- **确保** 吸附功能在重构后仍然正常工作
- **测试** 所有对象类型的移动（货架、人员、设备、标语等）
