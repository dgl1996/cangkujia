# 办公区自动墙体生成 Spec

## Why
用户需要在3D画布中自动为办公区生成墙体，墙体应沿着办公区边线自动生成，高度与仓库墙体保持一致。同时，这些墙体应支持添加门和窗户，与仓库墙体功能一致。

用户关心的核心问题：当用户在2D画布编辑办公区形状后切换到3D画布时，墙体是否能自动调整？

## What Changes
- **新增**: 办公区墙体自动生成逻辑
- **新增**: 办公区墙体随形状变化自动重建机制
- **修改**: `createZonesIn3D` 函数，为办公区类型(zoneType='office')生成墙体
- **修改**: `clearAllZones` 函数，清理办公区墙体
- **新增**: 办公区墙体门/窗支持（复用现有仓库墙体门/窗功能）

## Impact
- 影响文件:
  - `frontend/src/components/3d/ThreeScene.vue` - 主要实现文件
    - `createZonesIn3D` 函数：添加办公区墙体生成逻辑
    - `clearAllZones` 函数：添加办公区墙体清理逻辑
    - `deleteZone` 函数：添加单个办公区墙体清理逻辑
- 用户体验: 
  - 办公区加载到3D画布时自动生成墙体
  - 2D编辑后切换回3D，墙体自动重建适应新形状
  - 可在办公区墙体上添加门和窗户

## ADDED Requirements

### Requirement: 办公区墙体自动生成
The system SHALL 在加载办公区到3D画布时，自动沿着办公区边线生成墙体。

#### Scenario: 初始生成墙体
- **GIVEN** 用户在2D画布创建了办公区
- **WHEN** 点击"放置3D对象"切换到3D画布
- **THEN** 办公区周围自动生成墙体
- **AND** 墙体高度与仓库墙体高度一致
- **AND** 墙体使用与仓库墙体相同的材质和透明度

#### Scenario: 墙体属性
- **GIVEN** 办公区墙体已生成
- **THEN** 墙体userData包含：
  - type: 'officeWall'
  - zoneId: 关联的办公区ID
  - wallIndex: 墙体段索引
  - baseHeight: 基础高度
  - height: 墙体高度
  - openings: 门/窗开口数组

### Requirement: 墙体随形状自动重建
The system SHALL 当办公区形状在2D画布被修改后，重新切换到3D画布时，自动重建墙体以适应新形状。

#### Scenario: 2D编辑后重建
- **GIVEN** 办公区已在3D画布生成墙体
- **WHEN** 用户返回2D画布修改办公区形状
- **AND** 再次切换到3D画布
- **THEN** 原墙体被清除
- **AND** 根据新形状重新生成墙体
- **AND** 门/窗位置按比例调整或保持相对位置

#### Scenario: 技术实现机制
- **GIVEN** `createZonesIn3D` 函数被调用
- **THEN** 首先调用 `clearAllZones` 清除所有区域（包括墙体）
- **AND** 重新创建所有区域和办公区墙体
- **AND** 确保无重复墙体残留

### Requirement: 办公区门/窗支持
The system SHALL 允许用户在办公区墙体上添加门和窗户，与仓库墙体功能一致。

#### Scenario: 添加门/窗
- **GIVEN** 办公区墙体已生成
- **WHEN** 用户使用门/窗工具点击办公区墙体
- **THEN** 在点击位置创建门/窗
- **AND** 门/窗外观与仓库墙体门/窗一致

#### Scenario: 门/窗保存/加载
- **GIVEN** 办公区墙体上有门/窗
- **WHEN** 保存项目并重新加载
- **THEN** 门/窗正确恢复位置和属性

## MODIFIED Requirements

### Requirement: 区域清理逻辑
**原逻辑**: `clearAllZones` 只清理zone.mesh和zones数组
**新逻辑**: `clearAllZones` 同时清理办公区墙体（通过userData.zoneId关联）

**理由**: 确保2D/3D切换时旧墙体被正确清除，避免重复

### Requirement: 单个区域删除
**原逻辑**: `deleteZone` 只删除zone.mesh和名称标签
**新逻辑**: `deleteZone` 同时删除关联的办公区墙体

**理由**: 删除办公区时应同时删除其墙体

## REMOVED Requirements
无

## 用户问题解答

**用户问题**: 用户先在2D画布拖拽编辑生成办公区，然后点击放置3D对象后办公区自动生成墙体，如果用户再点击创建平面仓库后，对办公区形状进行调整编辑之后，再点击回到3D画布，办公区墙体是否会自动调整？类似这样切换调整的情况，会不会有什么问题？

**答案**: 
- **会**自动调整。原因如下：
  1. `createZonesIn3D` 函数每次被调用时都会先执行 `zones = []` 清空数组
  2. 同时会清除所有zone.mesh（办公区地面）
  3. 我们需要扩展 `clearAllZones` 函数，同时清除办公区墙体（通过userData.type === 'officeWall'识别）
  4. 然后重新根据新的zone.points生成墙体

- **潜在问题及解决方案**:
  1. **门/窗位置**: 重建后原门/窗位置可能不匹配新形状
     - 方案：保存门/窗相对于墙体的比例位置，重建时重新计算
  2. **墙体闪烁**: 清除和重建之间可能有视觉闪烁
     - 方案：这是正常行为，与仓库重建机制一致
  3. **性能**: 频繁切换可能导致重复计算
     - 方案：当前机制已足够，zones数据量通常很小
