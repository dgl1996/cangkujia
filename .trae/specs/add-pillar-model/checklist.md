# Checklist

## 阶段一：ThreeScene.vue 中立柱创建功能
- [x] `createPillar` 函数能正确创建立柱
- [x] 立柱尺寸为 20cm × 30cm × 墙体高度
- [x] 立柱材质与墙体一致（颜色 0x888888，透明度 0.8）
- [x] 立柱位置正确（底部对齐地面）
- [x] 立柱 userData 包含 type='pillar', modelType='pillar', name='立柱'
- [x] `onDrop` 函数能处理 `objectType === 'pillar'`
- [x] 拖拽放置能在正确位置创建立柱
- [x] `createPillar` 函数已 expose

## 阶段二：CoreFunction.vue 中菜单和批量复制
- [x] `onPillarDragStart` 函数设置正确的拖拽数据
- [x] 仓库设施菜单显示 "🏛️ 立柱 (20×30cm)"
- [x] 菜单项支持拖拽
- [x] `isSelectedObjectShelf` 计算属性包含立柱类型判断
- [x] 选中立柱时批量复制面板显示
- [x] `onPillarDragStart` 函数已 expose

## 阶段三：整体自检验证
- [x] 从菜单拖拽立柱到场景成功
- [x] 立柱外观、尺寸、材质正确
- [x] 立柱位置对齐网格
- [x] 批量复制功能对立柱可用
- [x] 保存项目后立柱正确保存
- [x] 加载项目后立柱正确恢复
