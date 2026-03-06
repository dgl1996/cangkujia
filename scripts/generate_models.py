"""
仓酷家 3D模型生成脚本
使用 Trimesh 程序化生成物流设备模型
"""

import trimesh
import numpy as np
from pathlib import Path
import json

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 元数据文件
METADATA_FILE = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "model_metadata.json"


def save_model(mesh, filename, metadata=None):
    """保存模型并记录元数据"""
    filepath = OUTPUT_DIR / filename
    mesh.export(str(filepath))
    print(f"✓ 生成: {filename}")
    
    if metadata:
        metadata["filename"] = filename
        return metadata
    return None


def generate_wooden_pallet(length=1200, width=1000, height=150):
    """
    生成木质托盘
    标准欧标托盘: 1200x1000x150mm
    """
    meshes = []
    
    # 木板厚度
    board_thickness = 22
    # 垫块高度
    block_height = height - board_thickness * 3
    block_size = 100
    
    # 顶板 (3块)
    top_board_width = width / 3
    for i in range(3):
        y_pos = -width/2 + top_board_width/2 + i * top_board_width
        board = trimesh.creation.box(
            extents=[length, top_board_width - 10, board_thickness]
        )
        board.apply_translation([0, y_pos, height - board_thickness/2])
        meshes.append(board)
    
    # 底板 (3块)
    for i in range(3):
        y_pos = -width/2 + top_board_width/2 + i * top_board_width
        board = trimesh.creation.box(
            extents=[length, top_board_width - 10, board_thickness]
        )
        board.apply_translation([0, y_pos, board_thickness/2])
        meshes.append(board)
    
    # 中间板 (3块)
    for i in range(3):
        y_pos = -width/2 + top_board_width/2 + i * top_board_width
        board = trimesh.creation.box(
            extents=[length, top_board_width - 10, board_thickness]
        )
        board.apply_translation([0, y_pos, height/2])
        meshes.append(board)
    
    # 垫块 (9块)
    block_positions = [
        [-length/3, -width/3], [0, -width/3], [length/3, -width/3],
        [-length/3, 0], [0, 0], [length/3, 0],
        [-length/3, width/3], [0, width/3], [length/3, width/3]
    ]
    
    for x, y in block_positions:
        block = trimesh.creation.box(
            extents=[block_size, block_size, block_height]
        )
        block.apply_translation([x, y, board_thickness + block_height/2])
        meshes.append(block)
    
    # 合并所有网格
    pallet = trimesh.util.concatenate(meshes)
    
    # 设置颜色 (木质)
    pallet.visual.vertex_colors = [139, 90, 43, 255]  # 棕色
    
    return pallet, {
        "id": "pallet-wooden-1200",
        "name": "木质托盘 1200×1000",
        "category": "containers",
        "description": "标准欧标木质托盘，四面进叉",
        "tags": ["木质", "标准", "欧标"],
        "parameters": {
            "length": {"type": "number", "min": 800, "max": 1400, "default": 1200, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 120, "max": 200, "default": 150, "unit": "mm"}
        }
    }


def generate_plastic_pallet(length=1200, width=1000, height=150):
    """
    生成塑料托盘 (网格型)
    """
    meshes = []
    
    # 顶面 (网格状)
    top_surface = trimesh.creation.box(
        extents=[length, width, 20]
    )
    top_surface.apply_translation([0, 0, height - 10])
    meshes.append(top_surface)
    
    # 底部支撑 (网格加强筋)
    # 纵向加强筋
    for i in range(5):
        x_pos = -length/2 + length/4 * i
        rib = trimesh.creation.box(
            extents=[30, width, height - 40]
        )
        rib.apply_translation([x_pos, 0, height/2])
        meshes.append(rib)
    
    # 横向加强筋
    for i in range(3):
        y_pos = -width/2 + width/2 * i
        rib = trimesh.creation.box(
            extents=[length, 30, height - 40]
        )
        rib.apply_translation([0, y_pos, height/2])
        meshes.append(rib)
    
    # 底部面板
    bottom = trimesh.creation.box(
        extents=[length, width, 20]
    )
    bottom.apply_translation([0, 0, 10])
    meshes.append(bottom)
    
    # 合并
    pallet = trimesh.util.concatenate(meshes)
    
    # 设置颜色 (蓝色塑料)
    pallet.visual.vertex_colors = [30, 100, 180, 255]
    
    return pallet, {
        "id": "pallet-plastic-1200",
        "name": "塑料托盘 1200×1000",
        "category": "containers",
        "description": "HDPE塑料托盘，防潮防腐蚀",
        "tags": ["塑料", "防潮", "耐用"],
        "parameters": {
            "length": {"type": "number", "min": 800, "max": 1400, "default": 1200, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 120, "max": 200, "default": 150, "unit": "mm"}
        }
    }


