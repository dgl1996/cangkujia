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
    
    # 坐标转换：Trimesh(Z轴向上) -> Three.js(Y轴向上)
    # 使托盘平躺（高度方向变为Y轴）
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    pallet.apply_transform(rotation_matrix)
    
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
    
    # 坐标转换：Trimesh(Z轴向上) -> Three.js(Y轴向上)
    # 使托盘平躺（高度方向变为Y轴）
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    pallet.apply_transform(rotation_matrix)
    
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


def generate_flow_shelf(length=900, width=450, height=1800, levels=4):
    """
    生成流利式货架 - 带倾斜流利条层板
    
    Args:
        length: 货架长度 (mm)
        width: 货架深度 (mm)  
        height: 货架高度 (mm)
        levels: 层数
    """
    meshes = []
    
    # 颜色定义 - 薄荷绿主题
    COLOR_UPRIGHT = [0.31, 0.89, 0.76]   # 薄荷绿 #50E3C2
    COLOR_BEAM = [0.9, 0.4, 0.1]         # 橙红色
    COLOR_ROLLER = [0.75, 0.75, 0.75]    # 银灰色流利条
    COLOR_FOOT = [0.3, 0.3, 0.3]         # 深灰色脚垫
    
    # 尺寸参数
    upright_width = 40
    upright_depth = 30
    beam_height = 60
    beam_width = 30
    foot_height = 30
    tilt_angle = 5  # 倾斜角度5度
    
    # 立柱位置（4根）
    upright_positions = [
        [-length/2 + upright_width/2, -width/2 + upright_depth/2],
        [length/2 - upright_width/2, -width/2 + upright_depth/2],
        [-length/2 + upright_width/2, width/2 - upright_depth/2],
        [length/2 - upright_width/2, width/2 - upright_depth/2]
    ]
    
    # 生成立柱和脚垫
    for i, (x, y) in enumerate(upright_positions):
        # 主立柱
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height - foot_height]
        )
        upright.apply_translation([x, y, (height - foot_height)/2 + foot_height])
        set_mesh_color(upright, COLOR_UPRIGHT)
        meshes.append((f'upright_{i}', upright))
        
        # 脚垫
        foot = trimesh.creation.box(
            extents=[upright_width + 10, upright_depth + 10, foot_height]
        )
        foot.apply_translation([x, y, foot_height/2])
        set_mesh_color(foot, COLOR_FOOT)
        meshes.append((f'foot_{i}', foot))
    
    # 计算层板高度 - 均匀分布
    level_spacing = (height - 300) / (levels + 1)
    
    # 生成横梁和流利条层板
    for level in range(1, levels + 1):
        # 后端高度（较高）
        z_back = 150 + level * level_spacing + 20
        # 前端高度（较低，倾斜5度）
        z_front = z_back - width * np.sin(np.radians(tilt_angle))
        
        # 后横梁（较高位置）
        back_beam = trimesh.creation.box(
            extents=[length - 2*upright_width, beam_width, beam_height]
        )
        back_beam.apply_translation([0, -width/2 + upright_depth/2, z_back])
        set_mesh_color(back_beam, COLOR_BEAM)
        meshes.append((f'beam_back_{level}', back_beam))
        
        # 前横梁（较低位置）
        front_beam = trimesh.creation.box(
            extents=[length - 2*upright_width, beam_width, beam_height]
        )
        front_beam.apply_translation([0, width/2 - upright_depth/2, z_front])
        set_mesh_color(front_beam, COLOR_BEAM)
        meshes.append((f'beam_front_{level}', front_beam))
        
        # 流利条（倾斜的圆柱体表示）
        num_rollers = 8
        roller_diameter = 15
        roller_length = length - 2*upright_width - 20
        
        for i in range(num_rollers):
            y_pos = -width/2 + upright_depth + (width - 2*upright_depth) * (i + 0.5) / num_rollers
            # 根据Y位置计算Z高度（线性插值）
            ratio = (y_pos - (-width/2 + upright_depth)) / (width - 2*upright_depth)
            z_pos = z_back - (z_back - z_front) * ratio
            
            roller = trimesh.creation.cylinder(
                radius=roller_diameter/2,
                height=roller_length
            )
            # 旋转圆柱体使其沿X轴
            roller.apply_transform(trimesh.transformations.rotation_matrix(
                angle=np.pi/2, direction=[0, 1, 0], point=[0, 0, 0]
            ))
            roller.apply_translation([0, y_pos, z_pos])
            set_mesh_color(roller, COLOR_ROLLER)
            meshes.append((f'roller_{level}_{i}', roller))
    
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
    
    return scene


