"""比较V2模型和新生成的模型"""
import trimesh
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 60)
print("模型对比分析")
print("=" * 60)

models = [
    ("shelf-light-v2.glb", "V2 (可正常显示)"),
    ("shelf-beam-heavy-3level.glb", "3层重型"),
    ("shelf-beam-heavy-4level.glb", "4层重型"),
    ("shelf-beam-heavy-5level.glb", "5层重型"),
]

for filename, desc in models:
    path = models_dir / filename
    print(f"\n📦 {desc}: {filename}")
    print("-" * 60)
    
    try:
        scene = trimesh.load(str(path))
        
        if isinstance(scene, trimesh.Scene):
            print(f"  类型: Scene ✓")
            print(f"  几何体数量: {len(scene.geometry)}")
            
            # 检查第一个几何体的顶点颜色
            first_geom = list(scene.geometry.values())[0]
            has_vertex_colors = hasattr(first_geom.visual, 'vertex_colors') and first_geom.visual.vertex_colors is not None
            print(f"  顶点颜色: {'✓ 有' if has_vertex_colors else '✗ 无'}")
            
            if has_vertex_colors:
                print(f"  顶点颜色数量: {len(first_geom.visual.vertex_colors)}")
            
            # 检查材质
            has_material = hasattr(first_geom.visual, 'material') and first_geom.visual.material is not None
            print(f"  材质: {'✓ 有' if has_material else '✗ 无'}")
            
            if has_material:
                print(f"  材质类型: {type(first_geom.visual.material).__name__}")
        else:
            print(f"  类型: {type(scene).__name__} ⚠️ 不是Scene")
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")

print("\n" + "=" * 60)
