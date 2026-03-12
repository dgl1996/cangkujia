"""
仓酷家 3D模型生成器 - 可复用模板模块

使用说明:
1. 导入此模块
2. 调用 generate_shelf() / generate_container() / generate_equipment()
3. 传入必要的参数
4. 返回Scene对象和元数据

示例:
    from model_generator_template import generate_shelf
    
    scene, metadata = generate_shelf(
        length=2300,
        width=1000,
        height=4500,
        levels=4,
        colors={
            'upright': [0.18, 0.25, 0.45],  # 立柱蓝色
            'beam': [0.85, 0.45, 0.15],     # 横梁橙色
            'deck': [0.75, 0.75, 0.75]      # 层板灰色
        }
    )
"""

import numpy as np
import trimesh


def set_mesh_color(mesh, color):
    """
    设置网格颜色 - 使用顶点颜色确保GLB导出正确
    
    Args:
        mesh: trimesh.Trimesh 对象
        color: [R, G, B] 颜色值(范围0-1) 或 Hex字符串(如"#FF4500")
    
    Returns:
        mesh: 设置好颜色的mesh
    """
    # 支持Hex颜色格式
    if isinstance(color, str) and color.startswith('#'):
        # Hex转RGB
        hex_color = color.lstrip('#')
        rgb = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        color_255 = [int(c * 255) for c in rgb] + [255]
    else:
        # RGB数组格式
        color_255 = [int(c * 255) for c in color] + [255]
    
    if hasattr(mesh.visual, 'vertex_colors'):
        mesh.visual.vertex_colors = color_255
    return mesh


def hex_to_rgb(hex_color):
    """
    Hex颜色转换为RGB数组
    
    Args:
        hex_color: Hex字符串(如"#FF4500")
    
    Returns:
        [R, G, B]: RGB数组(范围0-1)
    """
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]


def create_scene(meshes):
    """
    创建Scene并应用坐标转换
    
    Args:
        meshes: mesh对象列表
    
    Returns:
        scene: trimesh.Scene 对象
    """
    scene = trimesh.Scene()
    
    # 坐标转换：Trimesh(Z轴向上) -> Three.js(Y轴向上)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-np.pi / 2,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    
    for i, mesh in enumerate(meshes):
        mesh.apply_transform(rotation_matrix)
        scene.add_geometry(mesh, node_name=f'part_{i}')
    
    return scene