def generate_foldable_container(length=600, width=400, height=300):
    """
    生成可折叠周转箱
    """
    meshes = []
    wall_thickness = 5
    
    # 底板
    base = trimesh.creation.box(
        extents=[length, width, wall_thickness]
    )
    base.apply_translation([0, 0, wall_thickness/2])
    meshes.append(base)
    
    # 四壁
    # 前壁
    front = trimesh.creation.box(
        extents=[length, wall_thickness, height]
    )
    front.apply_translation([0, -width/2 + wall_thickness/2, height/2])
    meshes.append(front)
    
    # 后壁
    back = trimesh.creation.box(
        extents=[length, wall_thickness, height]
    )
    back.apply_translation([0, width/2 - wall_thickness/2, height/2])
    meshes.append(back)
    
    # 左壁
    left = trimesh.creation.box(
        extents=[wall_thickness, width - 2*wall_thickness, height]
    )
    left.apply_translation([-length/2 + wall_thickness/2, 0, height/2])
    meshes.append(left)
    
    # 右壁
    right = trimesh.creation.box(
        extents=[wall_thickness, width - 2*wall_thickness, height]
    )
    right.apply_translation([length/2 - wall_thickness/2, 0, height/2])
    meshes.append(right)
    
    # 合并
    container = trimesh.util.concatenate(meshes)
    
    # 设置颜色 (灰色塑料)
    container.visual.vertex_colors = [120, 120, 120, 255]
    
    return container, {
        "id": "container-foldable",
        "name": "可折叠周转箱",
        "category": "containers",
        "description": "可折叠设计，节省回程运输空间",
        "tags": ["可折叠", "周转箱", "省空间"],
        "parameters": {
            "length": {"type": "number", "min": 300, "max": 800, "default": 600, "unit": "mm"},
            "width": {"type": "number", "min": 200, "max": 600, "default": 400, "unit": "mm"},
            "height": {"type": "number", "min": 200, "max": 500, "default": 300, "unit": "mm"}
        }
    }


def generate_beam_shelf(length=2700, width=1000, height=4500, levels=4, load_capacity="heavy"):
    """
    生成横梁式货架 - 使用Scene保留独立mesh以便前端着色
    
    Args:
        length: 货架长度 (mm)
        width: 货架深度 (mm)
        height: 货架高度 (mm)
        levels: 层数
        load_capacity: "heavy"(重型), "medium"(中型), "light"(轻型)
    """
    meshes = []
    
    # 根据载重确定立柱和横梁规格
    if load_capacity == "heavy":
        upright_size = 90  # 立柱截面
        beam_height = 120
        beam_width = 50
        upright_color = [0.8, 0.2, 0.2]  # 红色
        beam_color = [0.9, 0.4, 0.1]     # 橙红
        deck_color = [0.95, 0.95, 0.95]  # 白色
    elif load_capacity == "medium":
        upright_size = 70
        beam_height = 100
        beam_width = 40
        upright_color = [0.2, 0.5, 0.8]  # 淡蓝色
        beam_color = [0.9, 0.4, 0.1]     # 橙红
        deck_color = [0.95, 0.95, 0.95]  # 白色
    else:
        upright_size = 55
        beam_height = 80
        beam_width = 35
        upright_color = [0.2, 0.5, 0.8]  # 淡蓝色
        beam_color = [0.9, 0.4, 0.1]     # 橙红
        deck_color = [0.95, 0.95, 0.95]  # 白色
    
    # 立柱 (4根)
    upright_positions = [
        [-length/2 + upright_size/2, -width/2 + upright_size/2],
        [length/2 - upright_size/2, -width/2 + upright_size/2],
        [-length/2 + upright_size/2, width/2 - upright_size/2],
        [length/2 - upright_size/2, width/2 - upright_size/2]
    ]
    
    for i, (x, y) in enumerate(upright_positions):
        upright = trimesh.creation.box(
            extents=[upright_size, upright_size, height]
        )
        upright.apply_translation([x, y, height/2])
        set_mesh_color(upright, upright_color)
        meshes.append((f'upright_{i}', upright))
    
    # 横梁 (每层2根)
    level_height = height / (levels + 1)
    for level in range(1, levels + 1):
        z = level * level_height
        
        # 前横梁
        front_beam = trimesh.creation.box(
            extents=[length - 2*upright_size, beam_width, beam_height]
        )
        front_beam.apply_translation([0, -width/2 + upright_size/2, z])
        set_mesh_color(front_beam, beam_color)
        meshes.append((f'beam_front_{level}', front_beam))
        
        # 后横梁
        back_beam = trimesh.creation.box(
            extents=[length - 2*upright_size, beam_width, beam_height]
        )
        back_beam.apply_translation([0, width/2 - upright_size/2, z])
        set_mesh_color(back_beam, beam_color)
        meshes.append((f'beam_back_{level}', back_beam))
        
        # 层板
        deck = trimesh.creation.box(
            extents=[length - 2*upright_size, width - 2*upright_size, 30]
        )
        deck.apply_translation([0, 0, z - 15])
        set_mesh_color(deck, deck_color)
        meshes.append((f'deck_{level}', deck))
    
    # 使用Scene并应用坐标转换
    scene = trimesh.Scene()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    
    for name, mesh in meshes:
        mesh.apply_transform(rotation_matrix)
        scene.add_geometry(mesh, node_name=name)
    
    # 元数据
    if load_capacity == "heavy":
        name = "重型横梁式货架"
        desc = "适用于重型货物存储，单层承重2000kg"
        tags = ["重型", "横梁式", "可调节"]
        model_id = "shelf-beam-heavy"
    elif load_capacity == "medium":
        name = "中型横梁式货架"
        desc = "适用于中型货物存储，单层承重500kg"
        tags = ["中型", "横梁式", "标准"]
        model_id = "shelf-beam-medium"
    else:
        name = "轻型横梁式货架"
        desc = "适用于轻型货物存储，单层承重200kg"
        tags = ["轻型", "横梁式", "经济"]
        model_id = "shelf-beam-light"
    
    return scene, {
        "id": model_id,
        "name": name,
        "category": "storage",
        "description": desc,
        "tags": tags,
        "parameters": {
            "length": {"type": "number", "min": 1500, "max": 4000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 600, "max": 1200, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 2000, "max": 12000, "default": height, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 8, "default": levels}
        }
    }


