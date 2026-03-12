"""
生成工业采光通风窗模型 - 宽2m×高1.2m、离地1.2m
标准厂房高位安装，兼顾采光与自然通风
"""

import numpy as np
import trimesh
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model_generator_template import set_mesh_color, create_scene


def generate_industrial_window(
    frame_width=2000,
    frame_height=1200,
    frame_depth=150,
    installation_height=1200,
    opening_angle=30,
    color='#F8FAFC'
):
    """
    生成工业采光通风窗模型
    
    Args:
        frame_width: 窗框宽度 (mm)，默认2m
        frame_height: 窗框高度 (mm)，默认1.2m
        frame_depth: 窗框深度 (mm)，默认150mm
        installation_height: 安装高度 (mm)，默认1.2m离地
        opening_angle: 开启角度 (度)，默认30°
        color: 窗框颜色，默认白色 #F8FAFC
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典
    """
    
    meshes = []
    
    # 颜色转换
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    
    frame_color = hex_to_rgb(color)
    glass_color = [0.9, 0.95, 1.0]  # 淡蓝透明玻璃
    
    # 1. 窗框（外框）
    frame_thickness = 40  # 窗框料厚
    
    # 上框
    top_frame = trimesh.creation.box(
        extents=[frame_width, frame_depth, frame_thickness]
    )
    top_frame.apply_translation([0, 0, frame_height - frame_thickness/2])
    set_mesh_color(top_frame, frame_color)
    meshes.append(top_frame)
    
    # 下框（窗台）
    bottom_frame = trimesh.creation.box(
        extents=[frame_width, frame_depth + 20, frame_thickness + 20]
    )
    bottom_frame.apply_translation([0, 0, frame_thickness/2 + 10])
    set_mesh_color(bottom_frame, frame_color)
    meshes.append(bottom_frame)
    
    # 左框
    left_frame = trimesh.creation.box(
        extents=[frame_thickness, frame_depth, frame_height - 2*frame_thickness]
    )
    left_frame.apply_translation([-frame_width/2 + frame_thickness/2, 0, frame_height/2])
    set_mesh_color(left_frame, frame_color)
    meshes.append(left_frame)
    
    # 右框
    right_frame = trimesh.creation.box(
        extents=[frame_thickness, frame_depth, frame_height - 2*frame_thickness]
    )
    right_frame.apply_translation([frame_width/2 - frame_thickness/2, 0, frame_height/2])
    set_mesh_color(right_frame, frame_color)
    meshes.append(right_frame)
    
    # 2. 中梃（分格）- 分为2扇
    mullion = trimesh.creation.box(
        extents=[frame_thickness, frame_depth - 10, frame_height - 2*frame_thickness]
    )
    mullion.apply_translation([0, 0, frame_height/2])
    set_mesh_color(mullion, frame_color)
    meshes.append(mullion)
    
    # 3. 窗扇（上悬外开）
    sash_thickness = 35
    sash_width = (frame_width - 3*frame_thickness) / 2
    sash_height = frame_height - 2*frame_thickness - 10
    
    # 左窗扇
    left_sash_frame = trimesh.creation.box(
        extents=[sash_width, sash_thickness, sash_height]
    )
    # 窗扇底部向外开启
    angle_rad = np.radians(opening_angle)
    y_offset = np.sin(angle_rad) * sash_height / 2
    z_offset = frame_height/2 + np.cos(angle_rad) * 10
    left_sash_frame.apply_translation([-sash_width/2 - frame_thickness/2, y_offset, z_offset])
    # 旋转开启
    left_sash_frame.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-angle_rad, direction=[1, 0, 0], 
        point=[-sash_width/2 - frame_thickness/2, 0, frame_height - frame_thickness]
    ))
    set_mesh_color(left_sash_frame, frame_color)
    meshes.append(left_sash_frame)
    
    # 左窗扇玻璃
    left_glass = trimesh.creation.box(
        extents=[sash_width - 20, 10, sash_height - 20]
    )
    left_glass.apply_translation([-sash_width/2 - frame_thickness/2, y_offset, z_offset])
    left_glass.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-angle_rad, direction=[1, 0, 0], 
        point=[-sash_width/2 - frame_thickness/2, 0, frame_height - frame_thickness]
    ))
    set_mesh_color(left_glass, glass_color)
    meshes.append(left_glass)
    
    # 右窗扇
    right_sash_frame = trimesh.creation.box(
        extents=[sash_width, sash_thickness, sash_height]
    )
    right_sash_frame.apply_translation([sash_width/2 + frame_thickness/2, y_offset, z_offset])
    right_sash_frame.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-angle_rad, direction=[1, 0, 0], 
        point=[sash_width/2 + frame_thickness/2, 0, frame_height - frame_thickness]
    ))
    set_mesh_color(right_sash_frame, frame_color)
    meshes.append(right_sash_frame)
    
    # 右窗扇玻璃
    right_glass = trimesh.creation.box(
        extents=[sash_width - 20, 10, sash_height - 20]
    )
    right_glass.apply_translation([sash_width/2 + frame_thickness/2, y_offset, z_offset])
    right_glass.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-angle_rad, direction=[1, 0, 0], 
        point=[sash_width/2 + frame_thickness/2, 0, frame_height - frame_thickness]
    ))
    set_mesh_color(right_glass, glass_color)
    meshes.append(right_glass)
    
    # 4. 纱窗（不锈钢丝网）
    screen_color = [0.7, 0.7, 0.75]  # 银灰色
    left_screen = trimesh.creation.box(
        extents=[sash_width - 10, 5, sash_height - 10]
    )
    left_screen.apply_translation([-sash_width/2 - frame_thickness/2, y_offset - 20, z_offset])
    left_screen.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-angle_rad, direction=[1, 0, 0], 
        point=[-sash_width/2 - frame_thickness/2, 0, frame_height - frame_thickness]
    ))
    set_mesh_color(left_screen, screen_color)
    meshes.append(left_screen)
    
    right_screen = trimesh.creation.box(
        extents=[sash_width - 10, 5, sash_height - 10]
    )
    right_screen.apply_translation([sash_width/2 + frame_thickness/2, y_offset - 20, z_offset])
    right_screen.apply_transform(trimesh.transformations.rotation_matrix(
        angle=-angle_rad, direction=[1, 0, 0], 
        point=[sash_width/2 + frame_thickness/2, 0, frame_height - frame_thickness]
    ))
    set_mesh_color(right_screen, screen_color)
    meshes.append(right_screen)
    
    # 5. 密封胶条（黑色）
    seal_color = [0.2, 0.2, 0.2]
    seal = trimesh.creation.box(
        extents=[frame_width - 10, 10, 5]
    )
    seal.apply_translation([0, 0, frame_height - 5])
    set_mesh_color(seal, seal_color)
    meshes.append(seal)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据
    metadata = {
        "id": "window-industrial-awning-2m",
        "name": "工业采光窗-上悬式",
        "category": "facility",
        "description": "宽2m×高1.2m、离地1.2m",
        "tags": ["窗", "采光窗", "上悬窗", "仓库设施", "通风"],
        "parameters": {
            "frameWidth": {"type": "number", "min": 1000, "max": 3000, "default": frame_width, "unit": "mm"},
            "frameHeight": {"type": "number", "min": 600, "max": 2000, "default": frame_height, "unit": "mm"},
            "installationHeight": {"type": "number", "min": 800, "max": 4000, "default": installation_height, "unit": "mm"}
        }
    }
    
    return scene, metadata


if __name__ == "__main__":
    print("生成工业采光通风窗模型...")
    
    # 生成模型
    scene, metadata = generate_industrial_window()
    
    # 导出GLB文件
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'frontend', 'public', 'assets', 'models',
        'window-industrial-awning-2m.glb'
    )
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 导出
    scene.export(output_path)
    print(f"✅ 模型已导出: {output_path}")
    print(f"📊 模型信息:")
    print(f"   - 名称: {metadata['name']}")
    print(f"   - 类别: {metadata['category']}")
    print(f"   - 尺寸: {metadata['parameters']['frameWidth']['default']}x{metadata['parameters']['frameHeight']['default']}mm")
    print(f"   - 几何体数量: {len(scene.geometry)}")
