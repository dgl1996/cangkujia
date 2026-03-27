# Checklist

## 代码实现检查项

- [x] CoreFunction.vue 菜单添加"🏷️ 外墙标语"项
- [x] CoreFunction.vue 添加 `onWallSignDragStart()` 函数
- [x] ThreeScene.vue `onDrop()` 处理 `wallSign` 类型
- [x] ThreeScene.vue 添加 `createWallSign()` 函数
- [x] ThreeScene.vue 使用 Canvas 生成文字纹理
- [x] ThreeScene.vue 标语默认样式正确（文字"外墙标语"、24px、白字蓝底）
- [x] CoreFunction.vue 右侧面板添加"编辑标语"按钮
- [x] CoreFunction.vue 创建标语编辑对话框
- [x] ThreeScene.vue 添加 `updateWallSign()` 函数
- [x] CoreFunction.vue 右侧面板添加"移动"按钮
- [x] ThreeScene.vue 实现标语移动（限制在墙面）
- [x] CoreFunction.vue 右侧面板添加"删除"按钮
- [x] ThreeScene.vue 实现标语删除
- [x] `getSceneObjects()` 包含标语对象
- [x] 保存逻辑导出标语数据
- [x] 导入逻辑恢复标语显示

## 功能验证检查项

- [x] 可以拖拽放置标语到前墙
- [x] 可以拖拽放置标语到后墙
- [x] 可以拖拽放置标语到左墙
- [x] 可以拖拽放置标语到右墙
- [x] 标语默认显示"外墙标语"
- [x] 点击"编辑标语"弹出编辑对话框
- [x] 可以修改文字内容（支持中英文）
- [x] 可以修改字体大小
- [x] 可以修改文字颜色
- [x] 可以修改背景颜色
- [x] 编辑时实时预览效果
- [x] 点击移动按钮可以沿墙面移动
- [x] 移动时标语不离开墙面
- [x] 点击删除按钮可以删除标语
- [x] 保存项目包含标语数据
- [x] 导入项目恢复标语显示
- [x] 标语固定在墙面（不Billboard）
- [x] 不影响门/窗/立柱等其他功能
