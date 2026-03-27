# 项目报告导出功能 Spec

## Why
用户需要将仓库规划方案导出为可读的报告文档，用于汇报、存档或作为实施方案的参考。项目报告应包含仓库整体情况、功能区清单和3D物流对象清单三部分，以Markdown表格形式呈现，便于阅读和分析。

## What Changes
- 实现 `exportReport()` 函数，生成完整的项目报告
- 报告包含三部分：仓库概况、功能区清单、3D物流对象清单
- 第2、3部分使用Markdown表格格式
- 支持下载为 `.md` 文件

## Impact
- 影响文件：`CoreFunction.vue` 中的 `exportReport()` 函数
- 需要获取的数据：warehouseShape、zones、sceneObjects（3D对象）
- 新增功能：Markdown报告生成、文件下载

## ADDED Requirements

### Requirement: 项目报告导出功能
The system SHALL provide a project report export feature that generates a Markdown document containing warehouse overview, zone inventory, and 3D logistics object inventory.

#### Scenario: 成功导出项目报告
- **GIVEN** 用户已创建仓库（warehouseShape.length >= 3）
- **WHEN** 用户点击"导出项目报告"按钮
- **THEN** 系统生成Markdown格式的项目报告
- **AND** 自动触发浏览器下载 `.md` 文件
- **AND** 文件名为 `{projectName}_项目报告.md` 或 `仓库项目报告_{timestamp}.md`

#### Scenario: 未创建仓库时导出
- **GIVEN** 用户未创建仓库（warehouseShape.length < 3）
- **WHEN** 用户点击"导出项目报告"按钮
- **THEN** 显示提示"请先创建仓库！"
- **AND** 不执行导出操作

## 报告内容规范

### 第1部分：仓库概况
- 仓库名称（projectName）
- 仓库长度、宽度、高度（从3D场景获取）
- 仓库总面积（平方米）
- 功能区数量
- 3D物流对象总数

### 第2部分：功能区清单（表格）
| 序号 | 功能区名称 | 类型 | 长度(m) | 宽度(m) | 面积(m²) |
|------|-----------|------|---------|---------|----------|
| 1 | 存储区 | storage | 47.5 | 35.0 | 1662.5 |

### 第3部分：3D物流对象清单（表格）
| 序号 | 对象名称 | 型号/规格 | 尺寸(长×宽×高) | 数量 |
|------|---------|-----------|----------------|------|
| 1 | 轻型货架 | A15-4 | 1500×400×1500mm | 10 |

## 数据获取方式
- 仓库尺寸：从 `warehouseShape` 计算边界框
- 功能区数据：从 `zones` 数组获取
- 3D对象数据：从 `threeScene.value.getSceneObjects()` 获取
- 对象名称和规格：从 `userData.name` 和 `userData.modelType` 获取
