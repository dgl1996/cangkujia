"""验证生成的GLB文件"""
import trimesh
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

# 要验证的模型
models_to_check = [
    "shelf-beam-heavy-3level.glb",
    "shelf-beam-heavy-4level.glb",
    "shelf-beam-heavy-5level.glb",
]

print("=" * 50)
print("验证GLB模型文件")
print("=" * 50)

for model_name in models_to_check:
    model_path = models_dir / model_name
    print(f"\n📦 {model_name}")
    print(f"   文件大小: {model_path.stat().st_size} bytes")
    
    try:
        # 加载模型
        scene = trimesh.load(str(model_path))
        
        if isinstance(scene, trimesh.Scene):
            print(f"   类型: Scene")
            print(f"   几何体数量: {len(scene.geometry)}")
            print(f"   节点数量: {len(scene.graph.nodes)}")
            
            # 检查每个几何体
            for name, geom in scene.geometry.items():
                print(f"   - {name}: {len(geom.vertices)} 顶点, {len(geom.faces)} 面")
                
                # 检查材质
                if hasattr(geom.visual, 'material') and geom.visual.material:
                    print(f"     材质: {type(geom.visual.material).__name__}")
                else:
                    print(f"     材质: 无")
            
            print("   ✅ 验证通过")
        else:
            print(f"   类型: {type(scene).__name__}")
            print(f"   ⚠️  不是Scene类型")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")

print("\n" + "=" * 50)
print("验证完成")
print("=" * 50)
