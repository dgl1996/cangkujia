# Tasks

## Task 1: 创建旋转角度输入对话框UI
**描述**: 在CoreFunction.vue中添加旋转角度输入对话框
- [ ] SubTask 1.1: 添加对话框显示状态变量
- [ ] SubTask 1.2: 创建对话框模板（角度输入框、确认/取消按钮）
- [ ] SubTask 1.3: 添加对话框样式
- [ ] SubTask 1.4: 实现对话框打开/关闭逻辑

## Task 2: 修改旋转按钮逻辑
**描述**: 修改旋转按钮点击事件，触发角度输入对话框
- [ ] SubTask 2.1: 找到现有旋转按钮处理函数
- [ ] SubTask 2.2: 修改旋转按钮点击逻辑
- [ ] SubTask 2.3: 移除手动拖动旋转相关代码
- [ ] SubTask 2.4: 添加打开旋转对话框的调用

## Task 3: 实现实时旋转预览
**描述**: 在ThreeScene.vue中实现对象实时旋转方法
- [ ] SubTask 3.1: 添加预览旋转方法
- [ ] SubTask 3.2: 实现以白线方向为基准的旋转计算
- [ ] SubTask 3.3: 连接输入框变化事件到预览方法
- [ ] SubTask 3.4: 实现取消时恢复原角度

## Task 4: 实现角度确认应用
**描述**: 实现确认按钮应用旋转角度
- [ ] SubTask 4.1: 添加确认旋转方法
- [ ] SubTask 4.2: 保存旋转后的角度到对象数据
- [ ] SubTask 4.3: 关闭对话框并清理状态

## Task 5: 测试验证
**描述**: 完整测试精确旋转功能
- [ ] SubTask 5.1: 测试0°、90°、180°、270°旋转
- [ ] SubTask 5.2: 测试负角度旋转（-90°）
- [ ] SubTask 5.3: 测试实时预览功能
- [ ] SubTask 5.4: 测试取消恢复功能
- [ ] SubTask 5.5: 测试确认应用功能

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
