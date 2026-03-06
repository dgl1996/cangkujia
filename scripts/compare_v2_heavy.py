"""深度对比V2和重型货架的所有差异"""
import trimesh
import json
import struct
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 80)
print("深度对比V2和重型货架")
print("=" * 80)

# 加载两个模型
v2_path = models_dir / "shelf-light-v2.glb"
heavy_path = models_dir / "shelf-beam-heavy-3level.glb"

v2_scene = trimesh.load(str(v2_path))
heavy_scene = trimesh.load(str(heavy_path))

print("\n📊 基本结构对比")
print("-" * 80)
print(f"{'属性':<30} {'V2':<25} {'重型3层':<25}")
print("-" * 80)
print(f"{'类型':<30} {type(v2_scene).__name__:<25} {type(heavy_scene).__name__:<25}")
print(f"{'几何体数量':<30} {len(v2_scene.geometry):<25} {len(heavy_scene.geometry):<25}")
print(f"{'节点数量':<30} {len(v2_scene.graph.nodes):<25} {len(heavy_scene.graph.nodes):<25}")

# 检查第一个几何体的详细信息
print("\n📦 第一个几何体对比")
print("-" * 80)

v2_first = list(v2_scene.geometry.values())[0]
heavy_first = list(heavy_scene.geometry.values())[0]

print(f"{'属性':<30} {'V2':<25} {'重型3层':<25}")
print("-" * 80)
print(f"{'顶点数':<30} {len(v2_first.vertices):<25} {len(heavy_first.vertices):<25}")
print(f"{'面数':<30} {len(v2_first.faces):<25} {len(heavy_first.faces):<25}")

# 顶点颜色
v2_has_colors = hasattr(v2_first.visual, 'vertex_colors') and v2_first.visual.vertex_colors is not None
heavy_has_colors = hasattr(heavy_first.visual, 'vertex_colors') and heavy_first.visual.vertex_colors is not None

print(f"{'有顶点颜色':<30} {str(v2_has_colors):<25} {str(heavy_has_colors):<25}")

if v2_has_colors and heavy_has_colors:
    v2_colors = v2_first.visual.vertex_colors
    heavy_colors = heavy_first.visual.vertex_colors
    print(f"{'顶点颜色数量':<30} {len(v2_colors):<25} {len(heavy_colors):<25}")
    print(f"{'顶点颜色形状':<30} {str(v2_colors.shape):<25} {str(heavy_colors.shape):<25}")
    print(f"{'顶点颜色dtype':<30} {str(v2_colors.dtype):<25} {str(heavy_colors.dtype):<25}")
    print(f"{'第一个颜色值':<30} {str(v2_colors[0]):<25} {str(heavy_colors[0]):<25}")

# 检查bounds
print(f"{'Bounds':<30} {str(v2_first.bounds):<25} {str(heavy_first.bounds):<25}")

# 检查GLB JSON内容
print("\n📄 GLB JSON内容对比")
print("-" * 80)

def get_glb_json(path):
    with open(path, 'rb') as f:
        header = f.read(12)
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        json_chunk_type = struct.unpack('<I', f.read(4))[0]
        json_data = f.read(json_chunk_length)
        return json.loads(json_data.decode('utf-8'))

v2_gltf = get_glb_json(v2_path)
heavy_gltf = get_glb_json(heavy_path)

print(f"{'属性':<30} {'V2':<25} {'重型3层':<25}")
print("-" * 80)
print(f"{'asset版本':<30} {v2_gltf.get('asset', {}).get('version', 'N/A'):<25} {heavy_gltf.get('asset', {}).get('version', 'N/A'):<25}")
print(f"{'scenes数量':<30} {len(v2_gltf.get('scenes', [])):<25} {len(heavy_gltf.get('scenes', [])):<25}")
print(f"{'nodes数量':<30} {len(v2_gltf.get('nodes', [])):<25} {len(heavy_gltf.get('nodes', [])):<25}")
print(f"{'meshes数量':<30} {len(v2_gltf.get('meshes', [])):<25} {len(heavy_gltf.get('meshes', [])):<25}")
print(f"{'materials数量':<30} {len(v2_gltf.get('materials', [])):<25} {len(heavy_gltf.get('materials', [])):<25}")
print(f"{'buffers数量':<30} {len(v2_gltf.get('buffers', [])):<25} {len(heavy_gltf.get('buffers', [])):<25}")
print(f"{'bufferViews数量':<30} {len(v2_gltf.get('bufferViews', [])):<25} {len(heavy_gltf.get('bufferViews', [])):<25}")
print(f"{'accessors数量':<30} {len(v2_gltf.get('accessors', [])):<25} {len(heavy_gltf.get('accessors', [])):<25}")

# 检查第一个mesh的primitive
print("\n🔍 第一个Mesh的Primitive对比")
print("-" * 80)

v2_mesh = v2_gltf.get('meshes', [{}])[0]
heavy_mesh = heavy_gltf.get('meshes', [{}])[0]

v2_prim = v2_mesh.get('primitives', [{}])[0]
heavy_prim = heavy_mesh.get('primitives', [{}])[0]

print(f"{'属性':<30} {'V2':<25} {'重型3层':<25}")
print("-" * 80)
print(f"{'attributes':<30} {str(list(v2_prim.get('attributes', {}).keys())):<25} {str(list(heavy_prim.get('attributes', {}).keys())):<25}")
print(f"{'indices':<30} {str(v2_prim.get('indices', 'N/A')):<25} {str(heavy_prim.get('indices', 'N/A')):<25}")
print(f"{'material':<30} {str(v2_prim.get('material', 'N/A')):<25} {str(heavy_prim.get('material', 'N/A')):<25}")
print(f"{'mode':<30} {str(v2_prim.get('mode', 'N/A')):<25} {str(heavy_prim.get('mode', 'N/A')):<25}")

print("\n" + "=" * 80)
