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
    
    # 保存元数据
    print("\n📝 保存元数据...")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！共生成 {len(metadata_list)} 个模型")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"📄 元数据文件: {METADATA_FILE}")


if __name__ == "__main__":
    main()
