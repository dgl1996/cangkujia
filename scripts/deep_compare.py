"""深度对比V2和新生成的模型"""
import trimesh
import json
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 70)
print("深度对比V2和新生成的模型")
print("=" * 70)

models = [
    ("shelf-light-v2.glb", "V2 (可正常显示)"),
    ("shelf-beam-heavy-3level.glb", "3层重型"),
]

for filename, desc in models:
    path = models_dir / filename
    print(f"\n📦 {desc}: {filename}")
    print("-" * 70)
    
    scene = trimesh.load(str(path))
    
    if isinstance(scene, trimesh.Scene):
        print(f"  类型: Scene")
        print(f"  几何体数量: {len(scene.geometry)}")
        print(f"  节点数量: {len(scene.graph.nodes)}")
        print(f"  节点列表: {list(scene.graph.nodes)[:5]}...")  # 前5个
        
        # 检查第一个几何体
        first_name = list(scene.geometry.keys())[0]
        first_geom = scene.geometry[first_name]
        
        print(f"\n  第一个几何体 '{first_name}':")
        print(f"    顶点数: {len(first_geom.vertices)}")
        print(f"    面数: {len(first_geom.faces)}")
        
        # 顶点颜色
        if hasattr(first_geom.visual, 'vertex_colors') and first_geom.visual.vertex_colors is not None:
            colors = first_geom.visual.vertex_colors
            print(f"    顶点颜色: 有")
            print(f"    颜色数组形状: {colors.shape}")
            print(f"    颜色数据类型: {colors.dtype}")
            print(f"    前3个颜色:\n{colors[:3]}")
        else:
            print(f"    顶点颜色: 无")
        
        # 检查GLB导出信息
        print(f"\n  Scene元数据:")
        if hasattr(scene, 'metadata'):
            print(f"    {scene.metadata}")
        
        # 检查graph结构
        print(f"\n  Graph边 (前3条):")
        edges = list(scene.graph.edges)[:3]
        for edge in edges:
            print(f"    {edge}")

print("\n" + "=" * 70)
