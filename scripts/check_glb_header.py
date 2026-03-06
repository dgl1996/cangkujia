"""检查GLB文件头信息"""
from pathlib import Path
import struct

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 70)
print("检查GLB文件头信息")
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
        magic = header[:4]
        version = struct.unpack('<I', header[4:8])[0]
        length = struct.unpack('<I', header[8:12])[0]
        
        print(f"  Magic: {magic}")
        print(f"  Version: {version}")
        print(f"  Total Length: {length} bytes")
        
        # 读取前几个chunk
        print(f"\n  Chunks:")
        offset = 12
        chunk_num = 0
        while offset < length and chunk_num < 3:
            f.seek(offset)
            chunk_length = struct.unpack('<I', f.read(4))[0]
            chunk_type = struct.unpack('<I', f.read(4))[0]
            
            type_name = "JSON" if chunk_type == 0x4E4F534A else "BIN" if chunk_type == 0x004E4942 else f"0x{chunk_type:08X}"
            print(f"    Chunk {chunk_num}: {type_name}, {chunk_length} bytes")
            
            offset += 8 + chunk_length
            chunk_num += 1

print("\n" + "=" * 70)
