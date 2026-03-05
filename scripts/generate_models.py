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
    生成横梁式货架
    
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
        color = [80, 80, 80, 255]  # 深灰色
    elif load_capacity == "medium":
        upright_size = 70
        beam_height = 100
        beam_width = 40
        color = [100, 100, 100, 255]
    else:
        upright_size = 55
        beam_height = 80
        beam_width = 35
        color = [120, 120, 120, 255]
    
    # 立柱 (4根)
    upright_positions = [
        [-length/2 + upright_size/2, -width/2 + upright_size/2],
        [length/2 - upright_size/2, -width/2 + upright_size/2],
        [-length/2 + upright_size/2, width/2 - upright_size/2],
        [length/2 - upright_size/2, width/2 - upright_size/2]
    ]
    
    for x, y in upright_positions:
        upright = trimesh.creation.box(
            extents=[upright_size, upright_size, height]
        )
        upright.apply_translation([x, y, height/2])
        meshes.append(upright)
    
    # 横梁 (每层2根)
    level_height = height / (levels + 1)
    for level in range(1, levels + 1):
        z = level * level_height
        
        # 前横梁
        front_beam = trimesh.creation.box(
            extents=[length - 2*upright_size, beam_width, beam_height]
        )
        front_beam.apply_translation([0, -width/2 + upright_size/2, z])
        meshes.append(front_beam)
        
        # 后横梁
        back_beam = trimesh.creation.box(
            extents=[length - 2*upright_size, beam_width, beam_height]
        )
        back_beam.apply_translation([0, width/2 - upright_size/2, z])
        meshes.append(back_beam)
        
        # 层板 (金属网或木板)
        deck = trimesh.creation.box(
            extents=[length - 2*upright_size, width - 2*upright_size, 30]
        )
        deck.apply_translation([0, 0, z - 15])
        meshes.append(deck)
    
    # 合并
    shelf = trimesh.util.concatenate(meshes)
    shelf.visual.vertex_colors = color
    
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
    
    return shelf, {
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
    
    # 同时创建材质（PBR材质）
    material = trimesh.visual.material.PBRMaterial(
        metallicFactor=0.3,
        roughnessFactor=0.7,
        baseColorFactor=color_255
    )
    mesh.visual.material = material
    
    return mesh


def generate_light_shelf_v2(length=1200, width=400, height=2000, levels=4):
    """
    生成轻型货架 V2 - 基于参考图片改进版
    
    参考图片特征:
    - 蓝色立柱带菱形孔
    - 橙色阶梯状横梁
    - 白色层板
    - 立柱间斜拉支撑
    - 底部塑料脚垫
    
    Args:
        length: 货架长度 (mm), 默认1200
        width: 货架深度 (mm), 默认400
        height: 货架高度 (mm), 默认2000
        levels: 层数, 默认4层
    """
    meshes = []
    
    # 颜色定义 (参考图片) - 使用RGB 0-1范围
    COLOR_BLUE = [0.25, 0.45, 0.85]      # 立柱蓝色 - 调淡 #4075D9
    COLOR_ORANGE = [0.91, 0.36, 0.02]    # 横梁橙色 #E85D04
    COLOR_WHITE = [0.96, 0.96, 0.96]     # 层板白色 #F5F5F5
    COLOR_GREY = [0.39, 0.39, 0.39]      # 脚垫灰色
    
    # 尺寸参数
    upright_width = 40       # 立柱宽度
    upright_depth = 30       # 立柱深度
    beam_height = 35         # 横梁高度
    beam_width = 30          # 横梁宽度
    deck_thickness = 20      # 层板厚度
    foot_height = 30         # 脚垫高度
    
    # 立柱位置 (4根)
    upright_positions = [
        [-length/2 + upright_width/2, -width/2 + upright_depth/2],
        [length/2 - upright_width/2, -width/2 + upright_depth/2],
        [-length/2 + upright_width/2, width/2 - upright_depth/2],
        [length/2 - upright_width/2, width/2 - upright_depth/2]
    ]
    
    # 生成立柱
    for i, (x, y) in enumerate(upright_positions):
        # 主立柱
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height - foot_height]
        )
        upright.apply_translation([x, y, (height - foot_height)/2 + foot_height])
        
        # 给立柱添加菱形孔效果 (用纹理或简化表示)
        # 这里用多个小方块模拟孔洞效果
        hole_spacing = 50  # 孔间距
        hole_start = 200   # 起始高度
        for h in range(hole_start, int(height - foot_height - 100), hole_spacing):
            # 正面孔
            hole_front = trimesh.creation.box(
                extents=[15, 5, 25]
            )
            hole_front.apply_translation([x, y - upright_depth/2 - 2, h])
            
            # 侧面孔
            hole_side = trimesh.creation.box(
                extents=[5, 15, 25]
            )
            hole_side.apply_translation([x - upright_width/2 - 2, y, h])
            
            # 用布尔运算减去孔洞 (简化版：这里直接添加深色小块表示)
            hole_marker_front = trimesh.creation.box(
                extents=[12, 2, 20]
            )
            hole_marker_front.apply_translation([x, y - upright_depth/2 + 1, h])
            
            hole_marker_side = trimesh.creation.box(
                extents=[2, 12, 20]
            )
            hole_marker_side.apply_translation([x - upright_width/2 + 1, y, h])
        
        # 脚垫
        foot = trimesh.creation.box(
            extents=[upright_width + 10, upright_depth + 10, foot_height]
        )
        foot.apply_translation([x, y, foot_height/2])
        set_mesh_color(foot, COLOR_GREY)
        meshes.append(foot)
        
        set_mesh_color(upright, COLOR_BLUE)
        meshes.append(upright)
    
    # 计算层板高度
    level_spacing = (height - 300) / (levels + 1)
    
    # 生成横梁和层板
    for level in range(1, levels + 1):
        z = 150 + level * level_spacing
        
        # 横梁 (前后各一根)
        for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
            # 主横梁 (阶梯状，用两个长方体组合)
            # 上部
            beam_top = trimesh.creation.box(
                extents=[length - 2*upright_width - 10, beam_width, beam_height/2]
            )
            beam_top.apply_translation([0, y_offset, z + beam_height/4])
            
            # 下部 (稍微宽一点，形成阶梯效果)
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
    
    # 斜拉支撑 (增加稳定性，参考图片特征)
    # 前后各一组X型支撑
    for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
        # 左侧斜撑
        diag_left = trimesh.creation.box(
            extents=[3, 3, height * 0.7]
        )
        diag_left.apply_translation([
            -length/2 + upright_width + 20,
            y_offset,
            height/2
        ])
        set_mesh_color(diag_left, COLOR_BLUE)
        meshes.append(diag_left)
        
        # 右侧斜撑
        diag_right = trimesh.creation.box(
            extents=[3, 3, height * 0.7]
        )
        diag_right.apply_translation([
            length/2 - upright_width - 20,
            y_offset,
            height/2
        ])
        set_mesh_color(diag_right, COLOR_BLUE)
        meshes.append(diag_right)
    
    # 使用Scene来保留每个mesh的材质，而不是合并
    scene = trimesh.Scene()
    
    # 修复坐标系：Trimesh使用Z轴向上，Three.js使用Y轴向上
    # 需要旋转模型，使Z轴朝上变为Y轴朝上
    # 绕X轴旋转-90度（逆时针），这样Z向上变成Y向上
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,  # -90度
        direction=[1, 0, 0],  # 绕X轴旋转
        point=[0, 0, 0]
    )
    
    # 添加每个mesh到scene，并应用旋转
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


