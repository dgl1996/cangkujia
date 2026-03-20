# 仓酷家 - 对齐线功能实现计划

## [x] 任务1: 对齐线数据结构设计与管理
- **Priority**: P0
- **Depends On**: None
- **Description**: 设计对齐线数据结构并实现管理功能
- **Status**: ✅ 已完成（2026-03-19）

  ### [x] 子任务1.1: 对齐线数据结构定义
  - **Description**: 
    - 定义AlignmentLine接口，包含id、name、startPoint、endPoint、color、style、visible等属性
    - 设计对齐线集合管理类
  - **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
  - **Test Requirements**:
    - `programmatic` TR-1.1.1: 对齐线数据结构应包含所有必要属性
    - `programmatic` TR-1.1.2: 数据结构应支持JSON序列化和反序列化
  - **Notes**: 对齐线数据应与项目数据一起保存
  - **Status**: ✅ 已完成

  ### [x] 子任务1.2: 对齐线管理功能实现
  - **Description**: 
    - 实现addAlignmentLine()函数：添加新对齐线，自动生成顺序名称
    - 实现removeAlignmentLine(id)函数：删除指定对齐线
    - 实现updateAlignmentLine(id, data)函数：更新对齐线属性
    - 实现getAlignmentLine(id)函数：获取指定对齐线
  - **Acceptance Criteria Addressed**: AC-1, AC-5
  - **Test Requirements**:
    - `human-judgment` TR-1.2.1: 对齐线管理操作应响应迅速
    - `human-judgment` TR-1.2.2: 自动命名功能应正常工作
  - **Notes**: 需确保管理操作的原子性
  - **Status**: ✅ 已完成

  ### [x] 子任务1.3: 项目保存/加载集成
  - **Description**: 
    - 修改项目保存逻辑，包含对齐线数据
    - 修改项目加载逻辑，恢复对齐线状态
    - 实现对齐线数据的版本兼容处理
  - **Acceptance Criteria Addressed**: AC-6
  - **Test Requirements**:
    - `programmatic` TR-1.3.1: 对齐线数据应正确保存到项目文件
    - `programmatic` TR-1.3.2: 加载项目时对齐线状态应完全恢复
  - **Notes**: 需考虑向后兼容性
  - **Status**: ✅ 已完成

## [x] 任务2: 对齐线渲染系统实现
- **Priority**: P0
- **Depends On**: 任务1
- **Description**: 使用Three.js实现对齐线的3D渲染
- **Status**: ✅ 已完成（2026-03-19）

  ### [x] 子任务2.1: 对齐线几何构建
  - **Description**: 
    - 实现createAlignmentLineGeometry(start, end)函数：创建线几何体
    - 实现updateAlignmentLineGeometry(line, start, end)函数：更新线几何体
  - **Acceptance Criteria Addressed**: AC-2
  - **Test Requirements**:
    - `human-judgment` TR-2.1.1: 对齐线应在地面上正确显示
    - `human-judgment` TR-2.1.2: 对齐线长度应与定义一致
  - **Notes**: 需确保线条在地面平面上
  - **Status**: ✅ 已完成

  ### [x] 子任务2.2: 对齐线材质与样式
  - **Description**: 
    - 实现createAlignmentLineMaterial()函数：创建青色虚线材质
    - 实现createHighlightedMaterial()函数：创建高亮材质
    - 实现updateLineMaterial(line, isHighlighted)函数：更新线条材质
  - **Acceptance Criteria Addressed**: AC-2
  - **Test Requirements**:
    - `human-judgment` TR-2.2.1: 对齐线应显示为青色虚线
    - `human-judgment` TR-2.2.2: 选中的对齐线应高亮显示
  - **Notes**: 虚线样式需在Three.js中正确配置
  - **Status**: ✅ 已完成

  ### [x] 子任务2.3: 对齐线场景管理
  - **Description**: 
    - 实现addLineToScene(line)函数：将对齐线添加到场景
    - 实现removeLineFromScene(line)函数：从场景中移除对齐线
    - 实现updateLineVisibility(line, visible)函数：更新对齐线可见性
  - **Acceptance Criteria Addressed**: AC-2
  - **Test Requirements**:
    - `human-judgment` TR-2.3.1: 对齐线应在场景中正确显示
    - `human-judgment` TR-2.3.2: 对齐线的显示/隐藏应正常工作
  - **Notes**: 需优化渲染性能
  - **Status**: ✅ 已完成

