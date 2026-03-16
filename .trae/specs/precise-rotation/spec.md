# 精确旋转角度输入功能 Spec

## Why
当前旋转功能采用手动拖动方式，旋转角度不精确。用户需要能够输入精确角度值来控制对象旋转，特别是货架对象需要与仓库布局对齐。

## What Changes
- **新增**: 旋转角度输入对话框组件
- **修改**: 旋转按钮触发角度输入对话框（替代手动拖动）
- **新增**: 实时旋转预览功能
- **新增**: 以货架白线方向为0°基准的旋转逻辑

## Impact
- 影响文件:
  - `frontend/src/views/CoreFunction.vue` - 添加旋转对话框和旋转逻辑
  - `frontend/src/components/3d/ThreeScene.vue` - 实现3D对象旋转方法
- 用户体验: 旋转操作更精确，支持角度输入和实时预览

## ADDED Requirements

### Requirement: 旋转角度输入对话框
The system SHALL provide a dialog for precise rotation angle input.

#### Scenario: 对话框显示
- **GIVEN** 用户选中一个3D对象
- **WHEN** 用户点击"旋转"按钮
- **THEN** 弹出旋转角度输入对话框
- **AND** 对话框包含角度输入框（支持负数）
- **AND** 显示当前旋转角度
- **AND** 有"确认"和"取消"按钮

#### Scenario: 角度输入范围
- **GIVEN** 旋转角度输入框
- **WHEN** 用户输入角度值
- **THEN** 支持 -360° 到 +360° 范围
- **AND** 支持小数（如 45.5°）

### Requirement: 实时旋转预览
The system SHALL provide real-time rotation preview.

#### Scenario: 输入时实时预览
- **GIVEN** 旋转角度输入对话框已打开
- **WHEN** 用户在输入框中输入角度值
- **THEN** 选中的对象实时旋转到对应角度
- **AND** 旋转以白线方向为0°基准
- **AND** 顺时针方向为正角度

#### Scenario: 取消恢复
- **GIVEN** 用户正在预览旋转效果
- **WHEN** 用户点击"取消"按钮
- **THEN** 对象恢复到旋转前的角度

### Requirement: 旋转基准与方向
The system SHALL use shelf operation direction as rotation reference.

#### Scenario: 0°基准
- **GIVEN** 货架对象有白线标记
- **WHEN** 输入角度为 0°
- **THEN** 白线方向朝向 +Z 方向

#### Scenario: 顺时针旋转
- **GIVEN** 货架对象当前角度为 0°
- **WHEN** 输入角度为 90°
- **THEN** 对象顺时针旋转 90°
- **AND** 白线方向朝向 +X 方向

#### Scenario: 逆时针旋转
- **GIVEN** 货架对象当前角度为 0°
- **WHEN** 输入角度为 -90°
- **THEN** 对象逆时针旋转 90°
- **AND** 白线方向朝向 -X 方向

## MODIFIED Requirements

### Requirement: 旋转按钮行为
**原行为**: 点击旋转按钮进入手动拖动旋转模式
**新行为**: 点击旋转按钮弹出角度输入对话框
**说明**: 提供更精确的旋转控制

## REMOVED Requirements

### Requirement: 手动拖动旋转
**Reason**: 替换为精确角度输入方式
**Migration**: 使用角度输入对话框进行旋转