def generate_drive_in_shelf(length=3600, width=1500, height=6000, depth=5):
    """
    生成驶入式货架
    """
    meshes = []
    
    upright_size = 100
    rail_height = 120
    rail_width = 60
    
    # 立柱组 (双排)
    for row in range(2):
        y_offset = (row - 0.5) * (width - upright_size)
        for col in range(depth + 1):
            x_pos = -length/2 + col * (length / depth)
            upright = trimesh.creation.box(
                extents=[upright_size, upright_size, height]
            )
            upright.apply_translation([x_pos, y_offset, height/2])
            meshes.append(upright)
    
    # 牛腿梁 (每层每侧)
    level_height = 1400  # 托盘高度 + 间隙
    levels = int(height / level_height) - 1
    
    for level in range(1, levels + 1):
        z = level * level_height
        
        for row in range(2):
            y_offset = (row - 0.5) * (width - upright_size)
            
            for col in range(depth):
                x_pos = -length/2 + col * (length / depth) + (length / depth) / 2
                
                rail = trimesh.creation.box(
                    extents=[length / depth - 50, rail_width, rail_height]
                )
                rail.apply_translation([x_pos, y_offset, z])
                meshes.append(rail)
    
    # 顶部拉梁
    top_beam = trimesh.creation.box(
        extents=[length, 80, 150]
    )
    top_beam.apply_translation([0, 0, height - 75])
    meshes.append(top_beam)
    
    # 合并
    shelf = trimesh.util.concatenate(meshes)
    shelf.visual.vertex_colors = [70, 70, 70, 255]  # 深灰色
    
    return shelf, {
        "id": "shelf-drive-in",
        "name": "驶入式货架",
        "category": "storage",
        "description": "高密度存储，适合大批量同类型货物",
        "tags": ["高密度", "驶入式", "冷链"],
        "parameters": {
            "length": {"type": "number", "min": 2000, "max": 6000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 1200, "max": 1800, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 3000, "max": 12000, "default": height, "unit": "mm"},
            "depth": {"type": "number", "min": 2, "max": 10, "default": depth, "unit": "托盘位"}
        }
    }


def set_mesh_color(mesh, color_rgb):
    """设置网格颜色，使用顶点颜色确保GLB导出正确"""
    # 将颜色转换为 0-255 范围
    color_255 = [int(c * 255) for c in color_rgb] + [255]
    
    # 为每个顶点设置颜色
    if hasattr(mesh.visual, 'vertex_colors'):
        mesh.visual.vertex_colors = color_255
    
    # 使用简单的材质，避免PBR材质纹理问题
    # 不设置material，让Three.js使用默认材质并读取顶点颜色
    
    return mesh


