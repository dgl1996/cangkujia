"""
生成工业滑升门模型 - 4米宽、4.2米高
物流仓库装卸月台标准配置
"""

import numpy as np
import trimesh
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model_generator_template import set_mesh_color, create_scene


def generate_sectional_door(
    opening_width=4000,
    opening_height=4200,
    panel_count=5,
    panel_thickness=40,
    frame_thickness=2,
    color='#64748B'
):
    """
    生成工业滑升门模型
    
    Args:
        opening_width: 门洞宽度 (mm)，默认4m
        opening_height: 门洞高度 (mm)，默认4.2m
        panel_count: 门板分节数量，默认5块
        panel_thickness: 门板厚度 (mm)，默认40mm
        frame_thickness: 门框厚度 (mm)，默认2mm
        color: 门板颜色，默认工业灰蓝 #64748B
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典
    """
    
    meshes = []
    
    # 颜色转换
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    
    door_color = hex_to_rgb(color)
    frame_color = [c * 0.7 for c in door_color]  # 门框稍深
    
    # 1. 门板（分节提升门，显示为半开状态）
    panel_height = opening_height / panel_count
    track_depth = 600  # 导轨转弯半径
    
    # 垂直部分门板（底部3块）
    vertical_panels = 3
    for i in range(vertical_panels):
        panel = trimesh.creation.box(
            extents=[opening_width, panel_thickness, panel_height - 5]
        )
        z_pos = i * panel_height + panel_height / 2
        panel.apply_translation([0, 0, z_pos])
        set_mesh_color(panel, door_color)
        meshes.append(panel)
        
        # 门板间缝隙（黑色细线）
        gap = trimesh.creation.box(
            extents=[opening_width + 10, panel_thickness + 5, 5]
        )
        gap.apply_translation([0, 0, z_pos + panel_height / 2])
        set_mesh_color(gap, [0.2, 0.2, 0.2])
        meshes.append(gap)
    
    # 水平部分门板（顶部2块，沿轨道水平收纳）
    horizontal_panels = 2
    for i in range(horizontal_panels):
        panel = trimesh.creation.box(
            extents=[opening_width, panel_thickness, panel_height - 5]
        )
        # 水平收纳在天花板下方
        y_offset = track_depth + i * (panel_height + 10)
        z_pos = opening_height + panel_thickness / 2
        panel.apply_translation([0, y_offset, z_pos])
        # 旋转90度水平放置
        panel.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi / 2, direction=[1, 0, 0], point=[0, y_offset, z_pos]
        ))
        set_mesh_color(panel, door_color)
        meshes.append(panel)
    
    # 2. 门框（两侧+顶部）
    frame_width = 100  # 门框宽度
    
    # 左侧门框
    left_frame = trimesh.creation.box(
        extents=[frame_width, frame_thickness * 10, opening_height + 200]
    )
    left_frame.apply_translation([-opening_width / 2 - frame_width / 2, 0, opening_height / 2])
    set_mesh_color(left_frame, frame_color)
    meshes.append(left_frame)
    
    # 右侧门框
    right_frame = trimesh.creation.box(
        extents=[frame_width, frame_thickness * 10, opening_height + 200]
    )
    right_frame.apply_translation([opening_width / 2 + frame_width / 2, 0, opening_height / 2])
    set_mesh_color(right_frame, frame_color)
    meshes.append(right_frame)
    
    # 顶部门框
    top_frame = trimesh.creation.box(
        extents=[opening_width + 2 * frame_width, frame_thickness * 10, frame_width]
    )
    top_frame.apply_translation([0, 0, opening_height + frame_width / 2 + 100])
    set_mesh_color(top_frame, frame_color)
    meshes.append(top_frame)
    
    # 3. 导轨系统
    rail_thickness = 30
    
    # 垂直导轨（两侧）
    for x_offset in [-opening_width / 2 - 50, opening_width / 2 + 50]:
        # 垂直段
        vertical_rail = trimesh.creation.box(
            extents=[rail_thickness, rail_thickness, opening_height]
        )
        vertical_rail.apply_translation([x_offset, track_depth, opening_height / 2])
        set_mesh_color(vertical_rail, [0.4, 0.4, 0.4])
        meshes.append(vertical_rail)
        
        # 转弯段（弧形）
        # 简化为斜向连接
        curve_rail = trimesh.creation.box(
            extents=[rail_thickness, track_depth, rail_thickness]
        )
        curve_rail.apply_translation([x_offset, track_depth / 2, opening_height])
        set_mesh_color(curve_rail, [0.4, 0.4, 0.4])
        meshes.append(curve_rail)
        
        # 水平段
        horizontal_rail = trimesh.creation.box(
            extents=[rail_thickness, rail_thickness, opening_width / 2]
        )
        horizontal_rail.apply_translation([x_offset, 0, opening_height + 100])
        set_mesh_color(horizontal_rail, [0.4, 0.4, 0.4])
        meshes.append(horizontal_rail)
    
    # 4. 电机箱（顶部侧面）
    motor_box = trimesh.creation.box(
        extents=[300, 200, 200]
    )
    motor_box.apply_translation([opening_width / 2 + 200, track_depth, opening_height + 200])
    set_mesh_color(motor_box, [0.3, 0.3, 0.3])
    meshes.append(motor_box)
    
    # 5. 底封条（铝合金）
    bottom_seal = trimesh.creation.box(
        extents=[opening_width, panel_thickness + 20, 30]
    )
    bottom_seal.apply_translation([0, 0, 15])
    set_mesh_color(bottom_seal, [0.7, 0.7, 0.7])
    meshes.append(bottom_seal)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据
    metadata = {
        "id": "door-industrial-sectional-4m",
        "name": "工业滑升门-标准4米",
        "category": "facility",
        "description": "4米宽、4.2米高",
        "tags": ["门", "滑升门", "工业门", "仓库设施", "装卸月台"],
        "parameters": {
            "openingWidth": {"type": "number", "min": 3000, "max": 6000, "default": opening_width, "unit": "mm"},
            "openingHeight": {"type": "number", "min": 3000, "max": 6000, "default": opening_height, "unit": "mm"},
            "panelCount": {"type": "number", "min": 3, "max": 8, "default": panel_count}
        }
    }
    
    return scene, metadata


if __name__ == "__main__":
    print("生成工业滑升门模型...")
    
    # 生成模型
    scene, metadata = generate_sectional_door()
    
    # 导出GLB文件
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'frontend', 'public', 'assets', 'models',
        'door-industrial-sectional-4m.glb'
    )
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 导出
    scene.export(output_path)
    print(f"✅ 模型已导出: {output_path}")
    print(f"📊 模型信息:")
    print(f"   - 名称: {metadata['name']}")
    print(f"   - 类别: {metadata['category']}")
    print(f"   - 尺寸: {metadata['parameters']['openingWidth']['default']}x{metadata['parameters']['openingHeight']['default']}mm")
    print(f"   - 几何体数量: {len(scene.geometry)}")
