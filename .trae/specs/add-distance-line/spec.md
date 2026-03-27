# 距离线功能 Spec

## Why
用户需要精确定位距离某点特定长度的位置（如从货架底部1.5米处），现有测量工具只能显示两点距离，无法根据输入距离自动延伸并标记目标点。距离线功能允许用户输入精确距离，实时预览目标位置，并在确定后临时显示距离标记。

## What Changes
- 在项目工具栏添加"+距离线"按钮
- 实现距离线绘制模式（类似测量工具）
- 添加距离输入弹窗
- 实现距离线预览（随鼠标方向动态延伸）
- 实现距离线固定显示（10秒后自动消失）
- 支持多个距离线同时存在
- **限制在仓库地面水平面内（Y=0）**
- **不保存到项目，仅临时显示**

## Impact
- **Affected files**:
  - `frontend/src/views/CoreFunction.vue` - 工具栏按钮、距离输入弹窗
  - `frontend/src/components/3d/ThreeScene.vue` - 距离线绘制逻辑、预览、显示
- **Risk level**: 低（参考现有测量工具实现，逻辑相似）
- **受影响的功能**: 无（新增功能，不影响现有功能）

## ADDED Requirements

### Requirement: 距离线工具按钮
The system SHALL provide a "+距离线" button in the project toolbar.

#### Scenario: 进入距离线模式
- **WHEN** 用户点击"+距离线"按钮
- **THEN** 进入距离线绘制模式
- **AND** 鼠标变为十字准星
- **AND** 提示用户"点击起点，输入距离"

### Requirement: 起点选择
The system SHALL allow user to select start point by clicking on the 3D canvas.

#### Scenario: 选择起点
- **WHEN** 用户在3D画布中点击
- **AND** 射线与地面平面相交
- **THEN** 记录起点坐标（Y=0）
- **AND** 弹出距离输入弹窗

### Requirement: 距离输入弹窗
The system SHALL show a modal dialog for user to input distance value.

#### Scenario: 输入距离
- **WHEN** 起点选择后
- **THEN** 显示弹窗，包含：
  - 距离输入框（单位：米，支持小数）
  - 确认按钮
  - 取消按钮
- **AND** 输入范围：0.1米 - 100米
- **WHEN** 用户点击确认
- **THEN** 关闭弹窗，进入终点预览模式
- **WHEN** 用户点击取消
- **THEN** 退出距离线模式

### Requirement: 距离线预览
The system SHALL display a preview line that extends from start point with the input distance, following mouse direction.

#### Scenario: 预览距离线
- **WHEN** 距离输入确认后
- **THEN** 从起点显示一条预览线
- **AND** 线的长度固定为输入距离
- **AND** 线的方向跟随鼠标方向（以起点为中心）
- **AND** 线显示在地面水平面（Y=0.2cm，避免z-fighting）
- **AND** 实时显示终点位置

### Requirement: 终点确定
The system SHALL allow user to confirm end point by clicking.

#### Scenario: 确定终点
- **WHEN** 用户在预览模式下点击
- **THEN** 固定距离线终点位置
- **AND** 在距离线上方显示距离标签（如"1.5米"）
- **AND** 距离线固定显示10秒
- **AND** 10秒后自动清除
- **AND** 退出距离线模式

### Requirement: 多个距离线支持
The system SHALL support multiple distance lines existing simultaneously.

#### Scenario: 多个距离线
- **WHEN** 用户完成一个距离线
- **THEN** 该距离线进入10秒倒计时
- **AND** 用户可以立即开始绘制新的距离线
- **AND** 多个距离线独立计时，各自10秒后消失

### Requirement: ESC取消
The system SHALL allow user to cancel distance line mode by pressing ESC.

#### Scenario: ESC取消
- **WHEN** 用户在距离线模式下按ESC
- **THEN** 清除当前预览
- **AND** 退出距离线模式

## MODIFIED Requirements
无

## REMOVED Requirements
无

## Implementation Notes

### 技术方案
参考现有测量工具（`isMeasuring`）的实现：
1. 状态变量：`isDistanceLineMode`, `distanceLineStartPoint`, `distanceLinePreview`, `distanceValue`
2. 鼠标点击处理：在 `onClick` 中添加距离线模式判断
3. 鼠标移动处理：在 `onMouseMove` 中添加预览更新
4. 弹窗组件：参考立柱高度编辑弹窗

### 数据结构
```javascript
// 距离线对象
{
  id: number,
  startPoint: Vector3,
  endPoint: Vector3,
  distance: number, // 米
  line: Line,
  label: Sprite, // 距离标签
  createdAt: timestamp
}
```

### 关键函数
1. `startDistanceLineMode()` - 进入距离线模式
2. `stopDistanceLineMode()` - 退出距离线模式
3. `showDistanceInputDialog()` - 显示距离输入弹窗
4. `createDistanceLinePreview()` - 创建预览线
5. `updateDistanceLinePreview()` - 更新预览线方向
6. `confirmDistanceLine()` - 确认终点，创建固定距离线
7. `clearDistanceLine(id)` - 清除指定距离线
8. `cleanupExpiredDistanceLines()` - 清理超时的距离线

### 避坑指南
- **不要** 修改测量工具相关代码
- **不要** 修改对齐线相关代码
- **不要** 修改保存/加载逻辑（距离线不保存）
- **确保** 距离线显示在地面之上（Y>0），避免z-fighting
- **确保** 预览线使用虚线或不同颜色，与固定线区分
- **确保** 10秒倒计时准确，及时清理避免内存泄漏
