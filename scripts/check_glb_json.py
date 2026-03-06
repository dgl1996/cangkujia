"""检查GLB文件的JSON内容"""
from pathlib import Path
import struct
import json

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 70)
print("检查GLB文件的JSON内容")
print("=" * 70)

models = [
    ("shelf-light-v2.glb", "V2 (可正常显示)"),
    ("shelf-beam-heavy-3level.glb", "3层重型"),
]

for filename, desc in models:
    path = models_dir / filename
    print(f"\n📦 {desc}: {filename}")
    print("-" * 70)
    
    with open(path, 'rb') as f:
        # 读取GLB头
        header = f.read(12)
        length = struct.unpack('<I', header[8:12])[0]
        
        # 读取JSON chunk
        f.seek(12)
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        json_chunk_type = struct.unpack('<I', f.read(4))[0]
        
        json_data = f.read(json_chunk_length)
        gltf = json.loads(json_data.decode('utf-8'))
        
        # 检查关键字段
        print(f"  Asset: {gltf.get('asset', {})}")
        print(f"  Scene: {gltf.get('scene', 'N/A')}")
        print(f"  Scenes数量: {len(gltf.get('scenes', []))}")
        print(f"  Nodes数量: {len(gltf.get('nodes', []))}")
        print(f"  Meshes数量: {len(gltf.get('meshes', []))}")
        print(f"  Materials数量: {len(gltf.get('materials', []))}")
        print(f"  Buffers数量: {len(gltf.get('buffers', []))}")
        print(f"  BufferViews数量: {len(gltf.get('bufferViews', []))}")
        print(f"  Accessors数量: {len(gltf.get('accessors', []))}")
        
        # 检查第一个mesh
        meshes = gltf.get('meshes', [])
        if meshes:
            print(f"\n  第一个Mesh:")
            print(f"    Name: {meshes[0].get('name', 'N/A')}")
            print(f"    Primitives: {len(meshes[0].get('primitives', []))}")
            
            prim = meshes[0].get('primitives', [{}])[0]
            print(f"    Attributes: {list(prim.get('attributes', {}).keys())}")
            print(f"    Material: {prim.get('material', 'N/A')}")

print("\n" + "=" * 70)
