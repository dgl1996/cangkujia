# Tasks

## 阶段一：ThreeScene.vue 中立柱创建功能
- [x] Task 1: 创建 `createPillar` 函数
  - [x] 使用 BoxGeometry 创建立柱几何体 (20cm x height x 30cm)
  - [x] 使用与墙体相同的材质参数
  - [x] 设置正确的位置 (Y = baseHeight + height/2)
  - [x] 设置 userData (type, modelType, name)
  - [x] 添加到 scene 和 sceneObjects
  - [x] 自检验证：函数能正确创建立柱

- [x] Task 2: 在 `onDrop` 函数中处理立柱拖拽放置
  - [x] 检测 `objectType === 'pillar'`
  - [x] 调用 `createPillar` 在释放位置创建立柱
  - [x] 自检验证：拖拽能正确放置立柱

- [x] Task 3: expose `createPillar` 函数
  - [x] 自检验证：函数能被外部调用

## 阶段二：CoreFunction.vue 中菜单和批量复制
- [x] Task 4: 新增 `onPillarDragStart` 函数
  - [x] 设置 `objectType = 'pillar'`
  - [x] 设置拖拽图像
  - [x] 自检验证：拖拽数据正确

- [x] Task 5: 在仓库设施菜单中添加立柱选项
  - [x] 添加 "🏛️ 立柱 (20×30cm)" 菜单项
  - [x] 绑定 `onPillarDragStart` 事件
  - [x] 自检验证：菜单显示正确

- [x] Task 6: 修改 `isSelectedObjectShelf` 计算属性
  - [x] 添加立柱类型判断 `type === 'pillar'`
  - [x] 自检验证：选中立柱时批量复制面板显示

- [x] Task 7: expose `onPillarDragStart` 函数
  - [x] 自检验证：函数能被模板调用

## 阶段三：整体自检验证
- [x] Task 8: 功能联调测试
  - [x] 从菜单拖拽立柱到场景
  - [x] 验证立柱尺寸、材质、位置正确
  - [x] 验证批量复制功能可用
  - [x] 验证保存/加载功能正常

# Task Dependencies
- Task 1 → Task 2 → Task 3 (ThreeScene.vue 内部依赖)
- Task 4 → Task 5 → Task 7 (CoreFunction.vue 内部依赖)
- Task 3 和 Task 7 完成后才能进行 Task 8
- Task 6 可以并行于 Task 4-7
