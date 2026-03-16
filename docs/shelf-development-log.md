# 货架系统开发记录

## 日期：2026-03-13

## 一、货架类型与预置型号

### 1. 轻型货架（A15系列）
- **预置型号**：A15-4（单组）、A15-4-pair（配组）
- **尺寸**：L1.5m × D0.4m × H2.0m
- **颜色**：立柱蓝色(#0066CC)，横梁橙红色(#FF4500)，层板白色(#FFFFFF)
- **立柱截面**：50mm × 40mm × 1.5mm
- **横梁截面**：50mm × 30mm × 1.2mm
- **侧拉梁**：无

### 2. 中型货架（B20系列）
- **预置型号**：B20-4（单组）、B20-4-pair（配组）
- **尺寸**：L2.0m × D0.6m × H2.0m
- **颜色**：立柱深蓝色(#00008B)，横梁橙红色(#FF4500)，层板白色(#FFFFFF)
- **立柱截面**：80mm × 60mm × 2.0mm
- **横梁截面**：80mm × 50mm × 1.5mm
- **侧拉梁**：无

### 3. 高位货架（C23系列）
- **预置型号**：C23-3（单组）、C23-3-pair（配组）
- **尺寸**：L2.3m × D1.0m × H3.0m
- **颜色**：立柱橙红色(#FF4500)，横梁深蓝色(#00008B)，层板透明
- **立柱截面**：100mm × 80mm × 3.0mm
- **横梁截面**：120mm × 60mm × 2.5mm
- **侧拉梁**：有

## 二、高位货架侧拉梁设计（关键！）

### 单组高位货架（C23-3）
- **数量**：4根
- **位置**：左右两侧各2根（上下各1根）
- **方向**：沿深度方向（Y轴），连接前后立柱
- **截面**：40mm × 25mm
- **长度**：匹配货架深度（1000mm）
- **高度位置**：下部20%、上部80%

### 背靠背配组高位货架（C23-3-pair）
- **第一组**：4根侧拉梁（1米深）+ 4根背靠背侧拉梁（20CM）
- **第二组**：4根侧拉梁（1米深），**不生成背靠背侧拉梁**
- **背靠背侧拉梁**：
  - 数量：4根（仅第一组生成）
  - 位置：两组货架之间，靠近第一组
  - 方向：沿间距方向（200mm）
  - 截面：40mm × 25mm
  - 长度：200mm（背靠背间距）
  - 连接：第一组和第二组的立柱
- **总共**：12根侧拉梁

## 三、技术实现要点

### 1. 颜色常量定义（model_generator_template.py）
```python
LIGHT_SHELF_COLORS = {
    'upright': '#0066CC',    # 立柱：蓝色
    'beam': '#FF4500',       # 横梁：橙红色
    'deck': '#FFFFFF',       # 层板：白色
}

MEDIUM_SHELF_COLORS = {
    'upright': '#00008B',    # 立柱：深蓝色
    'beam': '#FF4500',       # 横梁：橙红色
    'deck': '#FFFFFF',       # 层板：白色
}

HIGH_SHELF_COLORS = {
    'upright': '#FF4500',    # 立柱：橙红色
    'beam': '#00008B',       # 横梁：深蓝色
    'deck': None,            # 层板：透明
}
```

### 2. 尺寸常量定义
```python
LIGHT_SHELF_SIZES = {
    'upright': (50, 40),     # 立柱截面：宽度x深度
    'beam': (50, 30),        # 横梁截面：高度x宽度
    'deck_thickness': 20,    # 层板厚度
}

MEDIUM_SHELF_SIZES = {
    'upright': (80, 60),     # 立柱截面：宽度x深度
    'beam': (80, 50),        # 横梁截面：高度x宽度
    'deck_thickness': 20,    # 层板厚度
}

HIGH_SHELF_SIZES = {
    'upright': (100, 80),    # 立柱截面：宽度x深度
    'beam': (120, 60),       # 横梁截面：高度x宽度
    'deck_thickness': 20,    # 层板厚度
}
```

### 3. 关键函数参数
- `生成侧拉梁`：控制是否生成两侧侧拉梁
- `背靠背侧拉梁`：控制是否生成背靠背侧拉梁
- `背靠背间距`：背靠背间距（mm）

### 4. 配组生成逻辑（generate_pair_shelf）
```python
# 第一组：生成背靠背侧拉梁
kwargs_first = kwargs.copy()
kwargs_first['背靠背侧拉梁'] = True
kwargs_first['背靠背间距'] = spacing
scene1, metadata1 = shelf_generator_func(**kwargs_first)

# 第二组：不生成背靠背侧拉梁
kwargs_second = kwargs.copy()
kwargs_second['背靠背侧拉梁'] = False
scene2, metadata2 = shelf_generator_func(**kwargs_second)
```

## 四、开发过程中的关键教训

### 1. 侧拉梁方向问题
- **错误**：侧拉梁方向与横梁平行（水平方向）
- **正确**：侧拉梁应垂直于横梁，沿深度方向连接前后立柱

### 2. 背靠背侧拉梁归属问题
- **错误**：两组货架都生成背靠背侧拉梁
- **正确**：只有第一组生成背靠背侧拉梁，第二组不生成

### 3. 背靠背侧拉梁位置问题
- **错误**：背靠背侧拉梁位于第二组外侧
- **正确**：背靠背侧拉梁位于两组之间，靠近第一组

## 五、相关文件

### 核心文件
- `scripts/model_generator_template.py`：3D模型生成工具
- `frontend/src/views/ModelLibrary.vue`：P2页对象库
- `frontend/src/views/CoreFunction.vue`：P1页核心功能
- `frontend/src/components/3d/ThreeScene.vue`：3D场景组件

### 生成的模型文件
- `frontend/public/assets/models/light-duty-A15-4.glb`
- `frontend/public/assets/models/light-duty-A15-4-pair.glb`
- `frontend/public/assets/models/medium-duty-B20-4.glb`
- `frontend/public/assets/models/medium-duty-B20-4-pair.glb`
- `frontend/public/assets/models/high-duty-C23-3.glb`
- `frontend/public/assets/models/high-duty-C23-3-pair.glb`

## 六、后续扩展建议

1. **中型货架侧拉梁**：如需增强稳定性，可参考高位货架添加侧拉梁
2. **轻型货架配组**：当前轻型货架配组无侧拉梁，如需增强可添加
3. **自定义货架参数**：用户可能需要调整侧拉梁位置、数量等参数

---

**记录人**：RMF  
**日期**：2026-03-13
