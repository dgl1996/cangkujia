# 首页重新设计规格文档

## Why
提升品牌形象，让用户直观了解产品价值，优化首页信息结构和视觉呈现。

## What Changes
- 更新 LOGO 为商标版本（仓酷家logo.png），并放大尺寸
- Hero 区域嵌入 3D 仓库效果图背景，移除"查看案例"按钮
- 重新排序功能特点卡片，替换"平面图导入"为"专业级3D效果图演示"
- 删除"优秀案例展示"整个区块
- 修改产品故事文案
- CTA 区域更换背景色、LOGO，增加 ICP 备案号

## Impact
- 受影响文件：frontend/src/views/HomePage.vue
- 需要新增图片资源：仓酷家logo.png、仓酷家首页背景图.jpg

## ADDED Requirements

### Requirement: 新 LOGO 使用
The system SHALL 使用新的商标版 LOGO（仓酷家logo.png）替换现有的 LOGO.png

#### Scenario: 导航栏 LOGO
- **WHEN** 页面加载
- **THEN** 导航栏显示新的仓酷家logo.png，尺寸适当放大

#### Scenario: 页脚 LOGO
- **WHEN** 页面滚动到页脚
- **THEN** 页脚显示新的仓酷家logo.png

#### Scenario: CTA 区域 LOGO
- **WHEN** 页面显示 CTA 区域
- **THEN** CTA 区域显示新的仓酷家logo.png

### Requirement: Hero 区域背景图
The system SHALL 在 Hero 区域嵌入仓酷家首页背景图.jpg 作为背景

#### Scenario: 背景图展示
- **WHEN** 用户访问首页
- **THEN** Hero 区域显示 3D 仓库效果图作为背景
- **AND** 背景图应覆盖整个 Hero 区域
- **AND** 文字内容应清晰可见（可能需要遮罩或调整文字颜色）

### Requirement: 移除"查看案例"按钮
The system SHALL 从 Hero 区域移除"查看案例"按钮

#### Scenario: 按钮移除
- **WHEN** 页面加载
- **THEN** Hero 区域只保留"免费开始使用"按钮
- **AND** "查看案例"按钮不再显示

### Requirement: 功能特点重新排序
The system SHALL 按照新顺序显示功能特点卡片

#### Scenario: 新顺序展示
- **WHEN** 页面显示功能特点区域
- **THEN** 卡片按以下顺序显示：
  1. 丰富模型库
  2. 3D可视化设计
  3. 标准案例库
  4. 快速出图
  5. 专业级3D效果图演示（替换原"平面图导入"）
  6. 项目实施清单

### Requirement: 删除案例展示区块
The system SHALL 完全删除"优秀案例展示"区块

#### Scenario: 区块移除
- **WHEN** 页面加载
- **THEN** "优秀案例展示"区块不再显示
- **AND" 导航栏中的"案例展示"链接也应相应调整或移除

### Requirement: 产品故事文案修改
The system SHALL 修改产品故事区域的文案

#### Scenario: 文案更新
- **WHEN** 页面显示产品故事区域
- **THEN** "相信我，这就是你需要的极致效率工具！"改为"相信我，这就是你需要的无门槛物流仓库规划傻瓜式3D工具！"

### Requirement: CTA 区域样式更新
The system SHALL 更新 CTA 区域的视觉样式

#### Scenario: 背景色更换
- **WHEN** 页面显示 CTA 区域
- **THEN** 背景色改为设计工作台的背景色（需要确认具体颜色值）

#### Scenario: LOGO 更换
- **WHEN** 页面显示 CTA 区域
- **THEN** 显示新的仓酷家logo.png

#### Scenario: ICP 备案号
- **WHEN** 页面显示 CTA 区域
- **THEN** 显示"沪ICP备2026013469号"备案信息

## MODIFIED Requirements
无

## REMOVED Requirements
无
