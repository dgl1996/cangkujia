# Tasks

- [x] Task 1: 修改 `clearAllZones` 函数，添加办公区墙体清理逻辑
  - [x] 在清理zone.mesh时，同时清理userData.type === 'officeWall'的墙体
  - [x] 确保所有关联的办公区墙体都被正确移除

- [x] Task 2: 修改 `deleteZone` 函数，添加单个办公区墙体清理
  - [x] 删除区域时，同时删除关联的办公区墙体（通过zoneId匹配）
  - [x] 同时删除关联的门/窗对象

- [x] Task 3: 修改 `createZonesIn3D` 函数，添加办公区墙体生成逻辑
  - [x] 检测zoneType === 'office'的区域
  - [x] 沿着办公区points边线生成墙体（参考createWarehouseFromShape的墙体创建逻辑）
  - [x] 设置正确的userData属性（type: 'officeWall', zoneId, wallIndex等）
  - [x] 墙体高度使用warehouseConfig.height
  - [x] 墙体材质使用与仓库墙体相同的材质

- [x] Task 4: 修改门/窗创建函数，支持办公区墙体
  - [x] 修改 `createDoor` 函数，支持userData.type === 'officeWall'的墙体
  - [x] 修改 `createWindow` 函数，支持userData.type === 'officeWall'的墙体
  - [x] 确保门/窗的保存和加载逻辑兼容办公区墙体

- [x] Task 5: 修改保存/加载逻辑，支持办公区墙体门/窗
  - [x] 修改 `getSceneObjects` 函数，确保办公区墙体的门/窗被包含
  - [x] 修改导入逻辑，确保办公区墙体的门/窗正确恢复

# Task Dependencies
- Task 1 必须在 Task 3 之前完成（先能清理，才能重建）
- Task 2 可以并行于 Task 1
- Task 3 依赖于 Task 1
- Task 4 依赖于 Task 3
- Task 5 依赖于 Task 4