def generate_light_shelf_v2(length=1200, width=400, height=2000, levels=4):
    """
    生成轻型货架 V2 - 基于参考图片改进版
    """
    meshes = []
    
    # 颜色定义 (参考图片) - 使用RGB 0-1范围
    COLOR_BLUE = [0.25, 0.45, 0.85]      # 立柱蓝色
    COLOR_ORANGE = [0.91, 0.36, 0.02]    # 横梁橙色
    COLOR_WHITE = [0.96, 0.96, 0.96]     # 层板白色
    COLOR_GREY = [0.39, 0.39, 0.39]      # 脚垫灰色
    
    # 尺寸参数
    upright_width = 40
    upright_depth = 30
    beam_height = 35
    beam_width = 30
    deck_thickness = 20
    foot_height = 30
    
    # 立柱位置 (4根)
    upright_positions = [
        [-length/2 + upright_width/2, -width/2 + upright_depth/2],
        [length/2 - upright_width/2, -width/2 + upright_depth/2],
        [-length/2 + upright_width/2, width/2 - upright_depth/2],
        [length/2 - upright_width/2, width/2 - upright_depth/2]
    ]
    
    # 生成立柱和脚垫
    for x, y in upright_positions:
        # 主立柱
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height - foot_height]
        )
        upright.apply_translation([x, y, (height - foot_height)/2 + foot_height])
        set_mesh_color(upright, COLOR_BLUE)
        meshes.append(upright)
        
        # 脚垫
        foot = trimesh.creation.box(
            extents=[upright_width + 10, upright_depth + 10, foot_height]
        )
        foot.apply_translation([x, y, foot_height/2])
        set_mesh_color(foot, COLOR_GREY)
        meshes.append(foot)
    
    # 计算层板高度
    level_spacing = (height - 300) / (levels + 1)
    
    # 生成横梁和层板
    for level in range(1, levels + 1):
        z = 150 + level * level_spacing
        
        # 横梁 (前后各一根)
        for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
            # 主横梁 (阶梯状，用两个长方体组合)
            beam_top = trimesh.creation.box(
                extents=[length - 2*upright_width - 10, beam_width, beam_height/2]
            )
            beam_top.apply_translation([0, y_offset, z + beam_height/4])
            
            beam_bottom = trimesh.creation.box(
                extents=[length - 2*upright_width, beam_width + 5, beam_height/2]
            )
            beam_bottom.apply_translation([0, y_offset, z - beam_height/4])
            
            set_mesh_color(beam_top, COLOR_ORANGE)
            set_mesh_color(beam_bottom, COLOR_ORANGE)
            meshes.append(beam_top)
            meshes.append(beam_bottom)
        
        # 层板
        deck = trimesh.creation.box(
            extents=[length - 2*upright_width - 20, width - 2*upright_depth - 10, deck_thickness]
        )
        deck.apply_translation([0, 0, z])
        set_mesh_color(deck, COLOR_WHITE)
        meshes.append(deck)
    
    # 斜拉支撑
    for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
        diag_left = trimesh.creation.box(extents=[3, 3, height * 0.7])
        diag_left.apply_translation([-length/2 + upright_width + 20, y_offset, height/2])
        set_mesh_color(diag_left, COLOR_BLUE)
        meshes.append(diag_left)
        
        diag_right = trimesh.creation.box(extents=[3, 3, height * 0.7])
        diag_right.apply_translation([length/2 - upright_width - 20, y_offset, height/2])
        set_mesh_color(diag_right, COLOR_BLUE)
        meshes.append(diag_right)
    
    # 使用Scene并应用坐标转换
    scene = trimesh.Scene()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    
    for i, mesh in enumerate(meshes):
        mesh.apply_transform(rotation_matrix)
        scene.add_geometry(mesh, node_name=f'part_{i}')
    
    return scene, {
        "id": "shelf-light-v2",
        "name": "轻型货架 V2",
        "category": "storage",
        "description": "基于参考图片改进的轻型货架，蓝色立柱配橙色横梁",
        "tags": ["轻型", "横梁式", "蓝色立柱", "橙色横梁"],
        "parameters": {
            "length": {"type": "number", "min": 800, "max": 2000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 300, "max": 600, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 1500, "max": 3000, "default": height, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 6, "default": levels}
        }
    }


