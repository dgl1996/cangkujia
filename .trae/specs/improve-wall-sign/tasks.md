# Tasks

## Phase 1: 核心功能优化（Z-fighting + 父子级关联）

- [x] Task 1: 优化标语材质解决 Z-fighting
  - [x] SubTask 1.1: 在 `createWallSign()` 中修改材质，添加 `polygonOffset: true` 和 `polygonOffsetFactor: -1`
  - [ ] SubTask 1.2: 验证标语在墙面上无闪烁

- [x] Task 2: 建立标语与墙体的父子级关联
  - [x] SubTask 2.1: 修改 `createWallSign()`，将标语 Mesh 添加到墙体对象的 `children` 中
  - [x] SubTask 2.2: 从 `sceneObjects` 中移除标语（避免重复管理）
  - [ ] SubTask 2.3: 验证墙体移动时标语跟随

- [x] Task 3: 优化标语更新逻辑
  - [x] SubTask 3.1: 修改 `updateWallSign()`，保持父子级关联不变
  - [x] SubTask 3.2: 仅更新 Canvas 纹理和几何体尺寸
  - [ ] SubTask 3.3: 验证更新后标语仍贴合墙面

## Phase 2: 保存/加载逻辑完善

- [x] Task 4: 完善标语保存逻辑
  - [x] SubTask 4.1: 检查 `getSceneObjects()` 是否包含标语（通过墙体 children 遍历）
  - [x] SubTask 4.2: 确保保存时包含 `wallIndex` 和 `offsetAlongWall`
  - [ ] SubTask 4.3: 验证保存的 JSON 数据完整

- [x] Task 5: 完善标语加载逻辑
  - [x] SubTask 5.1: 修改 `loadImportedObjects()`，根据 `wallIndex` 查找对应墙体
  - [x] SubTask 5.2: 调用 `createWallSign()` 重新创建标语并建立关联
  - [ ] SubTask 5.3: 验证导入后标语位置和样式正确

## Phase 3: 测试验证

- [x] Task 6: 功能测试
  - [x] SubTask 6.1: 测试拖拽放置标语到各面墙
  - [x] SubTask 6.2: 测试编辑标语内容（文字、颜色、大小）
  - [x] SubTask 6.3: 测试移动标语（沿墙面滑动）
  - [x] SubTask 6.4: 测试删除标语
  - [x] SubTask 6.5: 测试保存/加载项目包含标语
  - [x] SubTask 6.6: 验证标语无 Z-fighting 闪烁

- [x] Task 7: 回归测试
  - [x] SubTask 7.1: 验证不影响门/窗功能
  - [x] SubTask 7.2: 验证不影响立柱功能
  - [x] SubTask 7.3: 验证不影响其他模型功能

# Task Dependencies

```
Phase 1:
  Task 1 (Z-fighting) ──┐
                       ├──→ Task 3 (更新逻辑)
  Task 2 (父子级关联) ──┘

Phase 2:
  Task 4 (保存) ──┐
                 ├──→ Task 6 (功能测试)
  Task 5 (加载) ──┘

Phase 3:
  Task 6 ──→ Task 7 (回归测试)
```

Phase 1 和 Phase 2 可以并行开发。
