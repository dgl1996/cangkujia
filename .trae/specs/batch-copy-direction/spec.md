# 批量复制方向选择功能 Spec

## Why
当前批量复制功能生成的货架对象方向由后台自动决定，可能与用户期望不符。用户需要在批量复制前能够预览并控制复制对象的排列方向。

## What Changes
- **新增**: 40个货架模型添加操作方向白线标记
- **新增**: 批量复制弹窗增加"排列方向"选择（前/后/左/右）
- **修改**: 批量复制算法支持相对方向计算
- **新增**: 模型元数据添加operationDirection字段

## Impact
- 影响文件:
  - `scripts/generate_all_shelves.py` - 货架模型生成脚本
  - `frontend/public/assets/shelf-models-metadata.json` - 模型元数据
  - `frontend/src/components/BatchCopyPanel.vue` - 批量复制弹窗
  - `frontend/src/components/ThreeScene.vue` - 批量复制逻辑
- 用户体验: 批量复制前可预览方向，提高操作准确性

## ADDED Requirements

### Requirement: 货架模型操作方向标记
The system SHALL provide visual indication of shelf operation direction.

#### Scenario: 单组货架标记
- **GIVEN** 单组货架模型
- **WHEN** 生成GLB模型时
- **THEN** 在操作横梁中央添加10cm粗白线标记
- **AND** 白线方向定义为"前"方向

#### Scenario: 配组货架标记
- **GIVEN** 配组货架模型（背靠背两组）
- **WHEN** 生成GLB模型时
- **THEN** 只在第一组货架的操作横梁添加白线标记
- **AND** 第二组不添加标记

### Requirement: 批量复制方向选择
The system SHALL allow users to select batch copy arrangement direction.

#### Scenario: 方向选择UI
- **GIVEN** 用户打开批量复制弹窗
- **WHEN** 弹窗显示时
- **THEN** 显示"排列方向"选择区域
- **AND** 包含两个选择器：行延伸方向、列延伸方向
- **AND** 选项为：向前/向后/向左/向右
- **AND** 默认值：行-向前，列-向左

#### Scenario: 方向预览
- **GIVEN** 用户设置行列数和方向
- **WHEN** 点击"预览"按钮
- **THEN** 生成半透明预览对象
- **AND** 预览对象按照选择的方向排列
- **AND** 预览跟随鼠标移动

#### Scenario: 方向计算逻辑
- **GIVEN** 货架当前有旋转角度
- **WHEN** 用户选择"向前延伸"
- **THEN** 新对象沿货架"前"方向（白线方向）排列
- **AND** 计算时考虑货架当前旋转角度

### Requirement: 模型元数据扩展
The system SHALL store operation direction in model metadata.

#### Scenario: 元数据格式
- **GIVEN** 货架模型元数据
- **THEN** 包含operationDirection字段
- **AND** 值为：+X/-X/+Z/-Z之一
- **AND** 默认值为+Z（白线朝+Z方向）

## MODIFIED Requirements

### Requirement: 批量复制弹窗布局
**原布局**: 行数、列数、行间距、列间距、旋转角度
**新布局**: 行数、列数、行间距、列间距、排列方向（行/列）
**说明**: 移除旋转角度设置，移至单独旋转功能

### Requirement: 新对象默认方向
**原行为**: 新放置货架无明确默认方向
**新行为**: 新放置货架默认白线（前）朝+Z方向
**说明**: 确保默认状态下方向一致性

## REMOVED Requirements

### Requirement: 批量复制旋转角度设置
**Reason**: 功能边界划分，旋转功能由单独旋转按钮负责
**Migration**: 使用单独的旋转按钮进行精确角度调整