def generate_wooden_pallet_standard(length=1200, width=1000, height=144):
    """
    生成木质标准托盘（双向进叉）
    标准款：5块顶板 + 3根纵梁 + 3块底板
    """
    meshes = []
    
    # 颜色 - 棕色木质
    COLOR_WOOD = [0.63, 0.32, 0.18]  # #A0522D
    
    # 尺寸参数
    board_thickness = 22
    stringer_width = 100
    stringer_height = height - board_thickness * 2
    
    # 顶板 (5块，沿宽度方向排列)
    top_board_width = width / 5
    for i in range(5):
        y_pos = -width/2 + top_board_width/2 + i * top_board_width
        board = trimesh.creation.box(
            extents=[length, top_board_width - 5, board_thickness]
        )
        board.apply_translation([0, y_pos, height - board_thickness/2])
        set_mesh_color(board, COLOR_WOOD)
        meshes.append(board)
    
    # 纵梁 (3根，沿长度方向)
    stringer_positions = [-length/3, 0, length/3]
    for x_pos in stringer_positions:
        stringer = trimesh.creation.box(
            extents=[stringer_width, width, stringer_height]
        )
        stringer.apply_translation([x_pos, 0, board_thickness + stringer_height/2])
        set_mesh_color(stringer, COLOR_WOOD)
        meshes.append(stringer)
    
    # 底板 (3块，双向进叉开口)
    bottom_board_width = width / 3
    for i in range(3):
        y_pos = -width/2 + bottom_board_width/2 + i * bottom_board_width
        board = trimesh.creation.box(
            extents=[length, bottom_board_width - 20, board_thickness]
        )
        board.apply_translation([0, y_pos, board_thickness/2])
        set_mesh_color(board, COLOR_WOOD)
        meshes.append(board)
    
    # 合并并旋转
    pallet = trimesh.util.concatenate(meshes)
    
    # 坐标转换
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    pallet.apply_transform(rotation_matrix)
    
    return pallet, {
        "id": "pallet-wood-1200x1000",
        "name": "木质托盘-标准双向",
        "category": "containers",
        "description": "标准欧标木质托盘，双向进叉，5块面板+3根纵梁结构",
        "tags": ["木质", "标准", "双向进叉", "GB/T 2934-2007"],
        "parameters": {
            "length": {"type": "number", "min": 1000, "max": 1400, "default": 1200, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 120, "max": 160, "default": 144, "unit": "mm"}
        }
    }


def generate_plastic_pallet_grid(length=1200, width=1000, height=150):
    """
    生成塑料网格托盘（四向进叉，双面）
    HDPE材质，网格结构，四面开口
    """
    meshes = []
    
    # 颜色 - 蓝色塑料
    COLOR_PLASTIC = [0.23, 0.51, 0.96]  # #3B82F6
    
    # 尺寸参数
    deck_thickness = 25
    foot_height = height - deck_thickness * 2
    
    # 顶面（网格状 - 用多个小方块模拟）
    grid_size = 80
    grid_thickness = 5
    for i in range(int(length/grid_size)):
        for j in range(int(width/grid_size)):
            x_pos = -length/2 + grid_size/2 + i * grid_size
            y_pos = -width/2 + grid_size/2 + j * grid_size
            # 网格交叉点
            grid_cell = trimesh.creation.box(
                extents=[grid_size-10, grid_size-10, deck_thickness]
            )
            grid_cell.apply_translation([x_pos, y_pos, height - deck_thickness/2])
            set_mesh_color(grid_cell, COLOR_PLASTIC)
            meshes.append(grid_cell)
    
    # 底面（同样网格结构）
    for i in range(int(length/grid_size)):
        for j in range(int(width/grid_size)):
            x_pos = -length/2 + grid_size/2 + i * grid_size
            y_pos = -width/2 + grid_size/2 + j * grid_size
            grid_cell = trimesh.creation.box(
                extents=[grid_size-10, grid_size-10, deck_thickness]
            )
            grid_cell.apply_translation([x_pos, y_pos, deck_thickness/2])
            set_mesh_color(grid_cell, COLOR_PLASTIC)
            meshes.append(grid_cell)
    
    # 支撑脚（9个，四向开口）
    foot_positions = [
        [-length/3, -width/3], [0, -width/3], [length/3, -width/3],
        [-length/3, 0], [0, 0], [length/3, 0],
        [-length/3, width/3], [0, width/3], [length/3, width/3]
    ]
    
    foot_size = 80
    for x, y in foot_positions:
        foot = trimesh.creation.box(
            extents=[foot_size, foot_size, foot_height]
        )
        foot.apply_translation([x, y, deck_thickness + foot_height/2])
        set_mesh_color(foot, COLOR_PLASTIC)
        meshes.append(foot)
    
    # 合并并旋转
    pallet = trimesh.util.concatenate(meshes)
    
    # 坐标转换
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    pallet.apply_transform(rotation_matrix)
    
    return pallet, {
        "id": "pallet-plastic-1200x1000",
        "name": "塑料托盘-网格双面",
        "category": "containers",
        "description": "HDPE塑料托盘，双面网格结构，四向进叉，防潮防腐蚀",
        "tags": ["塑料", "HDPE", "四向进叉", "双面", "网格"],
        "parameters": {
            "length": {"type": "number", "min": 1000, "max": 1400, "default": 1200, "unit": "mm"},
            "width": {"type": "number", "min": 800, "max": 1200, "default": 1000, "unit": "mm"},
            "height": {"type": "number", "min": 130, "max": 170, "default": 150, "unit": "mm"}
        }
    }