## [x] 任务3: 基于参考线的对齐线生成功能
- **Priority**: P1
- **Depends On**: 任务1, 任务2
- **Description**: 实现基于3D对象边缘生成参考线的功能
- **Status**: ✅ 已完成（2026-03-19）

  ### [x] 子任务3.1: 对象边界计算
  - **Description**: 
    - 实现getObjectBounds(object)函数：计算对象的边界框
    - 实现getObjectEdges(bounds)函数：提取对象的边缘线
  - **Acceptance Criteria Addressed**: AC-2
  - **Test Requirements**:
    - `human-judgment` TR-3.1.1: 边界计算应准确反映对象实际尺寸
    - `human-judgment` TR-3.1.2: 边缘提取应覆盖对象所有主要边缘
  - **Notes**: 需考虑不同类型对象的边界计算
  - **Status**: ✅ 已完成

  ### [x] 子任务3.2: 参考线生成逻辑
  - **Description**: 
    - 实现generateReferenceLines(object)函数：基于对象生成参考线
    - 实现filterReferenceLines(lines)函数：过滤冗余参考线
  - **Acceptance Criteria Addressed**: AC-2
  - **Test Requirements**:
    - `human-judgment` TR-3.2.1: 生成的参考线应准确对齐到对象边缘
    - `human-judgment` TR-3.2.2: 参考线生成应避免过度冗余
  - **Notes**: 可提供配置选项控制生成哪些边缘的参考线
  - **Status**: ✅ 已完成

## [x] 任务4: 手动绘制对齐线功能
- **Priority**: P1
- **Depends On**: 任务1, 任务2
- **Description**: 实现用户在地面上手动绘制对齐线的功能
- **Status**: ✅ 已完成（2026-03-19）

  ### [x] 子任务4.1: 鼠标事件处理
  - **Description**: 
    - 实现onMouseDown(event)函数：处理鼠标按下事件，开始绘制
    - 实现onMouseMove(event)函数：处理鼠标移动事件，更新绘制预览
    - 实现onMouseUp(event)函数：处理鼠标释放事件，完成绘制
  - **Acceptance Criteria Addressed**: AC-3
  - **Test Requirements**:
    - `human-judgment` TR-4.1.1: 鼠标事件处理应响应迅速
    - `human-judgment` TR-4.1.2: 绘制过程应流畅无卡顿
  - **Notes**: 需处理鼠标坐标到3D空间的转换
  - **Status**: ✅ 已完成

  ### [x] 子任务4.2: 绘制预览与确认
  - **Description**: 
    - 实现createPreviewLine(start, end)函数：创建预览线
    - 实现updatePreviewLine(start, end)函数：更新预览线
    - 实现confirmLineCreation()函数：确认创建对齐线
  - **Acceptance Criteria Addressed**: AC-3
  - **Test Requirements**:
    - `human-judgment` TR-4.2.1: 绘制预览应实时反映鼠标位置
    - `human-judgment` TR-4.2.2: 预览线应与最终创建的对齐线一致
  - **Notes**: 预览线样式应与最终对齐线有所区别
  - **Status**: ✅ 已完成

