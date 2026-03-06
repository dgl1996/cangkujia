"""检查scenes和nodes定义"""
import json
import struct
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

def get_glb_json(path):
    with open(path, 'rb') as f:
        f.read(12)  # skip header
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        f.read(4)  # skip chunk type
        json_data = f.read(json_chunk_length)
        return json.loads(json_data.decode('utf-8'))

print("=" * 80)
print("检查scenes和nodes定义")
print("=" * 80)

models = [
    ("shelf-light-v2.glb", "V2"),
    ("shelf-beam-heavy-3level.glb", "Heavy 3L"),
]

for filename, desc in models:
    path = models_dir / filename
    gltf = get_glb_json(path)
    
    print(f"\n📦 {desc}")
    print("-" * 80)
    
    # 检查scenes
    scenes = gltf.get('scenes', [])
    print(f"Scenes ({len(scenes)}):")
    for i, scene in enumerate(scenes):
        print(f"  Scene {i}: nodes = {scene.get('nodes', [])}")
    
    # 检查nodes
    nodes = gltf.get('nodes', [])
    print(f"\nNodes ({len(nodes)}):")
    for i, node in enumerate(nodes[:5]):  # 只显示前5个
        print(f"  Node {i}: {json.dumps(node, indent=2)[:100]}...")

print("\n" + "=" * 80)
