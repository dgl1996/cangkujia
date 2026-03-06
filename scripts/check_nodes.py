"""检查GLB文件的nodes结构"""
from pathlib import Path
import struct
import json

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 70)
print("检查GLB文件的nodes结构")
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
        
        # 读取JSON chunk
        f.seek(12)
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        json_chunk_type = struct.unpack('<I', f.read(4))[0]
        
        json_data = f.read(json_chunk_length)
        gltf = json.loads(json_data.decode('utf-8'))
        
        # 检查scene
        scenes = gltf.get('scenes', [])
        if scenes:
            print(f"  Scene[0] nodes: {scenes[0].get('nodes', [])}")
        
        # 检查前几个nodes
        nodes = gltf.get('nodes', [])
        print(f"\n  前3个Nodes:")
        for i, node in enumerate(nodes[:3]):
            print(f"    Node {i}: {node}")
        
        # 检查是否有mesh的node
        mesh_nodes = [n for n in nodes if 'mesh' in n]
        print(f"\n  有mesh的nodes数量: {len(mesh_nodes)}")

print("\n" + "=" * 70)
