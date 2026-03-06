from pathlib import Path

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("货架模型文件大小:")
print("-" * 50)
for f in sorted(models_dir.glob("shelf-*.glb")):
    size_kb = f.stat().st_size / 1024
    print(f"{f.name:40s} {size_kb:8.2f} KB")
