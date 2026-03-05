# 版本备份记录

## 版本 V1.0.0 - "旋转环重构版" - 2026-03-04

### 版本代号
**旋转环重构版** (Rotation Ring Refactor)

### 版本编号
**V1.0.0**

### 备份文件
- `frontend/src/components/3d/ThreeScene.vue.v1.0.0-旋转环重构版.backup`
- `frontend/src/views/CoreFunction.vue.v1.0.0-旋转环重构版.backup`

### 功能清单

#### ✅ 已实现功能

1. **3D场景基础功能**
   - 场景渲染（背景色#f0f0e6）
   - 相机控制（OrbitControls）
   - 窗口自适应

2. **模型管理功能**
   - 模型加载（GLB格式）
   - 模型预加载
   - 模型缓存

3. **模型放置功能**
   - 拖拽放置模型
   - 批量放置模型（已移除，待重新实现）
   - 放置位置对齐网格

4. **模型操作功能**
   - 选择模型（单击选中）
   - 移动模型
   - **旋转模型（新实现：旋转环+拖动旋转）**
   - 删除模型
   - 模型高亮显示

5. **场景管理功能**
   - 导入户型图（背景图片）
   - 保存布局（JSON导出）
   - 加载布局（JSON导入）
   - 导出效果图（PNG图片）
   - 清空场景

6. **辅助功能**
   - 网格显示
   - 地面吸附（模型底部对齐地面）
   - 角落标记（选中时显示）

#### ✅ 已验证功能
- 批量放置功能已移除，需要重新实现
- **旋转功能测试通过** ✓

### 回滚方法

如果需要回滚到 **V1.0.0 旋转环重构版**，执行以下命令：

```powershell
# 回滚 ThreeScene.vue
Copy-Item -Path "frontend\src\components\3d\ThreeScene.vue.v1.0.0-旋转环重构版.backup" -Destination "frontend\src\components\3d\ThreeScene.vue" -Force

# 回滚 CoreFunction.vue
Copy-Item -Path "frontend\src\views\CoreFunction.vue.v1.0.0-旋转环重构版.backup" -Destination "frontend\src\views\CoreFunction.vue" -Force
```

### 版本说明
此版本为旋转功能重构后的版本，采用旋转环+拖动旋转的交互方式，替代了原来的滑块旋转方式。