## [x] 任务5: 对象对齐吸附功能
- **Priority**: P0
- **Depends On**: 任务1, 任务2
- **Description**: 实现3D对象移动时的对齐吸附功能
- **Status**: ✅ 已完成（2026-03-20）- 代码已冻结

  ### [x] 子任务5.1: 距离计算与吸附逻辑
  - **Description**: 
    - 实现calculateDistance(point, line)函数：计算点到线的距离
    - 实现findClosestAlignmentLine(point, lines)函数：找到最近的对齐线
    - 实现applySnap(position, lines)函数：应用吸附逻辑
  - **Acceptance Criteria Addressed**: AC-4
  - **Test Requirements**:
    - `human-judgment` TR-5.1.1: 对象应在10CM范围内吸附到对齐线
    - `human-judgment` TR-5.1.2: 吸附操作应平滑自然
  - **Notes**: 吸附距离阈值设置为10CM
  - **Status**: ✅ 已完成 - 验收通过

  ### [x] 子任务5.2: 吸附优先级与边界处理
  - **Description**: 
    - 实现calculateSnapPriority(distance, direction, intent)函数：计算吸附优先级
    - 实现handleBoundarySnap(object, lines)函数：处理边界吸附
    - 实现cancelSnap()函数：取消吸附功能
  - **Acceptance Criteria Addressed**: AC-4
  - **Test Requirements**:
    - `human-judgment` TR-5.2.1: 吸附优先级应正确应用
    - `human-judgment` TR-5.2.2: 取消吸附功能应正常工作
  - **Notes**: 优先级顺序：最近距离 > 轴向优先 > 用户意图
  - **Status**: ✅ 已完成 - 验收通过

  ### [x] 子任务5.3: 对齐辅助提示
  - **Description**: 
    - 实现createSnapIndicator()函数：创建对齐提示指示器
    - 实现updateSnapIndicator(position, line)函数：更新对齐提示
    - 实现hideSnapIndicator()函数：隐藏对齐提示
  - **Acceptance Criteria Addressed**: AC-4
  - **Test Requirements**:
    - `human-judgment` TR-5.3.1: 对齐提示应清晰可见
    - `human-judgment` TR-5.3.2: 提示应准确指示吸附位置
  - **Notes**: 提示应在吸附发生时显示
  - **Status**: ✅ 已完成 - 验收通过

## [x] 任务6: 对齐线UI界面集成
- **Priority**: P1
- **Depends On**: 任务1, 任务2, 任务3, 任务4
- **Description**: 集成对齐线相关的UI界面
- **Status**: ✅ 已完成（2026-03-19）

  ### [x] 子任务6.1: 工具栏按钮实现
  - **Description**: 
    - 在项目工具栏添加对齐线全局按钮
    - 实现toggleAlignmentLines()函数：切换对齐线显示状态
    - 实现enterDrawMode()函数：进入绘制模式
  - **Acceptance Criteria Addressed**: AC-1, AC-2
  - **Test Requirements**:
    - `human-judgment` TR-6.1.1: 工具栏按钮应与现有风格一致
    - `human-judgment` TR-6.1.2: 按钮功能应正常工作
  - **Notes**: 按钮状态应反映当前模式
  - **Status**: ✅ 已完成

  ### [x] 子任务6.2: 左侧面板对齐线卡片
  - **Description**: 
    - 实现对齐线列表显示
    - 实现对齐线选择和高亮功能
    - 实现对齐线编辑和删除功能
  - **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
  - **Test Requirements**:
    - `human-judgment` TR-6.2.1: 对齐线列表应清晰显示所有对齐线
    - `human-judgment` TR-6.2.2: 选择功能应正常工作
  - **Notes**: 卡片设计应与现有UI风格一致
  - **Status**: ✅ 已完成

## [ ] 任务7: 测量工具集成
- **Priority**: P1
- **Depends On**: 任务1
- **Description**: 实现测量工具功能
- **Status**: ⏸️ 待开始

  ### [ ] 子任务7.1: 测量工具UI集成
  - **Description**: 
    - 在项目工具栏添加测量工具按钮
    - 实现toggleMeasureMode()函数：切换测量模式
  - **Acceptance Criteria Addressed**: FR-5
  - **Test Requirements**:
    - `human-judgment` TR-7.1.1: 测量工具按钮应与现有风格一致
    - `human-judgment` TR-7.1.2: 模式切换应正常工作
  - **Notes**: 测量模式应与其他工具模式互斥
  - **Status**: ⏸️ 待开始

  ### [ ] 子任务7.2: 两点距离测量实现
  - **Description**: 
    - 实现onMeasureStart(event)函数：开始测量
    - 实现onMeasureMove(event)函数：更新测量预览
    - 实现onMeasureEnd(event)函数：完成测量并显示结果
  - **Acceptance Criteria Addressed**: FR-5
  - **Test Requirements**:
    - `human-judgment` TR-7.2.1: 测量工具应能准确测量两点距离
    - `human-judgment` TR-7.2.2: 测量结果应清晰显示
  - **Notes**: 测量结果应显示单位（米）
  - **Status**: ⏸️ 待开始

