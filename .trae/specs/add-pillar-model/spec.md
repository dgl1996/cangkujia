# 立柱模型添加 Spec

## Why
用户需要在仓库设施中添加立柱3D模型，用于仓库内部支撑结构的规划。立柱需要与墙体风格一致，并支持批量复制功能以提高规划效率。

## What Changes
- **新增**: 立柱3D模型创建函数
- **新增**: 立柱拖拽放置功能
- **新增**: 仓库设施菜单中立柱选项
- **修改**: 批量复制功能支持立柱对象

## Impact
- 影响文件:
  - `frontend/src/components/3d/ThreeScene.vue` - 立柱创建、拖拽处理
  - `frontend/src/views/CoreFunction.vue` - 菜单、批量复制支持
- 用户体验:
  - 可从仓库设施菜单拖拽放置立柱
  - 立柱风格与墙体一致
  - 支持批量复制功能

## ADDED Requirements

### Requirement: 立柱3D模型创建
The system SHALL 提供立柱3D模型创建功能。

#### Scenario: 创建立柱
- **GIVEN** 用户在3D场景中指定位置
- **WHEN** 调用创建立柱函数
- **THEN** 创建尺寸为20cm×30cm×墙体高度的立柱
- **AND** 使用与墙体相同的材质（颜色0x888888，透明度0.8）
- **AND** 立柱底部对齐地面（Y=baseHeight）

#### Scenario: 立柱属性
- **GIVEN** 立柱已创建
- **THEN** userData包含：
  - type: 'pillar'
  - modelType: 'pillar'
  - name: '立柱'

### Requirement: 立柱拖拽放置
The system SHALL 支持从菜单拖拽放置立柱到3D场景。

#### Scenario: 拖拽放置
- **GIVEN** 用户从仓库设施菜单拖拽立柱
- **WHEN** 释放到3D场景地面
- **THEN** 在释放位置创建立柱
- **AND** 立柱位置对齐到网格

### Requirement: 批量复制支持
The system SHALL 支持对立柱进行批量复制。

#### Scenario: 批量复制立柱
- **GIVEN** 用户选中一个立柱
- **WHEN** 打开批量复制面板
- **THEN** 可以设置行数、列数、间距
- **AND** 生成预览并确认后批量创建

## MODIFIED Requirements

### Requirement: 批量复制对象范围
**原逻辑**: 批量复制仅支持货架、托盘、拣货车
**新逻辑**: 批量复制支持货架、托盘、拣货车、立柱

**修改内容**:
- `isSelectedObjectShelf` 计算属性添加立柱类型判断
- 判断条件: `type === 'pillar'`

## REMOVED Requirements
无
