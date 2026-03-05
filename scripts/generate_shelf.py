import trimesh
import numpy as np
import os
import json
import argparse

def create_box(size, position, color):
    """创建一个立方体"""
    box = trimesh.creation.box(extents=size)
    box.apply_translation(position)
    color_rgba = np.array([int(c * 255) for c in color] + [255], dtype=np.uint8)
    box.visual.vertex_colors = color_rgba
    return box

def generate_shelf(length_mm=2500, depth_mm=1000, height_mm=4500,
                   layers=4, layer_height_mm=1200,
                   output_dir="assets"):
    """生成货架+托盘3D模型"""

    # 转换为米

    SHELF_LENGTH = length_mm / 1000
    SHELF_DEPTH = depth_mm / 1000
    SHELF_HEIGHT = height_mm / 1000
    LAYER_COUNT = layers
    LAYER_HEIGHT = layer_height_mm / 1000

    PALLET_LENGTH = 1.2
    PALLET_WIDTH = 1.0
    PALLET_HEIGHT = 0.15

    UPRIGHT_WIDTH = 0.08
    UPRIGHT_DEPTH = 0.06
    BEAM_HEIGHT = 0.1
    BEAM_DEPTH = 0.05

    COLOR_SHELF = (0.4, 0.4, 0.45)
    COLOR_PALLET = (0.6, 0.4, 0.2)

    meshes = []

    # 立柱

    upright_positions = [
        (-SHELF_LENGTH/2 + UPRIGHT_WIDTH/2, -SHELF_DEPTH/2 + UPRIGHT_DEPTH/2, SHELF_HEIGHT/2),
        (SHELF_LENGTH/2 - UPRIGHT_WIDTH/2, -SHELF_DEPTH/2 + UPRIGHT_DEPTH/2, SHELF_HEIGHT/2),
        (-SHELF_LENGTH/2 + UPRIGHT_WIDTH/2, SHELF_DEPTH/2 - UPRIGHT_DEPTH/2, SHELF_HEIGHT/2),
        (SHELF_LENGTH/2 - UPRIGHT_WIDTH/2, SHELF_DEPTH/2 - UPRIGHT_DEPTH/2, SHELF_HEIGHT/2),
    ]
    for pos in upright_positions:
        meshes.append(create_box((UPRIGHT_WIDTH, UPRIGHT_DEPTH, SHELF_HEIGHT), pos, COLOR_SHELF))

    # 横梁

    beam_y_positions = [-SHELF_DEPTH/2 + UPRIGHT_DEPTH/2, SHELF_DEPTH/2 - UPRIGHT_DEPTH/2]
    for layer in range(LAYER_COUNT):
        z = (layer + 1) * LAYER_HEIGHT
        for y in beam_y_positions:
            meshes.append(create_box((SHELF_LENGTH - UPRIGHT_WIDTH * 2, BEAM_DEPTH, BEAM_HEIGHT), (0, y, z), COLOR_SHELF))

    # 层板

    for layer in range(LAYER_COUNT):
        z = (layer + 1) * LAYER_HEIGHT + BEAM_HEIGHT/2 + 0.02
        meshes.append(create_box((SHELF_LENGTH - UPRIGHT_WIDTH * 2, SHELF_DEPTH - UPRIGHT_DEPTH * 2, 0.03), (0, 0, z), COLOR_SHELF))

    # 托盘

    def create_pallet(center_pos):
        px, py, pz = center_pos
        meshes.append(create_box((PALLET_LENGTH, PALLET_WIDTH, 0.04), (px, py, pz + PALLET_HEIGHT - 0.02), COLOR_PALLET))
        beam_spacing = PALLET_WIDTH / 4
        for i in range(3):
            y = py - PALLET_WIDTH/2 + beam_spacing * (i + 1)
            meshes.append(create_box((PALLET_LENGTH, 0.08, 0.1), (px, y, pz + 0.05), COLOR_PALLET))
        block_spacing_x = PALLET_LENGTH / 4
        for i in range(3):
            for j in range(3):
                x = px - PALLET_LENGTH/2 + block_spacing_x * (i + 1)
                y = py - PALLET_WIDTH/2 + beam_spacing * (j + 1)
                meshes.append(create_box((0.1, 0.08, 0.05), (x, y, pz + 0.025), COLOR_PALLET))

    for layer in range(LAYER_COUNT):
        z = (layer + 1) * LAYER_HEIGHT + BEAM_HEIGHT/2 + 0.05
        create_pallet((-0.5, 0, z))
        create_pallet((0.5, 0, z))

    # 导出

    combined = trimesh.util.concatenate(meshes)
    os.makedirs(output_dir, exist_ok=True)

    glb_path = os.path.join(output_dir, "shelf_with_pallet.glb")
    combined.export(glb_path)

    params = {
        "name": "横梁式重型货架",
        "type": "shelf_beam_heavy",
        "dimensions": {"length_mm": length_mm, "depth_mm": depth_mm, "height_mm": height_mm},
        "layers": layers,
        "layer_height_mm": layer_height_mm,
        "pallet": {"length_mm": 1200, "width_mm": 1000, "height_mm": 150, "count_per_layer": 2},
        "model_file": glb_path,
        "format": "glb"
    }

    json_path = os.path.join(output_dir, "shelf_with_pallet.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, ensure_ascii=False, indent=2)

    print(f"✓ 已生成: {glb_path}")
    print(f"✓ 已生成: {json_path}")
    return glb_path, json_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成货架3D模型")
    parser.add_argument("--length", type=int, default=2500, help="货架长度(mm)")
    parser.add_argument("--depth", type=int, default=1000, help="货架深度(mm)")
    parser.add_argument("--height", type=int, default=4500, help="货架高度(mm)")
    parser.add_argument("--layers", type=int, default=4, help="层数")
    parser.add_argument("--layer-height", type=int, default=1200, help="层高(mm)")
    args = parser.parse_args()

    generate_shelf(args.length, args.depth, args.height, args.layers, args.layer_height)