## [ ] 任务8: 性能优化与测试
- **Priority**: P2
- **Depends On**: 所有前序任务
- **Description**: 优化性能并进行全面测试
- **Status**: ⏸️ 待开始

  ### [ ] 子任务8.1: 性能优化
  - **Description**: 
    - 实现空间分区算法优化距离计算
    - 优化对齐线渲染性能
    - 实现对齐线的懒加载
  - **Acceptance Criteria Addressed**: NFR-1
  - **Test Requirements**:
    - `programmatic` TR-8.1.1: 对齐吸附操作延迟应不超过100ms
    - `human-judgment` TR-8.1.2: 场景渲染应保持流畅
  - **Notes**: 可使用四叉树或网格空间分区
  - **Status**: ⏸️ 待开始

  ### [ ] 子任务8.2: 兼容性测试
  - **Description**: 
    - 测试与现有3D对象操作系统的兼容性
    - 测试在不同浏览器中的表现
    - 测试在不同设备上的性能
  - **Acceptance Criteria Addressed**: NFR-3
  - **Test Requirements**:
    - `human-judgment` TR-8.2.1: 对齐线功能应与现有功能无缝集成
    - `human-judgment` TR-8.2.2: 不应影响现有功能的正常使用
  - **Notes**: 需测试主流浏览器和设备
  - **Status**: ⏸️ 待开始

---

## 开发进度总结

### 已完成任务 ✅
| 任务 | 状态 | 完成日期 | 备注 |
|------|------|----------|------|
| 任务1: 对齐线数据结构设计与管理 | ✅ 完成 | 2026-03-19 | 包含3个子任务 |
| 任务2: 对齐线渲染系统实现 | ✅ 完成 | 2026-03-19 | 包含3个子任务 |
| 任务3: 基于参考线的对齐线生成功能 | ✅ 完成 | 2026-03-19 | 包含2个子任务 |
| 任务4: 手动绘制对齐线功能 | ✅ 完成 | 2026-03-19 | 包含2个子任务 |
| 任务5: 对象对齐吸附功能 | ✅ 完成 | 2026-03-20 | 包含3个子任务，代码已冻结 |
| 任务6: 对齐线UI界面集成 | ✅ 完成 | 2026-03-19 | 包含2个子任务 |

### 待开始任务 ⏸️
| 任务 | 状态 | 优先级 | 备注 |
|------|------|--------|------|
| 任务7: 测量工具集成 | ⏸️ 待开始 | P1 | 包含2个子任务 |
| 任务8: 性能优化与测试 | ⏸️ 待开始 | P2 | 包含2个子任务 |

### 代码冻结声明（任务5）
❌ 禁止修改吸附阈值（保持10cm）
❌ 禁止修改距离计算逻辑（handleBoundarySnap已正确）
❌ 禁止修改射线检测逻辑（已正确）
❌ 禁止重构AlignmentLine类
❌ 禁止优化createAlignmentLineGeometry（即使视觉端点有瑕疵）

### 关键Bug修复记录
1. **AlignmentLine类方向向量计算** - 强制Y=0，防止Y坐标漂移
2. **addLineToScene数据流** - 使用originalStart/End代替startPoint/End
3. **createAlignmentLineGeometry方向向量** - 强制Y=0，确保在XZ平面延伸

### P0教训
所有2.5D仓库布局的数学计算，必须强制Y=0，不能相信输入数据的Y坐标一定是0。
