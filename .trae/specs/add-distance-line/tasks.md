# Tasks

## Phase 1: UI组件开发

- [ ] Task 1: 添加工具栏按钮
  - [ ] SubTask 1.1: 在 CoreFunction.vue 工具栏添加"+距离线"按钮
  - [ ] SubTask 1.2: 添加按钮图标和样式
  - [ ] SubTask 1.3: 实现按钮点击事件，调用 startDistanceLineMode
  - [ ] SubTask 1.4: 添加按钮状态管理（激活/非激活）

- [ ] Task 2: 创建距离输入弹窗
  - [ ] SubTask 2.1: 在 CoreFunction.vue 添加距离输入弹窗模板
  - [ ] SubTask 2.2: 添加距离输入变量（ref）
  - [ ] SubTask 2.3: 实现弹窗显示/隐藏逻辑
  - [ ] SubTask 2.4: 添加输入验证（0.1-100米）
  - [Task 2.5: 实现确认/取消按钮事件

## Phase 2: ThreeScene 核心逻辑开发

- [ ] Task 3: 实现距离线模式状态管理
  - [ ] SubTask 3.1: 添加状态变量（isDistanceLineMode, distanceLineStartPoint 等）
  - [ ] SubTask 3.2: 实现 startDistanceLineMode 函数
  - [ ] SubTask 3.3: 实现 stopDistanceLineMode 函数
  - [ ] SubTask 3.4: 实现 ESC 键取消功能

- [ ] Task 4: 实现起点选择和距离输入
  - [ ] SubTask 4.1: 在 onClick 中添加距离线模式判断
  - [ ] SubTask 4.2: 实现起点选择逻辑（射线检测地面）
  - [ ] SubTask 4.3: 调用弹窗显示距离输入
  - [ ] SubTask 4.4: 接收弹窗返回的距离值

- [ ] Task 5: 实现距离线预览
  - [ ] SubTask 5.1: 实现 createDistanceLinePreview 函数
  - [ ] SubTask 5.2: 在 onMouseMove 中添加预览更新逻辑
  - [ ] SubTask 5.3: 计算预览线终点（起点 + 方向 * 距离）
  - [ ] SubTask 5.4: 使用虚线或不同颜色区分预览线

- [ ] Task 6: 实现终点确定和距离线创建
  - [ ] SubTask 6.1: 在 onClick 中处理预览模式下的点击
  - [ ] SubTask 6.2: 实现 confirmDistanceLine 函数
  - [ ] SubTask 6.3: 创建固定距离线（实线）
  - [ ] SubTask 6.4: 创建距离标签（Sprite 或 Canvas）
  - [ ] SubTask 6.5: 启动10秒倒计时

- [ ] Task 7: 实现距离线管理和清理
  - [ ] SubTask 7.1: 创建 distanceLines 数组存储多个距离线
  - [ ] SubTask 7.2: 实现 clearDistanceLine(id) 函数
  - [ ] SubTask 7.3: 实现 cleanupExpiredDistanceLines 函数
  - [ ] SubTask 7.4: 使用 setInterval 定期清理超时距离线

## Phase 3: 集成与测试

- [ ] Task 8: 组件集成
  - [ ] SubTask 8.1: 在 CoreFunction.vue 中暴露 startDistanceLineMode 给 ThreeScene
  - [ ] SubTask 8.2: 在 ThreeScene.vue 中调用弹窗显示
  - [ ] SubTask 8.3: 确保模式互斥（距离线模式 vs 测量模式 vs 对齐线模式）

- [ ] Task 9: 自检验证
  - [ ] SubTask 9.1: 验证工具栏按钮正常显示和点击
  - [ ] SubTask 9.2: 验证距离输入弹窗正常显示和输入
  - [ ] SubTask 9.3: 验证起点选择正常工作
  - [ ] SubTask 9.4: 验证距离线预览随鼠标方向变化
  - [ ] SubTask 9.5: 验证终点确定后距离线固定显示
  - [ ] SubTask 9.6: 验证距离标签正确显示
  - [ ] SubTask 9.7: 验证10秒后距离线自动消失
  - [ ] SubTask 9.8: 验证多个距离线同时存在
  - [ ] SubTask 9.9: 验证ESC键取消功能
  - [ ] SubTask 9.10: 验证不影响测量工具功能
  - [ ] SubTask 9.11: 验证不影响对齐线功能

## Phase 4: 汇报与验收

- [ ] Task 10: 准备验收报告
  - [ ] SubTask 10.1: 整理修改的代码清单
  - [ ] SubTask 10.2: 整理测试验证结果
  - [ ] SubTask 10.3: 编写用户使用说明

# Task Dependencies

```
Phase 1:
  Task 1 ──→ Task 2 ──┐
                     │
Phase 2:             ↓
  Task 3 ──→ Task 4 ──→ Task 5 ──→ Task 6 ──→ Task 7
                     │
Phase 3:             ↓
  Task 8 ──→ Task 9 ──┘
                     │
Phase 4:             ↓
                   Task 10
```

Task 3 需要在 Task 1-2 完成后开始（需要UI触发）。
Task 4-7 是核心逻辑，按顺序依赖。
Task 8 是集成，需要在UI和核心逻辑都完成后开始。