def generate_heavy_shelf_simple(length=2300, width=1000, height=4500, levels=4, 
                                 layer_heights=None, upright_size=(90, 80), beam_size=(100, 50)):
    """
    通用货架生成函数 - 支持自定义立柱和横梁尺寸
    
    Args:
        length: 货架长度 (mm)
        width: 货架深度 (mm)
        height: 货架高度 (mm)
        levels: 层数
        layer_heights: 各层层高列表
        upright_size: (宽度, 深度) 立柱截面尺寸
        beam_size: (高度, 宽度) 横梁截面尺寸
    """
    meshes = []
    
    # 颜色定义 - 使用RGB 0-1范围
    COLOR_BLUE = [0.18, 0.25, 0.45]      # 立柱深蓝色
    COLOR_ORANGE = [0.85, 0.45, 0.15]    # 横梁橙色
    COLOR_DECK = [0.75, 0.75, 0.75]      # 层板灰色
    
    # 尺寸参数
    upright_width, upright_depth = upright_size
    beam_height, beam_width = beam_size
    deck_thickness = 30
    foot_height = 50
    
    # 计算各层高度
    if layer_heights is None:
        base_height = 200
        available_height = height - base_height - 200
        avg_height = available_height / levels
        layer_heights = [avg_height] * levels
    
    # 立柱位置（4根）
    upright_positions = [
        [-length/2 + upright_width/2, -width/2 + upright_depth/2],
        [length/2 - upright_width/2, -width/2 + upright_depth/2],
        [-length/2 + upright_width/2, width/2 - upright_depth/2],
        [length/2 - upright_width/2, width/2 - upright_depth/2]
    ]
    
    # 生成立柱和脚垫
    for x, y in upright_positions:
        # 主立柱
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height - foot_height]
        )
        upright.apply_translation([x, y, (height - foot_height)/2 + foot_height])
        set_mesh_color(upright, COLOR_BLUE)
        meshes.append(upright)
        
        # 脚垫
        foot = trimesh.creation.box(
            extents=[upright_width + 20, upright_depth + 20, foot_height]
        )
        foot.apply_translation([x, y, foot_height/2])
        set_mesh_color(foot, COLOR_ORANGE)
        meshes.append(foot)
    
    # 生成横梁和层板
    current_z = 200
    for level in range(levels):
        layer_height = layer_heights[level]
        current_z += layer_height
        
        # 横梁 (前后各一根)
        for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
            # 主横梁 (阶梯状，用两个长方体组合)
            beam_top = trimesh.creation.box(
                extents=[length - 2*upright_width - 10, beam_width, beam_height/2]
            )
            beam_top.apply_translation([0, y_offset, current_z + beam_height/4])
            
            beam_bottom = trimesh.creation.box(
                extents=[length - 2*upright_width, beam_width + 5, beam_height/2]
            )
            beam_bottom.apply_translation([0, y_offset, current_z - beam_height/4])
            
            set_mesh_color(beam_top, COLOR_ORANGE)
            set_mesh_color(beam_bottom, COLOR_ORANGE)
            meshes.append(beam_top)
            meshes.append(beam_bottom)
        
        # 层板
        deck = trimesh.creation.box(
            extents=[length - 2*upright_width - 20, width - 2*upright_depth - 10, deck_thickness]
        )
        deck.apply_translation([0, 0, current_z])
        set_mesh_color(deck, COLOR_DECK)
        meshes.append(deck)
    
    # 斜拉支撑
    for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
        diag_left = trimesh.creation.box(extents=[5, 5, height * 0.7])
        diag_left.apply_translation([-length/2 + upright_width + 100, y_offset, height/2])
        set_mesh_color(diag_left, COLOR_BLUE)
        meshes.append(diag_left)
        
        diag_right = trimesh.creation.box(extents=[5, 5, height * 0.7])
        diag_right.apply_translation([length/2 - upright_width - 100, y_offset, height/2])
        set_mesh_color(diag_right, COLOR_BLUE)
        meshes.append(diag_right)
    
    # 使用Scene并应用坐标转换 - 完全复制V2
    scene = trimesh.Scene()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    
    for i, mesh in enumerate(meshes):
        mesh.apply_transform(rotation_matrix)
        scene.add_geometry(mesh, node_name=f'part_{i}')
    
    return scene