def generate_heavy_shelf_industrial(length=2300, width=1000, height=4500, levels=4, 
                                     layer_heights=None, upright_profile="90x80", 
                                     beam_profile="120x50", name_suffix=""):
    """
    生成行业标准重型货架（基于参考图片）
    
    参考图片特征：
    - 深蓝色立柱（带菱形孔）
    - 橙色横梁
    - 金属网格层板（橙色边框）
    - X型斜拉支撑
    - 黄色防撞护栏
    
    Args:
        length: 货架长度 (mm)，2300或2700
        width: 货架深度 (mm)，标准1000
        height: 货架高度 (mm)
        levels: 层数 (3/4/5)
        layer_heights: 各层层高列表，默认均匀分布
        upright_profile: 立柱规格
        beam_profile: 横梁规格
        name_suffix: 名称后缀
    """
    meshes = []
    
    # 颜色定义（基于参考图片）
    COLOR_UPRIGHT = [0.18, 0.25, 0.45]      # 深蓝色立柱 #2D3F73
    COLOR_BEAM = [0.85, 0.45, 0.15]         # 橙色横梁 #D97326
    COLOR_DECK_FRAME = [0.85, 0.45, 0.15]   # 层板边框橙色
    COLOR_DECK_MESH = [0.75, 0.75, 0.75]    # 层板网格灰色
    COLOR_GUARD = [0.95, 0.85, 0.15]        # 黄色防撞护栏 #F2D826
    
    # 尺寸参数
    upright_width = 90
    upright_depth = 80
    beam_height = 120
    beam_width = 50
    deck_thickness = 30
    guard_height = 400
    guard_depth = 300
    
    # 计算各层高度
    if layer_heights is None:
        # 默认均匀分布，底层留出叉车操作空间
        base_height = 200  # 底部离地高度
        available_height = height - base_height - 200  # 顶部预留
        avg_height = available_height / levels
        layer_heights = [avg_height] * levels
    
    # 立柱位置（4根）
    upright_positions = [
        [-length/2 + upright_width/2, -width/2 + upright_depth/2],
        [length/2 - upright_width/2, -width/2 + upright_depth/2],
        [-length/2 + upright_width/2, width/2 - upright_depth/2],
        [length/2 - upright_width/2, width/2 - upright_depth/2]
    ]
    
    # 生成立柱
    for x, y in upright_positions:
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height]
        )
        upright.apply_translation([x, y, height/2])
        
        set_mesh_color(upright, COLOR_UPRIGHT)
        meshes.append(upright)
    
    # 生成横梁和层板
    current_z = 200  # 从底部200mm开始
    for level in range(levels):
        layer_height = layer_heights[level]
        current_z += layer_height
        
        # 前后横梁（橙色）
        for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
            beam = trimesh.creation.box(
                extents=[length - 2*upright_width, beam_width, beam_height]
            )
            beam.apply_translation([0, y_offset, current_z - beam_height/2])
            set_mesh_color(beam, COLOR_BEAM)
            meshes.append(beam)
        
        # 层板（金属网格效果 - 用橙色边框+灰色网格表示）
        # 层板边框
        deck_frame = trimesh.creation.box(
            extents=[length - 2*upright_width - 20, width - 2*upright_depth - 20, deck_thickness]
        )
        deck_frame.apply_translation([0, 0, current_z])
        set_mesh_color(deck_frame, COLOR_DECK_FRAME)
        meshes.append(deck_frame)
        
        # 层板网格（简化用细条表示）
        grid_spacing = 100
        for i in range(int((length - 2*upright_width - 40) / grid_spacing)):
            x_pos = -(length - 2*upright_width - 40)/2 + i * grid_spacing + grid_spacing/2
            grid_bar = trimesh.creation.box(extents=[5, width - 2*upright_depth - 30, 5])
            grid_bar.apply_translation([x_pos, 0, current_z + 5])
            set_mesh_color(grid_bar, COLOR_DECK_MESH)
            meshes.append(grid_bar)
    
    # X型斜拉支撑（前后各一组）
    for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
        # 左侧X支撑
        diag1 = trimesh.creation.box(extents=[5, 5, height * 0.6])
        diag1.apply_translation([-length/2 + upright_width + 100, y_offset, height/2])
        set_mesh_color(diag1, COLOR_UPRIGHT)
        meshes.append(diag1)
        
        # 右侧X支撑
        diag2 = trimesh.creation.box(extents=[5, 5, height * 0.6])
        diag2.apply_translation([length/2 - upright_width - 100, y_offset, height/2])
        set_mesh_color(diag2, COLOR_UPRIGHT)
        meshes.append(diag2)
    
    # 黄色防撞护栏（底部两侧）
    for y_offset in [-width/2 - guard_depth/2, width/2 + guard_depth/2]:
        guard = trimesh.creation.box(
            extents=[length + 200, 40, guard_height]
        )
        guard.apply_translation([0, y_offset, guard_height/2])
        set_mesh_color(guard, COLOR_GUARD)
        meshes.append(guard)
    
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
    
    # 生成3种行业标准重型货架
    print("\n🏗️ 生成行业标准重型货架...")
    
    # 规格1：重型3层中高位货架（适配净空5.5m仓库）
    print("  - 重型3层中高位货架...")
    shelf_3level = generate_heavy_shelf_industrial(
        length=2300, 
        width=1000, 
        height=4500, 
        levels=3,
        layer_heights=[1400, 1400, 1400],
        upright_profile="90x70",
        beam_profile="120x50"
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
    
    # 规格2：重型4层标准货架（适配净空7m仓库，最常用）
    print("  - 重型4层标准货架...")
    shelf_4level = generate_heavy_shelf_industrial(
        length=2300, 
        width=1000, 
        height=6500, 
        levels=4,
        layer_heights=[1600, 1600, 1600, 1300],
        upright_profile="90x80",
        beam_profile="120x50"
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
    
    # 规格3：重型5层高位货架（适配净空9m仓库）
    print("  - 重型5层高位货架...")
    shelf_5level = generate_heavy_shelf_industrial(
        length=2700, 
        width=1000, 
        height=8200, 
        levels=5,
        layer_heights=[1700, 1700, 1700, 1700, 1400],
        upright_profile="90x90",
        beam_profile="140x50"
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
    
    # 保存元数据
    print("\n📝 保存元数据...")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！共生成 {len(metadata_list)} 个模型")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"📄 元数据文件: {METADATA_FILE}")


if __name__ == "__main__":
    main()
