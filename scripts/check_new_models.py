"""检查新生成的模型"""
import trimesh
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 70)
print("检查新生成的重型货架模型")
print("=" * 70)

models = [
    "shelf-beam-heavy-3level.glb",
    "shelf-beam-heavy-4level.glb",
    "shelf-beam-heavy-5level.glb",
]

for filename in models:
    path = models_dir / filename
    print(f"\n📦 {filename}")
    print("-" * 70)
    
    scene = trimesh.load(str(path))
    
    if isinstance(scene, trimesh.Scene):
        print(f"  类型: Scene")
        print(f"  几何体数量: {len(scene.geometry)}")
        print(f"  节点数量: {len(scene.graph.nodes)}")
        print(f"  几何体名称: {list(scene.geometry.keys())[:5]}")
        
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
        else:
            print(f"    顶点颜色: 无")
    else:
        print(f"  类型: {type(scene).__name__} ⚠️ 不是Scene")

print("\n" + "=" * 70)
