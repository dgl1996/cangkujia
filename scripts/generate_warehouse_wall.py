"""
生成仓库外围墙体模型 - 半透明玻璃幕墙风格
与草图大师（SketchUp）纯色描边风格融合
"""

import numpy as np
import trimesh
import sys
import os

# 添加脚本目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_generator_template import set_mesh_color, create_scene


def generate_warehouse_perimeter_wall(
    length=10000,
    width=200,
    height=8000,
    opacity=0.3,
    base_color='#E0F2F1',
    edge_color='#000000',
    base_height=300,
    base_color_solid='#B0BEC5',
    parapet_height=400,
    mullion_spacing=3000,
    mullion_width=80
):
    """
    生成仓库外围墙体 - 半透明玻璃幕墙风格
    
    Args:
        length: 墙体长度 (mm)，默认10m
        width: 墙体厚度 (mm)，默认200mm
        height: 墙体总高度 (mm)，默认8m
        opacity: 玻璃透明度 (0-1)，默认0.3（70%通透）
        base_color: 玻璃颜色，默认淡青色 #E0F2F1
        edge_color: 描边颜色，默认黑色
        base_height: 底部实墙高度 (mm)，默认300mm
        base_color_solid: 底部实墙颜色，默认灰色 #B0BEC5
        parapet_height: 女儿墙高度 (mm)，默认400mm
        mullion_spacing: 龙骨间距 (mm)，默认3m
        mullion_width: 龙骨宽度 (mm)，默认80mm
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典
    """
    
    meshes = []
    
    # 颜色转换 (hex to rgb 0-1)
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    
    glass_color = hex_to_rgb(base_color)
    solid_color = hex_to_rgb(base_color_solid)
    edge_rgb = hex_to_rgb(edge_color)
    
    # 1. 底部实墙基座 (防碰撞)
    base_wall = trimesh.creation.box(
        extents=[length, width, base_height]
    )
    base_wall.apply_translation([0, 0, base_height / 2])
    set_mesh_color(base_wall, solid_color)
    meshes.append(base_wall)
    
    # 2. 玻璃幕墙主体 (半透明)
    glass_height = height - base_height - parapet_height
    glass_wall = trimesh.creation.box(
        extents=[length, width * 0.6, glass_height]  # 玻璃薄一些
    )
    glass_wall.apply_translation([0, 0, base_height + glass_height / 2])
    set_mesh_color(glass_wall, glass_color)
    meshes.append(glass_wall)
    
    # 3. 顶部女儿墙 (不透明)
    parapet_wall = trimesh.creation.box(
        extents=[length, width, parapet_height]
    )
    parapet_wall.apply_translation([0, 0, height - parapet_height / 2])
    set_mesh_color(parapet_wall, solid_color)
    meshes.append(parapet_wall)
    
    # 4. 垂直龙骨 (铝合金框架)
    num_mullions = int(length / mullion_spacing) + 1
    for i in range(num_mullions):
        x_pos = -length / 2 + i * mullion_spacing
        if x_pos > length / 2:
            break
        
        # 龙骨贯穿底部到顶部
        mullion = trimesh.creation.box(
            extents=[mullion_width, width * 1.2, height]
        )
        mullion.apply_translation([x_pos, 0, height / 2])
        # 龙骨颜色略深于玻璃
        mullion_color = [c * 0.8 for c in glass_color]
        set_mesh_color(mullion, mullion_color)
        meshes.append(mullion)
    
    # 5. 水平横梁 (顶部和底部各一道)
    for z_pos in [base_height, height - parapet_height]:
        beam = trimesh.creation.box(
            extents=[length, width * 1.1, mullion_width]
        )
        beam.apply_translation([0, 0, z_pos])
        beam_color = [c * 0.8 for c in glass_color]
        set_mesh_color(beam, beam_color)
        meshes.append(beam)
    
    # 6. 黑色描边效果 (草图大师风格)
    # 创建轮廓线 - 使用细长的box模拟
    edge_thickness = 20  # 描边粗细 2px 对应 20mm
    
    # 顶部边缘线
    top_edge = trimesh.creation.box(
        extents=[length + edge_thickness * 2, width + edge_thickness * 2, edge_thickness]
    )
    top_edge.apply_translation([0, 0, height + edge_thickness / 2])
    set_mesh_color(top_edge, edge_rgb)
    meshes.append(top_edge)
    
    # 底部边缘线
    bottom_edge = trimesh.creation.box(
        extents=[length + edge_thickness * 2, width + edge_thickness * 2, edge_thickness]
    )
    bottom_edge.apply_translation([0, 0, -edge_thickness / 2])
    set_mesh_color(bottom_edge, edge_rgb)
    meshes.append(bottom_edge)
    
    # 左侧边缘线
    left_edge = trimesh.creation.box(
        extents=[edge_thickness, width + edge_thickness * 2, height + edge_thickness * 2]
    )
    left_edge.apply_translation([-length / 2 - edge_thickness / 2, 0, height / 2])
    set_mesh_color(left_edge, edge_rgb)
    meshes.append(left_edge)
    
    # 右侧边缘线
    right_edge = trimesh.creation.box(
        extents=[edge_thickness, width + edge_thickness * 2, height + edge_thickness * 2]
    )
    right_edge.apply_translation([length / 2 + edge_thickness / 2, 0, height / 2])
    set_mesh_color(right_edge, edge_rgb)
    meshes.append(right_edge)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据
    metadata = {
        "id": "wall-warehouse-perimeter-glass",
        "name": "仓库外围墙体-半透明",
        "category": "facility",
        "description": "仓库外围半透明玻璃幕墙墙体，70%通透率，淡青灰色调，草图大师风格描边",
        "tags": ["墙体", "玻璃幕墙", "半透明", "仓库设施", "草图风格"],
        "parameters": {
            "length": {"type": "number", "min": 5000, "max": 20000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 100, "max": 500, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 3000, "max": 12000, "default": height, "unit": "mm"},
            "opacity": {"type": "number", "min": 0.1, "max": 0.9, "default": opacity}
        }
    }
    
    return scene, metadata


if __name__ == "__main__":
    print("生成仓库外围墙体模型...")
    
    # 生成模型
    scene, metadata = generate_warehouse_perimeter_wall()
    
    # 导出GLB文件
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'frontend', 'public', 'assets', 'models',
        'wall-warehouse-perimeter-glass.glb'
    )
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 导出
    scene.export(output_path)
    print(f"✅ 模型已导出: {output_path}")
    print(f"📊 模型信息:")
    print(f"   - 名称: {metadata['name']}")
    print(f"   - 类别: {metadata['category']}")
    print(f"   - 尺寸: {metadata['parameters']['length']['default']}x{metadata['parameters']['width']['default']}x{metadata['parameters']['height']['default']}mm")
    print(f"   - 几何体数量: {len(scene.geometry)}")
