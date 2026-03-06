"""对比两个GLB文件的十六进制内容"""
from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

v2_path = models_dir / "shelf-light-v2.glb"
heavy_path = models_dir / "shelf-beam-heavy-3level.glb"

print("=" * 80)
print("对比GLB文件的前200字节")
print("=" * 80)

with open(v2_path, 'rb') as f:
    v2_data = f.read(200)

with open(heavy_path, 'rb') as f:
    heavy_data = f.read(200)

print(f"\n{'Offset':<10} {'V2':<50} {'Heavy 3L':<50}")
print("-" * 110)

for i in range(0, min(len(v2_data), len(heavy_data)), 16):
    v2_hex = v2_data[i:i+16].hex()
    heavy_hex = heavy_data[i:i+16].hex()
    match = "✓" if v2_hex == heavy_hex else "✗"
    print(f"{i:<10} {v2_hex:<50} {heavy_hex:<50} {match}")

print("\n" + "=" * 80)