def generate_tote_box(length=600, width=400, height=300, color=None):
    """
    生成可堆叠周转箱（EU箱标准）
    
    Args:
        length: 长度 (mm)
        width: 宽度 (mm)
        height: 高度 (mm)
        color: 颜色RGB列表，默认根据尺寸自动选择
    """
    meshes = []
    
    # 根据尺寸选择颜色
    if color is None:
        if length >= 600:
            COLOR_BOX = [0.29, 0.56, 0.89]  # 蓝色 #4A90E2
        else:
            COLOR_BOX = [0.96, 0.68, 0.33]  # 橙色 #F6AD55
    else:
        COLOR_BOX = color
    
    # 壁厚
    wall_thickness = 8
    
    # 外框（底部）
    bottom = trimesh.creation.box(
        extents=[length, width, wall_thickness]
    )
    bottom.apply_translation([0, 0, wall_thickness/2])
    set_mesh_color(bottom, COLOR_BOX)
    meshes.append(bottom)
    
    # 四壁
    # 前壁
    front_wall = trimesh.creation.box(
        extents=[length, wall_thickness, height]
    )
    front_wall.apply_translation([0, -width/2 + wall_thickness/2, height/2])
    set_mesh_color(front_wall, COLOR_BOX)
    meshes.append(front_wall)
    
    # 后壁
    back_wall = trimesh.creation.box(
        extents=[length, wall_thickness, height]
    )
    back_wall.apply_translation([0, width/2 - wall_thickness/2, height/2])
    set_mesh_color(back_wall, COLOR_BOX)
    meshes.append(back_wall)
    
    # 左壁
    left_wall = trimesh.creation.box(
        extents=[wall_thickness, width - 2*wall_thickness, height]
    )
    left_wall.apply_translation([-length/2 + wall_thickness/2, 0, height/2])
    set_mesh_color(left_wall, COLOR_BOX)
    meshes.append(left_wall)
    
    # 右壁
    right_wall = trimesh.creation.box(
        extents=[wall_thickness, width - 2*wall_thickness, height]
    )
    right_wall.apply_translation([length/2 - wall_thickness/2, 0, height/2])
    set_mesh_color(right_wall, COLOR_BOX)
    meshes.append(right_wall)
    
    # 加强筋（侧面）
    rib_count = 3
    for i in range(rib_count):
        y_pos = -width/2 + wall_thickness + (width - 2*wall_thickness) * (i + 0.5) / rib_count
        # 左侧面加强筋
        rib_left = trimesh.creation.box(
            extents=[wall_thickness + 5, 20, height * 0.8]
        )
        rib_left.apply_translation([-length/2 + wall_thickness/2, y_pos, height * 0.4])
        set_mesh_color(rib_left, COLOR_BOX)
        meshes.append(rib_left)
        
        # 右侧面加强筋
        rib_right = trimesh.creation.box(
            extents=[wall_thickness + 5, 20, height * 0.8]
        )
        rib_right.apply_translation([length/2 - wall_thickness/2, y_pos, height * 0.4])
        set_mesh_color(rib_right, COLOR_BOX)
        meshes.append(rib_right)
    
    # 把手（侧面凹槽）- 用稍暗的颜色表示
    COLOR_HANDLE = [c * 0.8 for c in COLOR_BOX]
    handle_width = 80
    handle_height = 30
    # 左侧把手
    handle_left = trimesh.creation.box(
        extents=[wall_thickness + 2, handle_width, handle_height]
    )
    handle_left.apply_translation([-length/2 + wall_thickness/2, 0, height * 0.6])
    set_mesh_color(handle_left, COLOR_HANDLE)
    meshes.append(handle_left)
    
    # 右侧把手
    handle_right = trimesh.creation.box(
        extents=[wall_thickness + 2, handle_width, handle_height]
    )
    handle_right.apply_translation([length/2 - wall_thickness/2, 0, height * 0.6])
    set_mesh_color(handle_right, COLOR_HANDLE)
    meshes.append(handle_right)
    
    # 标签卡槽（前面）
    label_slot = trimesh.creation.box(
        extents=[60, wall_thickness + 2, 30]
    )
    label_slot.apply_translation([0, -width/2 + wall_thickness/2, height * 0.75])
    set_mesh_color(label_slot, [c * 0.9 for c in COLOR_BOX])
    meshes.append(label_slot)
    
    # 合并所有部件
    box = trimesh.util.concatenate(meshes)
    
    # 坐标转换
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    box.apply_transform(rotation_matrix)
    
    return box


