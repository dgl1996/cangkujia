# Tasks

- [ ] Task 1: 修改移动模式基础逻辑
  - [ ] SubTask 1.1: 在ThreeScene.vue中添加移动模式状态变量（isMoveMode, originalPosition）
  - [ ] SubTask 1.2: 修改【移动】按钮点击处理，进入移动模式
  - [ ] SubTask 1.3: 实现对象半透明和抬高视觉效果
  - [ ] SubTask 1.4: 实现鼠标跟随逻辑（mousemove事件监听）
  - [ ] SubTask 1.5: 实现点击确认放置逻辑
  - [ ] SubTask 1.6: 实现ESC取消移动逻辑

- [ ] Task 2: 集成对齐线吸附功能
  - [ ] SubTask 2.1: 复用现有吸附计算逻辑（handleBoundarySnap）
  - [ ] SubTask 2.2: 在鼠标移动时检测对齐线距离
  - [ ] SubTask 2.3: 实现吸附时对象"跳"到对齐线位置
  - [ ] SubTask 2.4: 实现吸附时对齐线变绿高亮
  - [ ] SubTask 2.5: 实现远离时恢复原始颜色

- [ ] Task 3: 状态管理和事件处理
  - [ ] SubTask 3.1: 禁用OrbitControls在移动模式下的左键旋转（保留右键）
  - [ ] SubTask 3.2: 确保移动模式下其他操作按钮禁用
  - [ ] SubTask 3.3: 添加移动模式提示UI（如"移动模式：点击放置，ESC取消"）

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 1