def export_glb(scene, output_path, metadata=None):
    """
    导出Scene为GLB文件
    
    Args:
        scene: trimesh.Scene 对象
        output_path: 输出文件路径
        metadata: 可选的元数据字典，会添加到GLB的extra数据中
    
    Returns:
        bool: 是否导出成功
    """
    try:
        # 导出为GLB
        scene.export(output_path, file_type='glb')
        
        # 如果有元数据，保存到同名JSON文件
        if metadata:
            import json
            json_path = output_path.replace('.glb', '.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"导出失败: {e}")
        return False


def generate_shelf(length=2300, width=1000, height=4500, levels=4,
                   upright_size=(90, 80), beam_size=(100, 50),
                   colors=None, layer_heights=None):
    """
    生成标准货架模型
    
    Args:
        length: 货架长度 (mm)
        width: 货架深度 (mm)
        height: 货架高度 (mm)
        levels: 层数
        upright_size: (宽度, 深度) 立柱尺寸
        beam_size: (高度, 宽度) 横梁尺寸
        colors: {
            'upright': [R, G, B],  # 立柱颜色
            'beam': [R, G, B],     # 横梁颜色
            'deck': [R, G, B]      # 层板颜色
        }
        layer_heights: 各层层高列表，默认均匀分布
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典
    """
    # 默认颜色
    if colors is None:
        colors = {
            'upright': [0.18, 0.25, 0.45],  # 深蓝
            'beam': [0.85, 0.45, 0.15],     # 橙色
            'deck': [0.75, 0.75, 0.75]      # 灰色
        }
    
    meshes = []
    upright_width, upright_depth = upright_size
    beam_height, beam_width = beam_size
    deck_thickness = 30
    foot_height = 50
    
    # 计算层高度
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
        # 立柱
        upright = trimesh.creation.box(
            extents=[upright_width, upright_depth, height - foot_height]
        )
        upright.apply_translation([x, y, (height - foot_height)/2 + foot_height])
        set_mesh_color(upright, colors['upright'])
        meshes.append(upright)
        
        # 脚垫
        foot = trimesh.creation.box(
            extents=[upright_width + 20, upright_depth + 20, foot_height]
        )
        foot.apply_translation([x, y, foot_height/2])
        set_mesh_color(foot, colors['beam'])
        meshes.append(foot)
    
    # 生成横梁和层板
    current_z = 200
    for level in range(levels):
        layer_height = layer_heights[level]
        current_z += layer_height
        
        # 横梁（前后各一根）
        for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
            # 横梁上部分
            beam_top = trimesh.creation.box(
                extents=[length - 2*upright_width - 10, beam_width, beam_height/2]
            )
            beam_top.apply_translation([0, y_offset, current_z + beam_height/4])
            
            # 横梁下部分
            beam_bottom = trimesh.creation.box(
                extents=[length - 2*upright_width, beam_width + 5, beam_height/2]
            )
            beam_bottom.apply_translation([0, y_offset, current_z - beam_height/4])
            
            set_mesh_color(beam_top, colors['beam'])
            set_mesh_color(beam_bottom, colors['beam'])
            meshes.append(beam_top)
            meshes.append(beam_bottom)
        
        # 层板
        deck = trimesh.creation.box(
            extents=[length - 2*upright_width - 20, width - 2*upright_depth - 10, deck_thickness]
        )
        deck.apply_translation([0, 0, current_z])
        set_mesh_color(deck, colors['deck'])
        meshes.append(deck)
    
    # 斜拉支撑
    for y_offset in [-width/2 + upright_depth/2, width/2 - upright_depth/2]:
        diag_left = trimesh.creation.box(extents=[5, 5, height * 0.7])
        diag_left.apply_translation([-length/2 + upright_width + 100, y_offset, height/2])
        set_mesh_color(diag_left, colors['upright'])
        meshes.append(diag_left)
        
        diag_right = trimesh.creation.box(extents=[5, 5, height * 0.7])
        diag_right.apply_translation([length/2 - upright_width - 100, y_offset, height/2])
        set_mesh_color(diag_right, colors['upright'])
        meshes.append(diag_right)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据
    metadata = {
        "id": f"shelf-{length}x{width}x{height}-{levels}level",
        "name": f"货架-{length}x{width}x{height}mm-{levels}层",
        "category": "storage",
        "description": f"标准货架，尺寸{length}x{width}x{height}mm，{levels}层",
        "tags": ["货架", f"{levels}层"],
        "parameters": {
            "length": {"type": "number", "min": 1000, "max": 5000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 500, "max": 1500, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 1000, "max": 12000, "default": height, "unit": "mm"},
            "levels": {"type": "number", "min": 1, "max": 10, "default": levels}
        }
    }
    
    return scene, metadata


def generate_box_container(length=1200, width=1000, height=1000, 
                           wall_thickness=50, colors=None):
    """
    生成箱体容器（如周转箱、料箱）
    
    Args:
        length: 长度 (mm)
        width: 宽度 (mm)
        height: 高度 (mm)
        wall_thickness: 壁厚 (mm)
        colors: {
            'body': [R, G, B],     # 主体颜色
            'detail': [R, G, B]    # 细节颜色
        }
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典
    """
    if colors is None:
        colors = {
            'body': [0.2, 0.6, 0.8],    # 蓝色
            'detail': [0.9, 0.9, 0.9]   # 白色
        }
    
    meshes = []
    
    # 底部
    bottom = trimesh.creation.box(
        extents=[length, width, wall_thickness]
    )
    bottom.apply_translation([0, 0, wall_thickness/2])
    set_mesh_color(bottom, colors['body'])
    meshes.append(bottom)
    
    # 四壁
    # 前壁
    front = trimesh.creation.box(
        extents=[length, wall_thickness, height]
    )
    front.apply_translation([0, -width/2 + wall_thickness/2, height/2])
    set_mesh_color(front, colors['body'])
    meshes.append(front)
    
    # 后壁
    back = trimesh.creation.box(
        extents=[length, wall_thickness, height]
    )
    back.apply_translation([0, width/2 - wall_thickness/2, height/2])
    set_mesh_color(back, colors['body'])
    meshes.append(back)
    
    # 左壁
    left = trimesh.creation.box(
        extents=[wall_thickness, width - 2*wall_thickness, height]
    )
    left.apply_translation([-length/2 + wall_thickness/2, 0, height/2])
    set_mesh_color(left, colors['body'])
    meshes.append(left)
    
    # 右壁
    right = trimesh.creation.box(
        extents=[wall_thickness, width - 2*wall_thickness, height]
    )
    right.apply_translation([length/2 - wall_thickness/2, 0, height/2])
    set_mesh_color(right, colors['body'])
    meshes.append(right)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据
    metadata = {
        "id": f"container-{length}x{width}x{height}",
        "name": f"周转箱-{length}x{width}x{height}mm",
        "category": "containers",
        "description": f"标准周转箱，尺寸{length}x{width}x{height}mm",
        "tags": ["周转箱", "容器"],
        "parameters": {
            "length": {"type": "number", "min": 300, "max": 2000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 200, "max": 1500, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 100, "max": 1000, "default": height, "unit": "mm"}
        }
    }
    
    return scene, metadata


def generate_pallet(length=1200, width=1000, height=150, colors=None):
    """
    生成托盘模型
    
    Args:
        length: 长度 (mm)
        width: 宽度 (mm)
        height: 高度 (mm)
        colors: {
            'board': [R, G, B],    # 面板颜色
            'block': [R, G, B]     # 垫块颜色
        }
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典
    """
    if colors is None:
        colors = {
            'board': [0.55, 0.35, 0.20],  # 棕色（木质）
            'block': [0.45, 0.25, 0.10]   # 深棕色
        }
    
    meshes = []
    
    board_thickness = height / 3
    block_height = height / 3
    
    # 上面板
    top_board = trimesh.creation.box(
        extents=[length, width, board_thickness]
    )
    top_board.apply_translation([0, 0, height - board_thickness/2])
    set_mesh_color(top_board, colors['board'])
    meshes.append(top_board)
    
    # 下面板
    bottom_board = trimesh.creation.box(
        extents=[length, width, board_thickness]
    )
    bottom_board.apply_translation([0, 0, board_thickness/2])
    set_mesh_color(bottom_board, colors['board'])
    meshes.append(bottom_board)
    
    # 垫块（9个标准布局）
    block_positions = [
        [-length/3, -width/3], [0, -width/3], [length/3, -width/3],
        [-length/3, 0], [0, 0], [length/3, 0],
        [-length/3, width/3], [0, width/3], [length/3, width/3]
    ]
    
    for x, y in block_positions:
        block = trimesh.creation.box(
            extents=[100, 100, block_height]
        )
        block.apply_translation([x, y, height/2])
        set_mesh_color(block, colors['block'])
        meshes.append(block)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据
    metadata = {
        "id": f"pallet-{length}x{width}",
        "name": f"托盘-{length}x{width}mm",
        "category": "containers",
        "description": f"标准托盘，尺寸{length}x{width}mm",
        "tags": ["托盘", "木质"],
        "parameters": {
            "length": {"type": "number", "min": 800, "max": 2000, "default": length, "unit": "mm"},
            "width": {"type": "number", "min": 600, "max": 1500, "default": width, "unit": "mm"},
            "height": {"type": "number", "min": 100, "max": 200, "default": height, "unit": "mm"}
        }
    }
    
    return scene, metadata


def generate_light_duty_shelf(长度=1500, 深度=400, 高度=2000, 层数=4,
                               层载重=500, 标准层高=600, 层板厚度=20,
                               立柱颜色="#B0C4DE", 横梁颜色="#FF4500", 层板颜色="#FFFFFF",
                               顶层挡板高度=50):
    """
    生成轻型货架模型（增强版）- 支持中文参数和Hex颜色
    
    Args:
        长度: 货架长度 (mm)，默认1500
        深度: 货架深度 (mm)，默认400
        高度: 货架高度 (mm)，默认2000
        层数: 层数，默认4
        层载重: 单层承载重量(kg)，默认500
        标准层高: 标准层高度(mm)，默认600
        层板厚度: 层板厚度(mm)，默认20
        立柱颜色: 立柱颜色(Hex格式)，默认"#B0C4DE"(浅钢蓝)
        横梁颜色: 横梁颜色(Hex格式)，默认"#FF4500"(橙红)
        层板颜色: 层板颜色(Hex格式)，默认"#FFFFFF"(白色)
        顶层挡板高度: 顶层后侧挡板高度(mm)，默认50
    
    Returns:
        scene: trimesh.Scene 对象
        metadata: 模型元数据字典(中文参数格式)
    """
    meshes = []
    
    # 立柱尺寸
    立柱宽度 = 40
    立柱深度 = 40
    横梁高度 = 40
    横梁宽度 = 30
    底脚高度 = 30
    
    # 计算层高度（均匀分布）
    底层高度 = 100
    可用高度 = 高度 - 底层高度 - 顶层挡板高度
    平均层高 = 可用高度 / 层数
    层高度列表 = [平均层高] * 层数
    
    # 立柱位置（4根）
    立柱位置 = [
        [-长度/2 + 立柱宽度/2, -深度/2 + 立柱深度/2],
        [长度/2 - 立柱宽度/2, -深度/2 + 立柱深度/2],
        [-长度/2 + 立柱宽度/2, 深度/2 - 立柱深度/2],
        [长度/2 - 立柱宽度/2, 深度/2 - 立柱深度/2]
    ]
    
    # 生成立柱和底脚
    for x, y in 立柱位置:
        # 立柱
        立柱 = trimesh.creation.box(
            extents=[立柱宽度, 立柱深度, 高度 - 底脚高度]
        )
        立柱.apply_translation([x, y, (高度 - 底脚高度)/2 + 底脚高度])
        set_mesh_color(立柱, 立柱颜色)
        meshes.append(立柱)
        
        # 底脚
        底脚 = trimesh.creation.box(
            extents=[立柱宽度 + 20, 立柱深度 + 20, 底脚高度]
        )
        底脚.apply_translation([x, y, 底脚高度/2])
        set_mesh_color(底脚, 横梁颜色)
        meshes.append(底脚)
    
    # 生成横梁和层板
    当前高度 = 底层高度
    for 层索引 in range(层数):
        层高 = 层高度列表[层索引]
        当前高度 += 层高
        
        # 横梁（前后各一根）
        for y偏移 in [-深度/2 + 立柱深度/2, 深度/2 - 立柱深度/2]:
            # 横梁上部分
            横梁上 = trimesh.creation.box(
                extents=[长度 - 2*立柱宽度 - 10, 横梁宽度, 横梁高度/2]
            )
            横梁上.apply_translation([0, y偏移, 当前高度 + 横梁高度/4])
            
            # 横梁下部分
            横梁下 = trimesh.creation.box(
                extents=[长度 - 2*立柱宽度, 横梁宽度 + 5, 横梁高度/2]
            )
            横梁下.apply_translation([0, y偏移, 当前高度 - 横梁高度/4])
            
            set_mesh_color(横梁上, 横梁颜色)
            set_mesh_color(横梁下, 横梁颜色)
            meshes.append(横梁上)
            meshes.append(横梁下)
        
        # 层板（白色平面，厚度20mm）
        层板 = trimesh.creation.box(
            extents=[长度 - 2*立柱宽度 - 20, 深度 - 2*立柱深度 - 10, 层板厚度]
        )
        层板.apply_translation([0, 0, 当前高度])
        set_mesh_color(层板, 层板颜色)
        meshes.append(层板)
        
        # 顶层挡板（只有顶层添加）
        if 层索引 == 层数 - 1 and 顶层挡板高度 > 0:
            挡板 = trimesh.creation.box(
                extents=[长度 - 2*立柱宽度 - 20, 20, 顶层挡板高度]
            )
            挡板.apply_translation([0, -深度/2 + 立柱深度/2 + 10, 当前高度 + 层板厚度 + 顶层挡板高度/2])
            set_mesh_color(挡板, 层板颜色)
            meshes.append(挡板)
    
    # 创建Scene
    scene = create_scene(meshes)
    
    # 元数据（中文参数格式）
    metadata = {
        "id": f"light-duty-A{int(长度/100)}-{层数}",
        "name": f"{层数}层轻型货架-L{长度/1000:.1f}xD{深度/1000:.1f}xH{高度/1000:.1f}",
        "category": "light-shelf",
        "description": f"标准{层数}层轻型搁板式货架，适合3米以下仓库，人工存取轻型货物，单层层载{层载重}kg，层高{标准层高}mm，顶层配{顶层挡板高度}cm挡板",
        "tags": ["轻型货架", "搁板式", "人工存取", f"A{int(长度/100)}系列"],
        "parameters": {
            "长度": {"type": "number", "min": 长度, "max": 长度, "default": 长度, "unit": "mm"},
            "深度": {"type": "number", "min": 深度, "max": 深度, "default": 深度, "unit": "mm"},
            "高度": {"type": "number", "min": 高度, "max": 高度, "default": 高度, "unit": "mm"},
            "层数": {"type": "number", "min": 层数, "max": 层数, "default": 层数, "unit": "层"},
            "层载重": {"type": "number", "min": 300, "max": 800, "default": 层载重, "unit": "kg"},
            "标准层高": {"type": "number", "min": 标准层高, "max": 标准层高, "default": 标准层高, "unit": "mm"},
            "层板厚度": {"type": "number", "min": 层板厚度, "max": 层板厚度, "default": 层板厚度, "unit": "mm"},
            "适配净高": {"type": "string", "default": "3米以下"},
            "立柱颜色": {"type": "color", "default": 立柱颜色},
            "横梁颜色": {"type": "color", "default": 横梁颜色},
            "层板颜色": {"type": "color", "default": 层板颜色}
        }
    }
    
    return scene, metadata


# 颜色库 - 常用物流设备颜色
COLORS = {
    'blue': [0.18, 0.25, 0.45],      # 深蓝（立柱）
    'light_blue': [0.25, 0.45, 0.85], # 浅蓝
    'orange': [0.85, 0.45, 0.15],     # 橙色（横梁）
    'gray': [0.75, 0.75, 0.75],       # 灰色（层板）
    'dark_gray': [0.39, 0.39, 0.39],  # 深灰
    'white': [0.96, 0.96, 0.96],      # 白色
    'brown': [0.55, 0.35, 0.20],      # 棕色（木质）
    'yellow': [0.95, 0.85, 0.15],     # 黄色（安全标识）
    'green': [0.20, 0.60, 0.30],      # 绿色
    'red': [0.80, 0.20, 0.20],        # 红色（警示）
}


if __name__ == "__main__":
    # 测试代码
    print("测试生成标准货架...")
    scene, metadata = generate_shelf(length=2300, width=1000, height=4500, levels=3)
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    
    print("\n测试生成轻型货架（增强版）- 4层...")
    scene, metadata = generate_light_duty_shelf(
        长度=1500, 深度=400, 高度=2000, 层数=4,
        层载重=500, 标准层高=600, 层板厚度=20,
        立柱颜色="#B0C4DE", 横梁颜色="#FF4500", 层板颜色="#FFFFFF",
        顶层挡板高度=50
    )
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    print(f"元数据: {metadata}")
    
    # 导出GLB文件
    output_path = "../frontend/public/assets/models/light-duty-A15-4.glb"
    export_glb(scene, output_path, metadata)
    print(f"已导出: {output_path}")
    
    print("\n测试生成轻型货架（增强版）- 5层...")
    scene, metadata = generate_light_duty_shelf(
        长度=1500, 深度=400, 高度=2000, 层数=5,
        层载重=500, 标准层高=600, 层板厚度=20,
        立柱颜色="#B0C4DE", 横梁颜色="#FF4500", 层板颜色="#FFFFFF",
        顶层挡板高度=50
    )
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    
    # 导出GLB文件
    output_path = "../frontend/public/assets/models/light-duty-A15-5.glb"
    export_glb(scene, output_path, metadata)
    print(f"已导出: {output_path}")
    
    print("\n测试生成轻型货架（增强版）- A20系列 4层...")
    scene, metadata = generate_light_duty_shelf(
        长度=2000, 深度=600, 高度=2000, 层数=4,
        层载重=500, 标准层高=600, 层板厚度=20,
        立柱颜色="#B0C4DE", 横梁颜色="#FF4500", 层板颜色="#FFFFFF",
        顶层挡板高度=50
    )
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    
    # 导出GLB文件
    output_path = "../frontend/public/assets/models/light-duty-A20-4.glb"
    export_glb(scene, output_path, metadata)
    print(f"已导出: {output_path}")
    
    print("\n测试生成轻型货架（增强版）- A20系列 5层...")
    scene, metadata = generate_light_duty_shelf(
        长度=2000, 深度=600, 高度=2500, 层数=5,
        层载重=500, 标准层高=600, 层板厚度=20,
        立柱颜色="#B0C4DE", 横梁颜色="#FF4500", 层板颜色="#FFFFFF",
        顶层挡板高度=50
    )
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    
    # 导出GLB文件
    output_path = "../frontend/public/assets/models/light-duty-A20-5.glb"
    export_glb(scene, output_path, metadata)
    print(f"已导出: {output_path}")
    
    print("\n测试生成轻型货架（增强版）- A20系列 6层...")
    scene, metadata = generate_light_duty_shelf(
        长度=2000, 深度=600, 高度=3000, 层数=6,
        层载重=500, 标准层高=600, 层板厚度=20,
        立柱颜色="#B0C4DE", 横梁颜色="#FF4500", 层板颜色="#FFFFFF",
        顶层挡板高度=50
    )
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    
    # 导出GLB文件
    output_path = "../frontend/public/assets/models/light-duty-A20-6.glb"
    export_glb(scene, output_path, metadata)
    print(f"已导出: {output_path}")
    
    print("\n测试生成周转箱...")
    scene, metadata = generate_box_container(length=600, width=400, height=300)
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
    
    print("\n测试生成托盘...")
    scene, metadata = generate_pallet(length=1200, width=1000)
    print(f"生成成功: {metadata['name']}")
    print(f"几何体数量: {len(scene.geometry)}")
