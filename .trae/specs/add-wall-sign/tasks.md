# Tasks

- [x] Task 1: 菜单添加外墙标语拖拽项
  - [x] SubTask 1.1: 在 CoreFunction.vue 仓库设施菜单添加"🏷️ 外墙标语"项
  - [x] SubTask 1.2: 添加 `onWallSignDragStart()` 拖拽开始处理函数
  - [x] SubTask 1.3: 在 ThreeScene.vue `onDrop()` 添加标语类型处理

- [x] Task 2: 实现标语创建功能
  - [x] SubTask 2.1: 在 ThreeScene.vue 添加 `createWallSign(position, wallType)` 函数
  - [x] SubTask 2.2: 使用 Canvas 生成文字纹理
  - [x] SubTask 2.3: 创建 PlaneGeometry 并贴到指定墙面
  - [x] SubTask 2.4: 设置默认样式（文字"外墙标语"、24px、白字蓝底）

- [x] Task 3: 实现标语编辑功能
  - [x] SubTask 3.1: 在 CoreFunction.vue 右侧面板添加"编辑标语"按钮
  - [x] SubTask 3.2: 创建编辑对话框（文字、字体大小、文字颜色、背景颜色）
  - [x] SubTask 3.3: 在 ThreeScene.vue 添加 `updateWallSign(sign, config)` 函数
  - [x] SubTask 3.4: 实现实时预览和确认保存

- [x] Task 4: 实现标语移动功能
  - [x] SubTask 4.1: 在 CoreFunction.vue 右侧面板添加"移动"按钮
  - [x] SubTask 4.2: 在 ThreeScene.vue 实现 `moveWallSign()` 限制在墙面移动
  - [x] SubTask 4.3: 确保移动时标语始终贴合墙面

- [x] Task 5: 实现标语删除功能
  - [x] SubTask 5.1: 在 CoreFunction.vue 右侧面板添加"删除"按钮
  - [x] SubTask 5.2: 在 ThreeScene.vue 实现标语删除逻辑

- [x] Task 6: 实现保存与加载
  - [x] SubTask 6.1: 修改 `getSceneObjects()` 包含标语对象
  - [x] SubTask 6.2: 修改保存逻辑，导出标语数据
  - [x] SubTask 6.3: 修改导入逻辑，恢复标语显示

- [x] Task 7: 自检验证
  - [x] SubTask 7.1: 测试拖拽放置标语到各面墙
  - [x] SubTask 7.2: 测试编辑标语内容和样式
  - [x] SubTask 7.3: 测试移动标语（限制在墙面）
  - [x] SubTask 7.4: 测试删除标语
  - [x] SubTask 7.5: 测试保存/加载项目包含标语
  - [x] SubTask 7.6: 验证不影响现有功能（门/窗/立柱等）

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 2
- Task 5 depends on Task 2
- Task 6 depends on Task 2
- Task 7 depends on Task 3, 4, 5, 6
