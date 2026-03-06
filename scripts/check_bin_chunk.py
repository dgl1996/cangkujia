"""检查GLB文件的BIN chunk"""
from pathlib import Path
import struct

models_dir = Path(__file__).parent.parent / "frontend" / "public" / "assets" / "models"

print("=" * 80)
print("检查GLB文件的BIN chunk")
print("=" * 80)

models = [
    ("shelf-light-v2.glb", "V2 (可正常显示)"),
    ("shelf-beam-heavy-3level.glb", "3层重型"),
]

for filename, desc in models:
    path = models_dir / filename
    print(f"\n📦 {desc}: {filename}")
    print("-" * 80)
    
    with open(path, 'rb') as f:
        # 读取GLB头
        header = f.read(12)
        total_length = struct.unpack('<I', header[8:12])[0]
        
        # 读取JSON chunk
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        json_chunk_type = struct.unpack('<I', f.read(4))[0]
        json_data = f.read(json_chunk_length)
        
        print(f"  JSON chunk: {json_chunk_length} bytes")
        
        # 读取BIN chunk
        bin_chunk_start = 12 + 8 + json_chunk_length
        f.seek(bin_chunk_start)
        
        if bin_chunk_start < total_length:
            bin_chunk_length = struct.unpack('<I', f.read(4))[0]
            bin_chunk_type = struct.unpack('<I', f.read(4))[0]
            
            print(f"  BIN chunk: {bin_chunk_length} bytes")
            print(f"  BIN chunk type: 0x{bin_chunk_type:08X}")
            
            # 读取BIN数据的前几个字节
            bin_data = f.read(min(64, bin_chunk_length))
            print(f"  BIN data前64字节: {bin_data[:64].hex()}")
        else:
            print(f"  没有BIN chunk")

print("\n" + "=" * 80)