def generate_reach_truck(length=2900, width=1100, height=2500, lift_height=9000):
    """
    生成前移式叉车（Reach Truck）
    窄通道高位存取专用，适配重型5层立体库
    
    Args:
        length: 车身总长（含货叉）
        width: 车身宽度
        height: 门架收起时高度
        lift_height: 最大举升高度
    """
    meshes = []
    
    # 颜色定义
    COLOR_ORANGE = [0.96, 0.62, 0.04]    # 工业橙 #F59E0B
    COLOR_BLACK = [0.15, 0.15, 0.15]      # 黑色部件
    COLOR_GREY = [0.4, 0.4, 0.4]          # 灰色金属
    COLOR_SILVER = [0.75, 0.75, 0.75]     # 银色货叉
    
    # 尺寸参数
    body_length = 1700      # 车身长度（不含货叉）
    body_width = width
    body_height = 1400      # 车身高度
    mast_height = height - 500  # 门架高度
    fork_length = 1200      # 货叉长度
    fork_width = 100        # 货叉宽度
    fork_thickness = 40     # 货叉厚度
    
    # 1. 车身主体（橙色）
    body = trimesh.creation.box(
        extents=[body_length, body_width, body_height]
    )
    body.apply_translation([fork_length/2, 0, body_height/2 + 300])
    set_mesh_color(body, COLOR_ORANGE)
    meshes.append(('body', body))
    
    # 2. 驾驶室顶棚
    roof = trimesh.creation.box(
        extents=[800, body_width - 50, 50]
    )
    roof.apply_translation([fork_length/2 + 200, 0, height - 100])
    set_mesh_color(roof, COLOR_ORANGE)
    meshes.append(('roof', roof))
    
    # 3. 驾驶室立柱（4根）
    pillar_positions = [
        [fork_length/2 - 300, -body_width/2 + 50],
        [fork_length/2 - 300, body_width/2 - 50],
        [fork_length/2 + 300, -body_width/2 + 50],
        [fork_length/2 + 300, body_width/2 - 50]
    ]
    for i, (x, y) in enumerate(pillar_positions):
        pillar = trimesh.creation.box(
            extents=[50, 50, height - body_height - 300]
        )
        pillar.apply_translation([x, y, body_height + 300 + (height - body_height - 300)/2])
        set_mesh_color(pillar, COLOR_ORANGE)
        meshes.append((f'pillar_{i}', pillar))
    
    # 4. 门架（黑色，3节结构）
    mast_width = 300
    mast_depth = 150
    
    # 外门架
    mast_outer = trimesh.creation.box(
        extents=[mast_depth, mast_width, mast_height]
    )
    mast_outer.apply_translation([0, 0, mast_height/2 + 300])
    set_mesh_color(mast_outer, COLOR_BLACK)
    meshes.append(('mast_outer', mast_outer))
    
    # 中门架（稍短）
    mast_middle = trimesh.creation.box(
        extents=[mast_depth - 20, mast_width - 20, mast_height * 0.85]
    )
    mast_middle.apply_translation([0, 0, mast_height * 0.85/2 + 400])
    set_mesh_color(mast_middle, COLOR_GREY)
    meshes.append(('mast_middle', mast_middle))
    
    # 内门架（最短）
    mast_inner = trimesh.creation.box(
        extents=[mast_depth - 40, mast_width - 40, mast_height * 0.7]
    )
    mast_inner.apply_translation([0, 0, mast_height * 0.7/2 + 500])
    set_mesh_color(mast_inner, COLOR_BLACK)
    meshes.append(('mast_inner', mast_inner))
    
    # 5. 货叉架
    carriage = trimesh.creation.box(
        extents=[100, mast_width + 50, 200]
    )
    carriage.apply_translation([0, 0, 800])
    set_mesh_color(carriage, COLOR_GREY)
    meshes.append(('carriage', carriage))
    
    # 6. 货叉（2根，银色）
    fork_spacing = 300
    for i, y_offset in enumerate([-fork_spacing/2, fork_spacing/2]):
        fork = trimesh.creation.box(
            extents=[fork_length, fork_width, fork_thickness]
        )
        fork.apply_translation([-fork_length/2, y_offset, 750])
        set_mesh_color(fork, COLOR_SILVER)
        meshes.append((f'fork_{i}', fork))
    
    # 7. 后轮（2个）
    wheel_radius = 150
    wheel_width = 80
    for i, x_offset in enumerate([fork_length/2 + 600, fork_length/2 + 1200]):
        wheel = trimesh.creation.cylinder(
            radius=wheel_radius,
            height=wheel_width
        )
        wheel.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
        ))
        wheel.apply_translation([x_offset, -body_width/2 - wheel_width/2, wheel_radius])
        set_mesh_color(wheel, COLOR_BLACK)
        meshes.append((f'wheel_left_{i}', wheel))
        
        wheel_right = trimesh.creation.cylinder(
            radius=wheel_radius,
            height=wheel_width
        )
        wheel_right.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
        ))
        wheel_right.apply_translation([x_offset, body_width/2 + wheel_width/2, wheel_radius])
        set_mesh_color(wheel_right, COLOR_BLACK)
        meshes.append((f'wheel_right_{i}', wheel_right))
    
    # 8. 前轮（2个，转向轮）
    front_wheel_radius = 100
    for i, y_offset in enumerate([-150, 150]):
        wheel = trimesh.creation.cylinder(
            radius=front_wheel_radius,
            height=60
        )
        wheel.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
        ))
        wheel.apply_translation([fork_length/2 + 1400, y_offset, front_wheel_radius])
        set_mesh_color(wheel, COLOR_BLACK)
        meshes.append((f'front_wheel_{i}', wheel))
    
    # 9. 配重块（后部）
    counterweight = trimesh.creation.box(
        extents=[400, body_width - 100, 800]
    )
    counterweight.apply_translation([fork_length/2 + body_length - 300, 0, 700])
    set_mesh_color(counterweight, COLOR_GREY)
    meshes.append(('counterweight', counterweight))
    
    # 10. 警示灯（顶部）
    light = trimesh.creation.cylinder(radius=30, height=50)
    light.apply_translation([fork_length/2 + 200, 0, height + 25])
    set_mesh_color(light, [1.0, 0.0, 0.0])  # 红色警示灯
    meshes.append(('warning_light', light))
    
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
    
    return scene