def generate_light_shelf_v2_style(length=1200, width=400, height=2000, levels=4):
    """
    生成轻型货架 - 使用V2的细参数（细立柱、细横梁）
    适用于轻型货架，视觉更纤细美观
    """
    meshes = []
    
    # 颜色定义 - 使用V2的颜色
    COLOR_BLUE = [0.25, 0.45, 0.85]      # 立柱蓝色
    COLOR_ORANGE = [0.91, 0.36, 0.02]    # 横梁橙色
    COLOR_WHITE = [0.96, 0.96, 0.96]     # 层板白色
    COLOR_GREY = [0.39, 0.39, 0.39]      # 脚垫灰色
    
    # 尺寸参数 - 使用V2的细参数
    upright_width = 40       # 立柱宽度（细）
    upright_depth = 30       # 立柱深度（细）
    beam_height = 35         # 横梁高度（细）
    beam_width = 30          # 横梁宽度（细）
    deck_thickness = 20      # 层板厚度（薄）
    foot_height = 30         # 脚垫高度
    
    # 立柱位置（4根）
    upright_positions = [
        [-length/2 + upright_width/2, -width/2 + upright_depth/2],
        [length/2 - upright_width/2, -width/2 + upright_depth/2],
        [-length/2 + upright_width/2, width/2 - upright_depth/2],
        [length/2 - upright_width/2, width/2 - upright_depth/2]
    ]
    
    # 生成立柱和脚垫
    for x, y in upright_positions:
        # 主立柱
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height - foot_height]
        )
        upright.apply_translation([x, y, (height - foot_height)/2 + foot_height])
        set_mesh_color(upright, COLOR_BLUE)
        meshes.append(upright)
        
        # 脚垫
        foot = trimesh.creation.box(
            extents=[upright_width + 10, upright_depth + 10, foot_height]
        )
        foot.apply_translation([x, y, foot_height/2])
        set_mesh_color(foot, COLOR_GREY)
        meshes.append(foot)
    
    # 计算层板高度 - 均匀分布
    level_spacing = (height - 300) / (levels + 1)
    
    # 生成横梁和层板
    for level in range(1, levels + 1):
        z = 150 + level * level_spacing
        
        # 横梁（前后各一根）- 使用V2的阶梯状设计
        for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
            # 横梁上部分
            beam_top = trimesh.creation.box(
                extents=[length - 2*upright_width - 10, beam_width, beam_height/2]
            )
            beam_top.apply_translation([0, y_offset, z + beam_height/4])
            
            # 横梁下部分
            beam_bottom = trimesh.creation.box(
                extents=[length - 2*upright_width, beam_width + 5, beam_height/2]
            )
            beam_bottom.apply_translation([0, y_offset, z - beam_height/4])
            
            set_mesh_color(beam_top, COLOR_ORANGE)
            set_mesh_color(beam_bottom, COLOR_ORANGE)
            meshes.append(beam_top)
            meshes.append(beam_bottom)
        
        # 层板
        deck = trimesh.creation.box(
            extents=[length - 2*upright_width - 20, width - 2*upright_depth - 10, deck_thickness]
        )
        deck.apply_translation([0, 0, z])
        set_mesh_color(deck, COLOR_WHITE)
        meshes.append(deck)
    
    # 斜拉支撑
    for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
        diag_left = trimesh.creation.box(extents=[3, 3, height * 0.7])
        diag_left.apply_translation([-length/2 + upright_width + 20, y_offset, height/2])
        set_mesh_color(diag_left, COLOR_BLUE)
        meshes.append(diag_left)
        
        diag_right = trimesh.creation.box(extents=[3, 3, height * 0.7])
        diag_right.apply_translation([length/2 - upright_width - 20, y_offset, height/2])
        set_mesh_color(diag_right, COLOR_BLUE)
        meshes.append(diag_right)
    
    # 使用Scene并应用坐标转换
    scene = trimesh.Scene()
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    
    for i, mesh in enumerate(meshes):
        mesh.apply_transform(rotation_matrix)
        scene.add_geometry(mesh, node_name=f'part_{i}')
    
    return scene


