# Tasks

- [x] Task 1: 添加网格常量定义
  - [x] SubTask 1.1: 在 ThreeScene.vue 顶部添加 GRID_CELL_SIZE、GRID_TOTAL_SIZE、GRID_DIVISIONS 常量
  - [x] SubTask 1.2: 验证常量值正确（100cm、10000cm、100）

- [x] Task 2: 修改矩形仓库网格生成
  - [x] SubTask 2.1: 修改 `createWarehouse()` 函数（Line 4415-4417），使用固定网格参数
  - [x] SubTask 2.2: 修改 `createWarehouse()` 中的网格辅助线更新（Line 4490-4494），使用固定网格参数
  - [x] SubTask 2.3: 确保网格中心与仓库中心对齐

- [x] Task 3: 修改多边形仓库网格生成
  - [x] SubTask 3.1: 修改 `createWarehouseFromShape()` 函数（Line 4548-4561），使用固定网格参数
  - [x] SubTask 3.2: 修改 `createWarehouseFromShape()` 中的网格辅助线更新（Line 4626-4632），使用固定网格参数
  - [x] SubTask 3.3: 确保网格中心与仓库中心对齐

- [x] Task 4: 添加坐标轴刻度
  - [x] SubTask 4.1: 修改 `createDirectionLabels()` 函数，添加每1米的刻度标记
  - [x] SubTask 4.2: 添加每10米的刻度标签（"10m", "20m"...）
  - [x] SubTask 4.3: 修改 `updateDirectionLabels()` 函数，同样添加刻度标记和标签

- [x] Task 5: 验证修复结果
  - [x] SubTask 5.1: 启动开发服务器，打开3D画布
  - [x] SubTask 5.2: 创建小仓库（10m×10m），验证网格单元格为1米
  - [x] SubTask 5.3: 创建大仓库（80m×80m），验证网格单元格仍为1米
  - [x] SubTask 5.4: 使用测量工具测量网格边长，验证显示1.00米
  - [x] SubTask 5.5: 验证坐标轴刻度每1米有标记，每10米有标签

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 1
- Task 4 depends on Task 1
- Task 5 depends on Task 2, Task 3, Task 4
