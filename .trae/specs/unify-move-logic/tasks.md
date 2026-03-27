# Tasks

## Phase 1: 代码分析与准备

- [x] Task 1: 详细分析现有移动逻辑
  - [x] SubTask 1.1: 阅读并理解 `onMouseMove` 函数的两套移动逻辑
  - [x] SubTask 1.2: 阅读并理解 `moveSelectedObjects` 函数
  - [x] SubTask 1.3: 阅读并理解 `moveWallSign` 函数
  - [x] SubTask 1.4: 绘制现有代码执行流程图
  - [x] SubTask 1.5: 确定需要移除的代码范围（精确到行号）

- [x] Task 2: 设计重构方案
  - [x] SubTask 2.1: 设计新的 `onMouseMove` 移动逻辑流程
  - [x] SubTask 2.2: 设计吸附逻辑整合方案
  - [x] SubTask 2.3: 确定 `moveSelectedObjects` 需要增强的功能点

## Phase 2: 核心重构

- [x] Task 3: 重构 `moveSelectedObjects` 函数
  - [x] SubTask 3.1: 添加吸附检测逻辑到函数开头
  - [x] SubTask 3.2: 确保吸附结果正确影响 delta 计算
  - [x] SubTask 3.3: 添加调试日志验证吸附生效
  - [x] SubTask 3.4: 验证函数对外墙标语的特殊处理仍然有效

- [x] Task 4: 重构 `onMouseMove` 函数
  - [x] SubTask 4.1: 移除第二套直接操作 `position` 的逻辑
  - [x] SubTask 4.2: 保留第一套调用 `moveSelectedObjects` 的逻辑
  - [x] SubTask 4.3: 将吸附检测逻辑从 `onMouseMove` 移到 `moveSelectedObjects`
  - [x] SubTask 4.4: 确保移动模式判断条件正确

- [x] Task 5: 代码清理与优化
  - [x] SubTask 5.1: 移除不再使用的变量和函数
  - [x] SubTask 5.2: 更新注释说明新的逻辑流程
  - [x] SubTask 5.3: 确保代码风格一致

## Phase 3: 自检验证

- [x] Task 6: 单元测试验证
  - [x] SubTask 6.1: 验证普通对象（货架）移动正常
  - [x] SubTask 6.2: 验证外墙标语移动并更新 `offsetAlongWall`
  - [x] SubTask 6.3: 验证对齐线吸附功能正常
  - [x] SubTask 6.4: 验证保存后 `offsetAlongWall` 值正确

- [x] Task 7: 集成测试验证
  - [x] SubTask 7.1: 验证门/窗功能不受影响
  - [x] SubTask 7.2: 验证立柱功能不受影响
  - [x] SubTask 7.3: 验证其他模型功能不受影响
  - [x] SubTask 7.4: 验证批量复制功能不受影响

## Phase 4: 汇报与验收

- [x] Task 8: 准备验收报告
  - [x] SubTask 8.1: 整理修改的代码清单
  - [x] SubTask 8.2: 整理测试验证结果
  - [x] SubTask 8.3: 编写用户使用说明

# Task Dependencies

```
Phase 1:
  Task 1 ──→ Task 2 ──┐
                     │
Phase 2:             ↓
  Task 3 ──┐      ┌──→ Task 5
           ├──→ Task 4
  Task 3 ──┘      └──→ Task 5
                     │
Phase 3:             ↓
  Task 6 ──→ Task 7 ──┘
                     │
Phase 4:             ↓
                   Task 8
```

Task 3 和 Task 4 可以并行开发，但需要协调好接口。
建议先完成 Task 3，再完成 Task 4。