def main():
    """主函数：生成所有模型"""
    print("=" * 50)
    print("仓酷家 3D模型生成器")
    print("=" * 50)
    
    metadata_list = []
    
    # 生成托盘
    print("\n📦 生成托盘...")
    pallet_wood, meta = generate_wooden_pallet()
    metadata_list.append(save_model(pallet_wood, "pallet-wooden-1200.glb", meta))
    
    pallet_plastic, meta = generate_plastic_pallet()
    metadata_list.append(save_model(pallet_plastic, "pallet-plastic-1200.glb", meta))
    
    # 生成周转箱
    print("\n📦 生成周转箱...")
    container, meta = generate_foldable_container()
    metadata_list.append(save_model(container, "container-foldable.glb", meta))
    
    # 生成货架
    print("\n🏗️ 生成货架...")
    shelf_heavy, meta = generate_beam_shelf(load_capacity="heavy")
    metadata_list.append(save_model(shelf_heavy, "shelf-beam-heavy.glb", meta))
    
    shelf_medium, meta = generate_beam_shelf(
        length=2000, width=800, height=3500, levels=4, load_capacity="medium"
    )
    metadata_list.append(save_model(shelf_medium, "shelf-beam-medium.glb", meta))
    
    shelf_drive, meta = generate_drive_in_shelf()
    metadata_list.append(save_model(shelf_drive, "shelf-drive-in.glb", meta))
    
    # 生成改进版轻型货架 (基于参考图片)
    print("\n🏗️ 生成轻型货架 V2 (基于参考图片)...")
    shelf_light_v2, meta = generate_light_shelf_v2()
    metadata_list.append(save_model(shelf_light_v2, "shelf-light-v2.glb", meta))
    
    # 生成3种行业标准重型货架（使用简化版函数）
    print("\n🏗️ 生成行业标准重型货架（简化版）...")
    
    # 规格1：重型3层中高位货架（适配净空5.5m仓库）- 立柱90x70，横梁120x50
    print("  - 重型3层中高位货架...")
    shelf_3level = generate_heavy_shelf_simple(
        length=2300, 
        width=1000, 
        height=4500, 
        levels=3,
        layer_heights=[1400, 1400, 1400],
        upright_size=(90, 70),
        beam_size=(120, 50)
    )
    meta_3level = {
        "id": "shelf-beam-heavy-3level-5m",
        "name": "重型横梁式货架-3层中高位",
        "category": "storage",
        "description": "适配净空5.5m仓库，单层高承重2吨，适合重货存储",
        "tags": ["重型", "3层", "中高位", "2吨承重"],
        "parameters": {
            "length": {"type": "number", "min": 2000, "max": 3000, "default": 2300, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 3500, "max": 5500, "default": 4500, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 5, "default": 3}
        }
    }
    metadata_list.append(save_model(shelf_3level, "shelf-beam-heavy-3level.glb", meta_3level))
    
    # 规格2：重型4层标准货架（适配净空7m仓库，最常用）- 立柱90x80，横梁120x50
    print("  - 重型4层标准货架...")
    shelf_4level = generate_heavy_shelf_simple(
        length=2300, 
        width=1000, 
        height=6500, 
        levels=4,
        layer_heights=[1600, 1600, 1600, 1300],
        upright_size=(90, 80),
        beam_size=(120, 50)
    )
    meta_4level = {
        "id": "shelf-beam-heavy-4level-6m",
        "name": "重型横梁式货架-4层标准库",
        "category": "storage",
        "description": "适配净空7m仓库，电商仓最常用规格，平衡型设计",
        "tags": ["重型", "4层", "标准", "电商仓常用"],
        "parameters": {
            "length": {"type": "number", "min": 2000, "max": 3000, "default": 2300, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 5000, "max": 7500, "default": 6500, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 6, "default": 4}
        }
    }
    metadata_list.append(save_model(shelf_4level, "shelf-beam-heavy-4level.glb", meta_4level))
    
    # 规格3：重型5层高位货架（适配净空9m仓库）- 立柱90x90，横梁140x50
    print("  - 重型5层高位货架...")
    shelf_5level = generate_heavy_shelf_simple(
        length=2700, 
        width=1000, 
        height=8200, 
        levels=5,
        layer_heights=[1700, 1700, 1700, 1700, 1400],
        upright_size=(90, 90),
        beam_size=(140, 50)
    )
    meta_5level = {
        "id": "shelf-beam-heavy-5level-8m",
        "name": "重型横梁式货架-5层高位立体库",
        "category": "storage",
        "description": "适配净空9m仓库，高位立体库专用，需要前移式叉车",
        "tags": ["重型", "5层", "高位", "立体库"],
        "parameters": {
            "length": {"type": "number", "min": 2300, "max": 3500, "default": 2700, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 7000, "max": 10000, "default": 8200, "unit": "mm"},
            "levels": {"type": "number", "min": 3, "max": 8, "default": 5}
        }
    }
    metadata_list.append(save_model(shelf_5level, "shelf-beam-heavy-5level.glb", meta_5level))
    
    # 生成2种中型货架（人工拣选用）- 立柱50x30，横梁80x40
    print("\n🏗️ 生成中型货架（人工拣选）...")
    
    # 规格1：中型4层货架（L2000*D600*H2500）- 立柱50x30，横梁80x40
    print("  - 中型4层货架...")
    shelf_medium_4level = generate_heavy_shelf_simple(
        length=2000, 
        width=600, 
        height=2500, 
        levels=4,
        layer_heights=[600, 600, 600, 500],
        upright_size=(50, 30),
        beam_size=(80, 40)
    )
    meta_medium_4level = {
        "id": "shelf-beam-medium-4level-2m",
        "name": "中型横梁式货架-4层人工拣选",
        "category": "storage",
        "description": "人工存取极限（配合2步登高梯），适配层高2.5m仓库",
        "tags": ["中型", "4层", "人工拣选", "登高梯"],
        "parameters": {
            "length": {"type": "number", "min": 1500, "max": 2500, "default": 2000, "unit": "mm"},
            "width": {"type": "number", "min": 400, "max": 800, "default": 600, "unit": "mm"},
            "height": {"type": "number", "min": 2000, "max": 3000, "default": 2500, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 5, "default": 4}
        }
    }
    metadata_list.append(save_model(shelf_medium_4level, "shelf-beam-medium-4level-2m.glb", meta_medium_4level))
    
    # 规格2：中型5层货架（L1500*D600*H2500）- 立柱50x30，横梁80x40
    print("  - 中型5层货架...")
    shelf_medium_5level = generate_heavy_shelf_simple(
        length=1500, 
        width=600, 
        height=2500, 
        levels=5,
        layer_heights=[500, 500, 500, 500, 400],
        upright_size=(50, 30),
        beam_size=(80, 40)
    )
    meta_medium_5level = {
        "id": "shelf-beam-medium-5level-2m",
        "name": "中型横梁式货架-5层高密度拣选",
        "category": "storage",
        "description": "高密度人工仓，层高2.5m极限，适合小件拣选",
        "tags": ["中型", "5层", "高密度", "人工仓"],
        "parameters": {
            "length": {"type": "number", "min": 1200, "max": 2000, "default": 1500, "unit": "mm"},
            "width": {"type": "number", "min": 400, "max": 800, "default": 600, "unit": "mm"},
            "height": {"type": "number", "min": 2000, "max": 3000, "default": 2500, "unit": "mm"},
            "levels": {"type": "number", "min": 3, "max": 6, "default": 5}
        }
    }
    metadata_list.append(save_model(shelf_medium_5level, "shelf-beam-medium-5level-2m.glb", meta_medium_5level))
    
    # 生成2种轻型货架 - 立柱40x30，横梁60x30
    print("\n🏗️ 生成轻型货架...")
    
    # 规格1：轻型4层货架（L1200*D400*H2000）- 立柱40x30，横梁60x30
    print("  - 轻型4层货架...")
    shelf_light_4level = generate_heavy_shelf_simple(
        length=1200, 
        width=400, 
        height=2000, 
        levels=4,
        layer_heights=[450, 450, 450, 450],
        upright_size=(40, 30),
        beam_size=(60, 30)
    )
    meta_light_4level = {
        "id": "shelf-beam-light-4level-2m",
        "name": "轻型横梁式货架-4层标准",
        "category": "storage",
        "description": "便利店后仓、办公室文件、轻型商品存储",
        "tags": ["轻型", "4层", "标准", "人工存取"],
        "parameters": {
            "length": {"type": "number", "min": 800, "max": 1500, "default": 1200, "unit": "mm"},
            "width": {"type": "number", "min": 300, "max": 500, "default": 400, "unit": "mm"},
            "height": {"type": "number", "min": 1500, "max": 2500, "default": 2000, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 5, "default": 4}
        }
    }
    metadata_list.append(save_model(shelf_light_4level, "shelf-beam-light-4level.glb", meta_light_4level))
    
    # 规格2：轻型5层货架（L1200*D500*H2000）- 立柱40x30，横梁60x30
    print("  - 轻型5层货架...")
    shelf_light_5level = generate_heavy_shelf_simple(
        length=1200, 
        width=500, 
        height=2000, 
        levels=5,
        layer_heights=[360, 360, 360, 360, 360],
        upright_size=(40, 30),
        beam_size=(60, 30)
    )
    meta_light_5level = {
        "id": "shelf-beam-light-5level-2m",
        "name": "轻型横梁式货架-5层宽型",
        "category": "storage",
        "description": "电商小件仓、配件仓、图书档案、多SKU轻货",
        "tags": ["轻型", "5层", "宽型", "高密度"],
        "parameters": {
            "length": {"type": "number", "min": 800, "max": 1500, "default": 1200, "unit": "mm"},
            "width": {"type": "number", "min": 400, "max": 600, "default": 500, "unit": "mm"},
            "height": {"type": "number", "min": 1500, "max": 2500, "default": 2000, "unit": "mm"},
            "levels": {"type": "number", "min": 3, "max": 6, "default": 5}
        }
    }
    metadata_list.append(save_model(shelf_light_5level, "shelf-beam-light-5level.glb", meta_light_5level))
    
    # 保存元数据
    print("\n📝 保存元数据...")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！共生成 {len(metadata_list)} 个模型")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"📄 元数据文件: {METADATA_FILE}")


if __name__ == "__main__":
    main()