def generate_counterbalance_forklift(length=3200, width=1200, height=2200, lift_height=4000):
    """
    生成平衡重叉车（Counterbalance Forklift）
    通用型搬运设备，适合室内外作业，适配重型3-4层货架
    
    Args:
        length: 车身总长（含货叉）
        width: 车身宽度
        height: 门架收起时高度
        lift_height: 最大举升高度
    """
    meshes = []
    
    # 颜色定义
    COLOR_YELLOW = [0.98, 0.80, 0.08]     # 柠檬黄 #FACC15
    COLOR_BLACK = [0.15, 0.15, 0.15]       # 黑色部件
    COLOR_GREY = [0.4, 0.4, 0.4]           # 灰色金属
    COLOR_SILVER = [0.75, 0.75, 0.75]      # 银色货叉
    COLOR_TIRE = [0.2, 0.2, 0.2]           # 轮胎黑色
    
    # 尺寸参数
    body_length = 2000      # 车身长度（不含货叉和后悬）
    body_width = width
    body_height = 1600      # 车身高度
    mast_height = height - 400  # 门架高度
    fork_length = 1220      # 货叉长度
    fork_width = 120        # 货叉宽度
    fork_thickness = 45     # 货叉厚度
    rear_overhang = 550     # 后悬长度（配重块）
    
    # 1. 车身主体（柠檬黄）
    body = trimesh.creation.box(
        extents=[body_length, body_width, body_height]
    )
    body.apply_translation([fork_length + body_length/2 - 200, 0, body_height/2 + 300])
    set_mesh_color(body, COLOR_YELLOW)
    meshes.append(('body', body))
    
    # 2. 配重块（后部黑色，视觉特征明显）
    counterweight = trimesh.creation.box(
        extents=[rear_overhang, body_width - 50, 1000]
    )
    counterweight.apply_translation([fork_length + body_length + rear_overhang/2 - 200, 0, 800])
    set_mesh_color(counterweight, COLOR_BLACK)
    meshes.append(('counterweight', counterweight))
    
    # 3. 驾驶室顶棚
    roof = trimesh.creation.box(
        extents=[600, body_width - 50, 50]
    )
    roof.apply_translation([fork_length + 400, 0, height - 50])
    set_mesh_color(roof, COLOR_BLACK)
    meshes.append(('roof', roof))
    
    # 4. 驾驶室立柱（4根）
    pillar_positions = [
        [fork_length + 100, -body_width/2 + 50],
        [fork_length + 100, body_width/2 - 50],
        [fork_length + 600, -body_width/2 + 50],
        [fork_length + 600, body_width/2 - 50]
    ]
    for i, (x, y) in enumerate(pillar_positions):
        pillar = trimesh.creation.box(
            extents=[50, 50, height - body_height - 200]
        )
        pillar.apply_translation([x, y, body_height + 200 + (height - body_height - 200)/2])
        set_mesh_color(pillar, COLOR_BLACK)
        meshes.append((f'pillar_{i}', pillar))
    
    # 5. 座椅
    seat = trimesh.creation.box(
        extents=[300, 250, 400]
    )
    seat.apply_translation([fork_length + 400, 0, 600])
    set_mesh_color(seat, [0.3, 0.3, 0.4])  # 深灰色座椅
    meshes.append(('seat', seat))
    
    # 6. 门架（黑色，2级结构）
    mast_width = 400
    mast_depth = 180
    
    # 外门架
    mast_outer = trimesh.creation.box(
        extents=[mast_depth, mast_width, mast_height]
    )
    mast_outer.apply_translation([0, 0, mast_height/2 + 300])
    set_mesh_color(mast_outer, COLOR_BLACK)
    meshes.append(('mast_outer', mast_outer))
    
    # 内门架（稍短）
    mast_inner = trimesh.creation.box(
        extents=[mast_depth - 30, mast_width - 30, mast_height * 0.8]
    )
    mast_inner.apply_translation([0, 0, mast_height * 0.8/2 + 400])
    set_mesh_color(mast_inner, COLOR_GREY)
    meshes.append(('mast_inner', mast_inner))
    
    # 7. 货叉架
    carriage = trimesh.creation.box(
        extents=[120, mast_width + 60, 250]
    )
    carriage.apply_translation([0, 0, 700])
    set_mesh_color(carriage, COLOR_GREY)
    meshes.append(('carriage', carriage))
    
    # 8. 货叉（2根，银色）
    fork_spacing = 360
    for i, y_offset in enumerate([-fork_spacing/2, fork_spacing/2]):
        fork = trimesh.creation.box(
            extents=[fork_length, fork_width, fork_thickness]
        )
        fork.apply_translation([-fork_length/2, y_offset, 650])
        set_mesh_color(fork, COLOR_SILVER)
        meshes.append((f'fork_{i}', fork))
    
    # 9. 前轮（2个，大轮胎）
    front_wheel_radius = 200
    front_wheel_width = 150
    for i, y_offset in enumerate([-body_width/2 + 100, body_width/2 - 100]):
        wheel = trimesh.creation.cylinder(
            radius=front_wheel_radius,
            height=front_wheel_width
        )
        wheel.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
        ))
        wheel.apply_translation([fork_length + 300, y_offset, front_wheel_radius])
        set_mesh_color(wheel, COLOR_TIRE)
        meshes.append((f'front_wheel_{i}', wheel))
    
    # 10. 后轮（2个，转向轮，稍小）
    rear_wheel_radius = 180
    rear_wheel_width = 120
    for i, y_offset in enumerate([-body_width/2 + 80, body_width/2 - 80]):
        wheel = trimesh.creation.cylinder(
            radius=rear_wheel_radius,
            height=rear_wheel_width
        )
        wheel.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
        ))
        wheel.apply_translation([fork_length + body_length - 200, y_offset, rear_wheel_radius])
        set_mesh_color(wheel, COLOR_TIRE)
        meshes.append((f'rear_wheel_{i}', wheel))
    
    # 11. 警示灯（顶部）
    light = trimesh.creation.cylinder(radius=40, height=60)
    light.apply_translation([fork_length + 400, 0, height + 30])
    set_mesh_color(light, [1.0, 0.0, 0.0])  # 红色警示灯
    meshes.append(('warning_light', light))
    
    # 12. 后视镜（2个）
    for i, y_offset in enumerate([-body_width/2 - 50, body_width/2 + 50]):
        mirror_stem = trimesh.creation.cylinder(radius=8, height=150)
        mirror_stem.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[0, 1, 0], point=[0, 0, 0]
        ))
        mirror_stem.apply_translation([fork_length + 150, y_offset, 1400])
        set_mesh_color(mirror_stem, COLOR_BLACK)
        meshes.append((f'mirror_stem_{i}', mirror_stem))
        
        mirror = trimesh.creation.box(extents=[80, 10, 60])
        mirror.apply_translation([fork_length + 100, y_offset * 1.3, 1400])
        set_mesh_color(mirror, COLOR_BLACK)
        meshes.append((f'mirror_{i}', mirror))
    
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
    
    return scene


