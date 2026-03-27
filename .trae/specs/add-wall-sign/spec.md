# 外墙标语功能 Spec

## Why
用户需要在仓库外墙上展示标识信息，如公司名称、收货口/发货口标识等。这是一个贴在墙体上的文字标签，支持自定义内容和样式。

## What Changes
- 在仓库设施菜单添加"外墙标语"拖拽项
- 实现标语放置到外墙的功能
- 实现标语编辑（文字内容、字体大小、颜色）
- 实现标语移动和删除
- 标语固定在墙面，不随相机转动

## Impact
- **Affected files**:
  - `frontend/src/views/CoreFunction.vue` - 菜单添加、拖拽处理
  - `frontend/src/components/3d/ThreeScene.vue` - 标语创建、编辑、渲染
- **Risk level**: 中（新增对象类型，需与现有墙体系统兼容）

## ADDED Requirements

### Requirement: 外墙标语对象
The system SHALL provide a wall sign object that can be placed on warehouse walls.

#### Scenario: 拖拽放置标语
- **WHEN** 用户从仓库设施菜单拖拽"外墙标语"到外墙上
- **THEN** 标语对象创建并吸附到最近的墙体表面
- **AND** 默认显示文字"外墙标语"
- **AND** 默认字体大小24px，白色文字，蓝色背景

#### Scenario: 编辑标语
- **WHEN** 用户选中标语对象并点击"编辑标语"按钮
- **THEN** 弹出编辑对话框
- **AND** 支持修改：文字内容、字体大小、字体颜色、背景颜色
- **AND** 实时预览修改效果
- **AND** 点击确认后保存修改

#### Scenario: 移动标语
- **WHEN** 用户点击"移动"按钮
- **THEN** 进入移动模式
- **AND** 标语只能在墙体表面移动（沿墙面滑动）
- **AND** 不能离开墙体

#### Scenario: 删除标语
- **WHEN** 用户点击"删除"按钮
- **THEN** 标语对象从场景中移除

### Requirement: 标语属性
The system SHALL support the following sign properties:

| 属性 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| 文字内容 | "外墙标语" | 任意文本 | 支持中英文 |
| 字体大小 | 24px | 12px - 72px | 像素单位 |
| 字体颜色 | #FFFFFF | 任意颜色 | 白色 |
| 背景颜色 | #0066CC | 任意颜色 | 蓝色 |
| 宽度 | 自适应 | 根据文字自动计算 | - |
| 高度 | 自适应 | 根据文字自动计算 | - |

### Requirement: 保存与加载
The system SHALL save and load wall signs with projects.

#### Scenario: 保存项目
- **WHEN** 用户保存项目
- **THEN** 所有外墙标语的位置、文字内容、样式属性被保存

#### Scenario: 加载项目
- **WHEN** 用户导入项目
- **THEN** 外墙标语按保存时的状态恢复显示

## MODIFIED Requirements
无

## REMOVED Requirements
无

## Implementation Notes

### 技术方案
使用 Canvas 生成文字纹理，创建 PlaneGeometry 贴到墙面上。

### 数据结构
```javascript
{
  type: 'wallSign',
  text: '外墙标语',
  fontSize: 24,
  textColor: '#FFFFFF',
  bgColor: '#0066CC',
  wallType: 'front', // front/back/left/right
  position: { x, y, z }
}
```

### 修改点清单
1. **CoreFunction.vue**: 在仓库设施菜单添加"外墙标语"拖拽项
2. **CoreFunction.vue**: 添加拖拽开始处理函数
3. **ThreeScene.vue**: 添加 `onDrop` 处理标语类型
4. **ThreeScene.vue**: 添加 `createWallSign()` 函数
5. **ThreeScene.vue**: 添加 `updateWallSign()` 函数
6. **ThreeScene.vue**: 添加 `moveWallSign()` 函数（限制在墙面移动）
7. **CoreFunction.vue**: 右侧面板添加标语编辑UI
8. **ThreeScene.vue**: 添加 `getSceneObjects()` 支持标语保存
9. **ThreeScene.vue**: 添加导入时恢复标语逻辑
