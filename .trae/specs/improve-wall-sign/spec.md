# 外墙标语功能优化 Spec

## Why
现有外墙标语功能存在 Z-fighting（闪烁）问题，且标语与墙体没有父子级关联，导致墙体变化时标语不会跟随。本次优化采用 Canvas 动态纹理 + 浮动平面方案，解决视觉问题并完善关联逻辑。

## What Changes
- 优化标语材质，添加 `polygonOffset` 解决 Z-fighting 闪烁问题
- 建立标语与墙体的父子级关联，确保墙体移动时标语跟随
- 优化标语位置计算，确保准确贴合墙面
- 完善保存/加载逻辑，确保标语数据完整恢复
- **BREAKING**: 修改标语数据结构，添加 `parentWall` 引用

## Impact
- **Affected files**:
  - `frontend/src/components/3d/ThreeScene.vue` - 标语创建、更新逻辑
  - `frontend/src/views/CoreFunction.vue` - 标语保存/加载逻辑
- **Risk level**: 中（修改现有功能，需确保向后兼容）

## ADDED Requirements

### Requirement: Z-fighting 修复
The system SHALL fix the Z-fighting issue for wall signs.

#### Scenario: 标语贴合墙面无闪烁
- **WHEN** 用户将标语放置到墙面上
- **THEN** 标语显示清晰，无闪烁现象
- **AND** 使用 `polygonOffset: true` 和 `polygonOffsetFactor: -1` 确保标语在墙体前方渲染

### Requirement: 父子级关联
The system SHALL establish parent-child relationship between wall and sign.

#### Scenario: 墙体移动时标语跟随
- **WHEN** 墙体位置发生变化（如仓库重新生成）
- **THEN** 标语自动跟随墙体移动，保持相对位置不变
- **AND** 标语始终贴合墙面

#### Scenario: 保存/加载保留关联
- **WHEN** 用户保存项目
- **THEN** 标语的墙体关联信息被保存
- **AND** 导入时根据墙体索引重新建立关联

## MODIFIED Requirements

### Requirement: 标语创建
**原需求**: 创建独立 Mesh 对象
**修改后**: 创建 Mesh 并建立父子级关联

#### Scenario: 创建标语
- **WHEN** 调用 `createWallSign()`
- **THEN** 创建标语 Mesh
- **AND** 将标语添加到墙体对象的 children 中（而非直接添加到 scene）
- **AND** 设置 `polygonOffset` 材质属性

### Requirement: 标语更新
**原需求**: 移除旧标语，创建新标语
**修改后**: 保持父子级关联，仅更新内容

#### Scenario: 更新标语内容
- **WHEN** 用户编辑标语内容
- **THEN** 更新 Canvas 纹理
- **AND** 保持与墙体的父子级关联不变

## REMOVED Requirements
无

## Implementation Notes

### 技术方案
采用 Canvas 动态纹理 + 浮动平面方案，重点优化：
1. 材质添加 `polygonOffset` 解决 Z-fighting
2. 标语作为墙体的子对象，建立父子级关联
3. 保存时记录墙体索引，加载时重新关联

### 数据结构
```javascript
// 标语对象 userData
{
  type: 'wallSign',
  text: '外墙标语',
  fontSize: 24,
  textColor: '#FFFFFF',
  bgColor: '#0066CC',
  wallIndex: 0,        // 用于重新关联墙体
  offsetAlongWall: 0,  // 沿墙体偏移量
  width: 10,
  height: 2
}
```

### 修改点清单
1. **ThreeScene.vue**: `createWallSign()` 添加 `polygonOffset` 材质
2. **ThreeScene.vue**: `createWallSign()` 将标语添加到墙体 children
3. **ThreeScene.vue**: `updateWallSign()` 保持父子级关联
4. **ThreeScene.vue**: 标语位置计算优化
5. **CoreFunction.vue**: 保存逻辑导出标语的 `wallIndex`
6. **CoreFunction.vue**: 导入逻辑根据 `wallIndex` 重新关联墙体

### 避坑指南
- **Z-fighting**: 必须使用 `polygonOffset`，仅调整 position.y 无法完全解决
- **父子级关联**: 标语应添加到墙体对象的 children，而非 scene
- **墙体查找**: 导入时通过 `wallIndex` 和 `userData.type === 'wall'` 查找对应墙体
