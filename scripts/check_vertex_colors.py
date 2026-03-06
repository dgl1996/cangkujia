"""详细检查顶点颜色"""
import trimesh
import numpy as np
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 60)
print("顶点颜色详细检查")
print("=" * 60)

models = [
    ("shelf-light-v2.glb", "V2 (可正常显示)"),
    ("shelf-beam-heavy-3level.glb", "3层重型"),
]

for filename, desc in models:
    path = models_dir / filename
    print(f"\n📦 {desc}: {filename}")
    print("-" * 60)
    
    scene = trimesh.load(str(path))
    
    if isinstance(scene, trimesh.Scene):
        for name, geom in list(scene.geometry.items())[:3]:  # 只检查前3个
            print(f"\n  几何体: {name}")
            print(f"    顶点数: {len(geom.vertices)}")
            
            if hasattr(geom.visual, 'vertex_colors') and geom.visual.vertex_colors is not None:
                colors = geom.visual.vertex_colors
                print(f"    顶点颜色数: {len(colors)}")
                print(f"    颜色形状: {colors.shape}")
                print(f"    第一个颜色: {colors[0] if len(colors) > 0 else 'N/A'}")
            else:
                print(f"    顶点颜色: 无")

print("\n" + "=" * 60)