def generate_electric_pallet_truck(length=1850, width=680, height=1350):
    """
    生成电动搬运车（Electric Pallet Truck）
    平库及重型货架底层搬运专用，步行式操作，适合短距离水平搬运
    
    Args:
        length: 总长（含货叉）
        width: 货叉外宽
        height: 手柄立起时高度
    """
    meshes = []
    
    # 颜色定义
    COLOR_RED = [0.94, 0.27, 0.27]       # 中国红 #EF4444
    COLOR_BLACK = [0.15, 0.15, 0.15]      # 黑色部件
    COLOR_GREY = [0.4, 0.4, 0.4]          # 灰色金属
    COLOR_SILVER = [0.75, 0.75, 0.75]     # 银色货叉
    COLOR_TIRE = [0.25, 0.25, 0.25]       # 轮胎灰色
    
    # 尺寸参数
    body_length = 700       # 车身长度（不含货叉）
    body_width = 200        # 车身宽度
    body_height = 400       # 车身高度
    fork_length = 1150      # 货叉长度
    fork_width = 80         # 单根货叉宽度
    fork_thickness = 50     # 货叉厚度
    fork_spacing = 540      # 货叉间距
    
    # 1. 车身主体（红色）
    body = trimesh.creation.box(
        extents=[body_length, body_width, body_height]
    )
    body.apply_translation([fork_length + body_length/2, 0, body_height/2 + 100])
    set_mesh_color(body, COLOR_RED)
    meshes.append(('body', body))
    
    # 2. 电瓶箱盖（顶部黑色）
    battery_cover = trimesh.creation.box(
        extents=[body_length - 100, body_width - 20, 30]
    )
    battery_cover.apply_translation([fork_length + body_length/2, 0, body_height + 100 + 15])
    set_mesh_color(battery_cover, COLOR_BLACK)
    meshes.append(('battery_cover', battery_cover))
    
    # 3. 立式手柄（Tiller Head）- 长杆
    handle_stem = trimesh.creation.cylinder(radius=25, height=800)
    handle_stem.apply_translation([fork_length + body_length - 100, 0, body_height + 100 + 400])
    set_mesh_color(handle_stem, COLOR_BLACK)
    meshes.append(('handle_stem', handle_stem))
    
    # 4. 手柄头（控制面板）
    handle_head = trimesh.creation.box(extents=[150, 200, 80])
    handle_head.apply_translation([fork_length + body_length - 100, 0, body_height + 100 + 800 + 40])
    set_mesh_color(handle_head, COLOR_BLACK)
    meshes.append(('handle_head', handle_head))
    
    # 5. 手柄握把（两侧）
    for i, y_offset in enumerate([-80, 80]):
        grip = trimesh.creation.cylinder(radius=20, height=120)
        grip.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[0, 1, 0], point=[0, 0, 0]
        ))
        grip.apply_translation([fork_length + body_length - 100, y_offset, body_height + 100 + 800 + 40])
        set_mesh_color(grip, COLOR_BLACK)
        meshes.append((f'handle_grip_{i}', grip))
    
    # 6. 货叉（2根，银色）
    for i, y_offset in enumerate([-fork_spacing/2, fork_spacing/2]):
        fork = trimesh.creation.box(
            extents=[fork_length, fork_width, fork_thickness]
        )
        fork.apply_translation([fork_length/2, y_offset, fork_thickness/2 + 85])
        set_mesh_color(fork, COLOR_SILVER)
        meshes.append((f'fork_{i}', fork))
    
    # 7. 货叉滚轮（每个货叉2个）
    wheel_radius = 40
    for i, y_offset in enumerate([-fork_spacing/2, fork_spacing/2]):
        for j, x_offset in enumerate([200, fork_length - 100]):
            wheel = trimesh.creation.cylinder(radius=wheel_radius, height=20)
            wheel.apply_transform(trimesh.transformations.rotation_matrix(
                angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
            ))
            wheel.apply_translation([x_offset, y_offset, wheel_radius])
            set_mesh_color(wheel, COLOR_TIRE)
            meshes.append((f'fork_wheel_{i}_{j}', wheel))
    
    # 8. 驱动轮（车身底部中央）
    drive_wheel_radius = 100
    drive_wheel = trimesh.creation.cylinder(radius=drive_wheel_radius, height=80)
    drive_wheel.apply_transform(trimesh.transformations.rotation_matrix(
        angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
    ))
    drive_wheel.apply_translation([fork_length + body_length/2, 0, drive_wheel_radius])
    set_mesh_color(drive_wheel, COLOR_TIRE)
    meshes.append(('drive_wheel', drive_wheel))
    
    # 9. 辅助轮（车身两侧）
    for i, y_offset in enumerate([-120, 120]):
        aux_wheel = trimesh.creation.cylinder(radius=60, height=40)
        aux_wheel.apply_transform(trimesh.transformations.rotation_matrix(
            angle=np.pi/2, direction=[1, 0, 0], point=[0, 0, 0]
        ))
        aux_wheel.apply_translation([fork_length + body_length/2 + 100, y_offset, 60])
        set_mesh_color(aux_wheel, COLOR_TIRE)
        meshes.append((f'aux_wheel_{i}', aux_wheel))
    
    # 10. 紧急停止按钮（红色圆形）
    e_stop = trimesh.creation.cylinder(radius=30, height=20)
    e_stop.apply_translation([fork_length + body_length - 50, 0, body_height + 100 + 30])
    set_mesh_color(e_stop, [0.9, 0.1, 0.1])  # 鲜红色
    meshes.append(('e_stop', e_stop))
    
    # 11. 电量表（车身侧面）
    battery_indicator = trimesh.creation.box(extents=[80, 10, 40])
    battery_indicator.apply_translation([fork_length + body_length/2, body_width/2 + 5, body_height/2 + 100])
    set_mesh_color(battery_indicator, [0.2, 0.8, 0.2])  # 绿色表示电量
    meshes.append(('battery_indicator', battery_indicator))
    
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
    
    # 生成流利式货架
    print("\n🏗️ 生成流利式货架...")
    print("  - 流利式4层拣选货架...")
    shelf_flow = generate_flow_shelf(
        length=900, 
        width=450, 
        height=1800, 
        levels=4
    )
    meta_flow = {
        "id": "shelf-flow-4level-1m8",
        "name": "流利式货架-4层拣选",
        "category": "storage",
        "description": "先进先出(FIFO)拣选作业，配送中心产线旁供料",
        "tags": ["流利式", "4层", "FIFO", "拣选"],
        "parameters": {
            "length": {"type": "number", "min": 600, "max": 1200, "default": 900, "unit": "mm"},
            "width": {"type": "number", "min": 300, "max": 600, "default": 450, "unit": "mm"},
            "height": {"type": "number", "min": 1200, "max": 2500, "default": 1800, "unit": "mm"},
            "levels": {"type": "number", "min": 2, "max": 6, "default": 4}
        }
    }
    metadata_list.append(save_model(shelf_flow, "shelf-flow-4level.glb", meta_flow))
    
    # 生成新托盘
    print("\n📦 生成新托盘...")
    
    # 规格1：木质托盘（双向进叉，标准款）
    print("  - 木质标准托盘...")
    pallet_wood_std, meta_wood_std = generate_wooden_pallet_standard()
    metadata_list.append(save_model(pallet_wood_std, "pallet-wood-1200x1000.glb", meta_wood_std))
    
    # 规格2：塑料托盘（网格双面，四向进叉）
    print("  - 塑料网格托盘...")
    pallet_plastic_grid, meta_plastic_grid = generate_plastic_pallet_grid()
    metadata_list.append(save_model(pallet_plastic_grid, "pallet-plastic-1200x1000.glb", meta_plastic_grid))
    
    # 生成周转箱
    print("\n📦 生成周转箱...")
    
    # 规格1：大型周转箱 600×400×300（适配中型货架）
    print("  - 大型周转箱 600×400×300...")
    tote_large = generate_tote_box(length=600, width=400, height=300)
    meta_tote_large = {
        "id": "container-tote-600x400x300",
        "name": "可堆叠周转箱-600×400×300",
        "category": "containers",
        "description": "EU标准周转箱，适配中型货架，可堆叠4层",
        "tags": ["周转箱", "EU标准", "可堆叠", "蓝色"],
        "parameters": {
            "length": {"type": "number", "min": 500, "max": 700, "default": 600, "unit": "mm"},
            "width": {"type": "number", "min": 300, "max": 500, "default": 400, "unit": "mm"},
            "height": {"type": "number", "min": 200, "max": 400, "default": 300, "unit": "mm"}
        }
    }
    metadata_list.append(save_model(tote_large, "container-tote-600x400.glb", meta_tote_large))
    
    # 规格2：标准周转箱 600×400×220（适配流利式货架）
    print("  - 标准周转箱 600×400×220...")
    tote_medium = generate_tote_box(length=600, width=400, height=220)
    meta_tote_medium = {
        "id": "container-tote-600x400x220",
        "name": "可堆叠周转箱-600×400×220",
        "category": "containers",
        "description": "EU标准矮型周转箱，适配流利式货架，可堆叠5层",
        "tags": ["周转箱", "EU标准", "矮型", "流利式", "蓝色"],
        "parameters": {
            "length": {"type": "number", "min": 500, "max": 700, "default": 600, "unit": "mm"},
            "width": {"type": "number", "min": 300, "max": 500, "default": 400, "unit": "mm"},
            "height": {"type": "number", "min": 150, "max": 300, "default": 220, "unit": "mm"}
        }
    }
    metadata_list.append(save_model(tote_medium, "container-tote-600x400-low.glb", meta_tote_medium))
    
    # 规格3：小型周转箱 400×300×150（适配轻型货架）
    print("  - 小型周转箱 400×300×150...")
    tote_small = generate_tote_box(length=400, width=300, height=150)
    meta_tote_small = {
        "id": "container-tote-400x300x150",
        "name": "可堆叠周转箱-400×300×150",
        "category": "containers",
        "description": "小型零件周转箱，适配轻型货架，可堆叠6层",
        "tags": ["周转箱", "零件盒", "小型", "橙色"],
        "parameters": {
            "length": {"type": "number", "min": 300, "max": 500, "default": 400, "unit": "mm"},
            "width": {"type": "number", "min": 200, "max": 400, "default": 300, "unit": "mm"},
            "height": {"type": "number", "min": 100, "max": 200, "default": 150, "unit": "mm"}
        }
    }
    metadata_list.append(save_model(tote_small, "container-tote-400x300.glb", meta_tote_small))
    
    # 生成前移式叉车
    print("\n🚛 生成前移式叉车...")
    print("  - 前移式叉车 2吨9米...")
    forklift_reach = generate_reach_truck()
    meta_forklift = {
        "id": "forklift-reach-2t-9m",
        "name": "前移式叉车-2吨9米",
        "category": "handling",
        "description": "前移式叉车，窄通道高位存取，适配重型5层立体库，举升高度9米",
        "tags": ["前移式叉车", "窄通道", "高位存取", "2吨", "9米"],
        "parameters": {
            "length": {"type": "number", "min": 2500, "max": 3500, "default": 2900, "unit": "mm"},
            "width": {"type": "number", "min": 1000, "max": 1300, "default": 1100, "unit": "mm"},
            "height": {"type": "number", "min": 2200, "max": 2800, "default": 2500, "unit": "mm"},
            "liftHeight": {"type": "number", "min": 6000, "max": 12000, "default": 9000, "unit": "mm"}
        }
    }
    metadata_list.append(save_model(forklift_reach, "forklift-reach-2t.glb", meta_forklift))
    
    # 生成平衡重叉车
    print("\n🚛 生成平衡重叉车...")
    print("  - 平衡重叉车 2.5吨4米...")
    forklift_counterbalance = generate_counterbalance_forklift()
    meta_counterbalance = {
        "id": "forklift-counterbalance-2.5t-4m",
        "name": "平衡重叉车-2.5吨4米",
        "category": "handling",
        "description": "平衡重叉车，通用型搬运设备，适合室内外作业，适配重型3-4层货架",
        "tags": ["平衡重叉车", "通用型", "室内外", "2.5吨", "4米"],
        "parameters": {
            "length": {"type": "number", "min": 2800, "max": 3600, "default": 3200, "unit": "mm"},
            "width": {"type": "number", "min": 1100, "max": 1300, "default": 1200, "unit": "mm"},
            "height": {"type": "number", "min": 2000, "max": 2400, "default": 2200, "unit": "mm"},
            "liftHeight": {"type": "number", "min": 3000, "max": 6000, "default": 4000, "unit": "mm"}
        }
    }
    metadata_list.append(save_model(forklift_counterbalance, "forklift-counterbalance-2.5t.glb", meta_counterbalance))
    
    # 生成电动搬运车
    print("\n🚛 生成电动搬运车...")
    print("  - 电动搬运车 2吨步行式...")
    pallet_truck = generate_electric_pallet_truck()
    meta_pallet_truck = {
        "id": "forklift-pallet-truck-electric-2t",
        "name": "电动搬运车-2吨步行式",
        "category": "handling",
        "description": "平库及重型货架底层搬运专用，步行式操作，适合短距离水平搬运",
        "tags": ["电动搬运车", "步行式", "平库搬运", "2吨"],
        "parameters": {
            "length": {"type": "number", "min": 1600, "max": 2100, "default": 1850, "unit": "mm"},
            "width": {"type": "number", "min": 550, "max": 750, "default": 680, "unit": "mm"},
            "height": {"type": "number", "min": 1200, "max": 1500, "default": 1350, "unit": "mm"},
            "liftHeight": {"type": "number", "min": 150, "max": 250, "default": 200, "unit": "mm"}
        }
    }
    metadata_list.append(save_model(pallet_truck, "forklift-pallet-truck-electric.glb", meta_pallet_truck))
    
    # 保存元数据
    print("\n📝 保存元数据...")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！共生成 {len(metadata_list)} 个模型")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"📄 元数据文件: {METADATA_FILE}")


if __name__ == "__main__":
    main()
