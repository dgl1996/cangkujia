# Tasks

## Task 1: 生成带白线标记的货架模型
**描述**: 修改货架模型生成脚本，在操作横梁中央添加10cm粗白线标记
- [ ] SubTask 1.1: 分析现有generate_all_shelves.py脚本结构
- [ ] SubTask 1.2: 在货架生成逻辑中添加白线标记功能
- [ ] SubTask 1.3: 单组货架：在操作横梁中央添加白线
- [ ] SubTask 1.4: 配组货架：只在第一组添加白线
- [ ] SubTask 1.5: 运行脚本生成40个新模型文件
- [ ] SubTask 1.6: 验证白线标记显示效果

## Task 2: 更新模型元数据
**描述**: 更新shelf-models-metadata.json，添加operationDirection字段
- [ ] SubTask 2.1: 读取现有元数据文件
- [ ] SubTask 2.2: 为每个货架模型添加operationDirection字段（默认+Z）
- [ ] SubTask 2.3: 验证元数据格式正确性

## Task 3: 修改批量复制弹窗UI
**描述**: 修改BatchCopyPanel.vue，添加方向选择UI
- [ ] SubTask 3.1: 移除旋转角度输入框
- [ ] SubTask 3.2: 添加行延伸方向选择器（向前/向后/向左/向右）
- [ ] SubTask 3.3: 添加列延伸方向选择器（向前/向后/向左/向右）
- [ ] SubTask 3.4: 设置默认值：行-向前，列-向左
- [ ] SubTask 3.5: 添加方向图例说明
- [ ] SubTask 3.6: 验证UI布局正确

## Task 4: 实现方向选择逻辑
**描述**: 修改ThreeScene.vue，实现相对方向计算
- [ ] SubTask 4.1: 分析现有批量复制算法
- [ ] SubTask 4.2: 实现"前/后/左/右"到坐标偏移的转换函数
- [ ] SubTask 4.3: 考虑货架当前旋转角度计算实际方向
- [ ] SubTask 4.4: 修改预览生成逻辑，使用新方向计算
- [ ] SubTask 4.5: 修改正式生成逻辑，使用新方向计算
- [ ] SubTask 4.6: 验证方向计算正确性

## Task 5: 测试验证
**描述**: 完整测试批量复制方向选择功能
- [ ] SubTask 5.1: 测试单组货架不同方向组合
- [ ] SubTask 5.2: 测试配组货架方向正确性
- [ ] SubTask 5.3: 测试旋转后的货架方向计算
- [ ] SubTask 5.4: 测试预览功能正常
- [ ] SubTask 5.5: 测试生成后对象位置正确

# Task Dependencies
- Task 2 depends on Task 1
- Task 4 depends on Task 3
- Task 5 depends on Task 2 and Task 4
