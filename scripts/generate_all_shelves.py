"""
仓酷家 40个货架模型批量生成脚本
基于 docs/shelf-specs.md 规格生成全部模型
"""

import sys
sys.path.insert(0, '.')

from model_generator_template import (
    generate_light_duty_shelf, 
    generate_pair_shelf, 
    export_glb,
    LIGHT_SHELF_COLORS,
    MEDIUM_SHELF_COLORS,
    HIGH_SHELF_COLORS,
    LIGHT_SHELF_SIZES,
    MEDIUM_SHELF_SIZES,
    HIGH_SHELF_SIZES
)

# 40个货架规格定义
SHELF_SPECS = [
    # 轻型货架 (10个)
    {"id": "light-duty-A15-4", "name": "4层轻型货架-L1.5xD0.4xH2.0", "category": "light-shelf", 
     "length": 1500, "depth": 400, "height": 2000, "levels": 4, "pair": False, "prebuilt": True},
    {"id": "light-duty-A15-5", "name": "5层轻型货架-L1.5xD0.4xH2.0", "category": "light-shelf",
     "length": 1500, "depth": 400, "height": 2000, "levels": 5, "pair": False, "prebuilt": False},
    {"id": "light-duty-A20-4", "name": "4层轻型货架-L2.0xD0.6xH2.0", "category": "light-shelf",
     "length": 2000, "depth": 600, "height": 2000, "levels": 4, "pair": False, "prebuilt": False},
    {"id": "light-duty-A20-5", "name": "5层轻型货架-L2.0xD0.6xH2.5", "category": "light-shelf",
     "length": 2000, "depth": 600, "height": 2500, "levels": 5, "pair": False, "prebuilt": False},
    {"id": "light-duty-A20-6", "name": "6层轻型货架-L2.0xD0.6xH3.0", "category": "light-shelf",
     "length": 2000, "depth": 600, "height": 3000, "levels": 6, "pair": False, "prebuilt": False},
    {"id": "light-duty-A15-4-pair", "name": "4层轻型货架-L1.5xD0.4xH2.0-配组", "category": "light-shelf",
     "length": 1500, "depth": 400, "height": 2000, "levels": 4, "pair": True, "prebuilt": True},
    {"id": "light-duty-A15-5-pair", "name": "5层轻型货架-L1.5xD0.4xH2.0-配组", "category": "light-shelf",
     "length": 1500, "depth": 400, "height": 2000, "levels": 5, "pair": True, "prebuilt": False},
    {"id": "light-duty-A20-4-pair", "name": "4层轻型货架-L2.0xD0.6xH2.0-配组", "category": "light-shelf",
     "length": 2000, "depth": 600, "height": 2000, "levels": 4, "pair": True, "prebuilt": False},
    {"id": "light-duty-A20-5-pair", "name": "5层轻型货架-L2.0xD0.6xH2.5-配组", "category": "light-shelf",
     "length": 2000, "depth": 600, "height": 2500, "levels": 5, "pair": True, "prebuilt": False},
    {"id": "light-duty-A20-6-pair", "name": "6层轻型货架-L2.0xD0.6xH3.0-配组", "category": "light-shelf",
     "length": 2000, "depth": 600, "height": 3000, "levels": 6, "pair": True, "prebuilt": False},
    
    # 中型货架 (7个，注意C23-3属于高位货架)
    {"id": "medium-duty-B20-4", "name": "4层中型货架-L2.0xD0.6xH2.0", "category": "medium-shelf",
     "length": 2000, "depth": 600, "height": 2000, "levels": 4, "pair": False, "prebuilt": True},
    {"id": "medium-duty-B20-5", "name": "5层中型货架-L2.0xD0.6xH2.5", "category": "medium-shelf",
     "length": 2000, "depth": 600, "height": 2500, "levels": 5, "pair": False, "prebuilt": False},
    {"id": "medium-duty-B20-6", "name": "6层中型货架-L2.0xD0.6xH3.0", "category": "medium-shelf",
     "length": 2000, "depth": 600, "height": 3000, "levels": 6, "pair": False, "prebuilt": False},
    {"id": "medium-duty-B20-4-pair", "name": "4层中型货架-L2.0xD0.6xH2.0-配组", "category": "medium-shelf",
     "length": 2000, "depth": 600, "height": 2000, "levels": 4, "pair": True, "prebuilt": True},
    {"id": "medium-duty-B20-5-pair", "name": "5层中型货架-L2.0xD0.6xH2.5-配组", "category": "medium-shelf",
     "length": 2000, "depth": 600, "height": 2500, "levels": 5, "pair": True, "prebuilt": False},
    {"id": "medium-duty-B20-6-pair", "name": "6层中型货架-L2.0xD0.6xH3.0-配组", "category": "medium-shelf",
     "length": 2000, "depth": 600, "height": 3000, "levels": 6, "pair": True, "prebuilt": False},
    
    # C23-3 高位货架 (2个)
    {"id": "high-duty-C23-3", "name": "3层高位货架-L2.3xD1.0xH3.0", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 3000, "levels": 3, "pair": False, "prebuilt": False},
    {"id": "high-duty-C23-3-pair", "name": "3层高位货架-L2.3xD1.0xH3.0-配组", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 3000, "levels": 3, "pair": True, "prebuilt": False},
    
    # 高位货架 C23系列 (5个)
    {"id": "high-duty-C23-4", "name": "4层高位货架-L2.3xD1.0xH4.5", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 4500, "levels": 4, "pair": False, "prebuilt": True},
    {"id": "high-duty-C23-5", "name": "5层高位货架-L2.3xD1.0xH6.0", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 6000, "levels": 5, "pair": False, "prebuilt": False},
    {"id": "high-duty-C23-6", "name": "6层高位货架-L2.3xD1.0xH7.0", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 7000, "levels": 6, "pair": False, "prebuilt": False},
    {"id": "high-duty-C23-4-pair", "name": "4层高位货架-L2.3xD1.0xH4.5-配组", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 4500, "levels": 4, "pair": True, "prebuilt": True},
    {"id": "high-duty-C23-5-pair", "name": "5层高位货架-L2.3xD1.0xH6.0-配组", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 6000, "levels": 5, "pair": True, "prebuilt": False},
    {"id": "high-duty-C23-6-pair", "name": "6层高位货架-L2.3xD1.0xH7.0-配组", "category": "high-shelf",
     "length": 2300, "depth": 1000, "height": 7000, "levels": 6, "pair": True, "prebuilt": False},
    
    # 高位货架 C25系列 (8个)
    {"id": "high-duty-C25-3", "name": "3层高位货架-L2.5xD1.0xH3.0", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 3000, "levels": 3, "pair": False, "prebuilt": False},
    {"id": "high-duty-C25-4", "name": "4层高位货架-L2.5xD1.0xH4.5", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 4500, "levels": 4, "pair": False, "prebuilt": False},
    {"id": "high-duty-C25-5", "name": "5层高位货架-L2.5xD1.0xH6.0", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 6000, "levels": 5, "pair": False, "prebuilt": False},
    {"id": "high-duty-C25-6", "name": "6层高位货架-L2.5xD1.0xH7.0", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 7000, "levels": 6, "pair": False, "prebuilt": False},
    {"id": "high-duty-C25-3-pair", "name": "3层高位货架-L2.5xD1.0xH3.0-配组", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 3000, "levels": 3, "pair": True, "prebuilt": False},
    {"id": "high-duty-C25-4-pair", "name": "4层高位货架-L2.5xD1.0xH4.5-配组", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 4500, "levels": 4, "pair": True, "prebuilt": False},
    {"id": "high-duty-C25-5-pair", "name": "5层高位货架-L2.5xD1.0xH6.0-配组", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 6000, "levels": 5, "pair": True, "prebuilt": False},
    {"id": "high-duty-C25-6-pair", "name": "6层高位货架-L2.5xD1.0xH7.0-配组", "category": "high-shelf",
     "length": 2500, "depth": 1000, "height": 7000, "levels": 6, "pair": True, "prebuilt": False},
    
    # 高位货架 C27系列 (8个)
    {"id": "high-duty-C27-3", "name": "3层高位货架-L2.7xD1.0xH3.2", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 3200, "levels": 3, "pair": False, "prebuilt": False},
    {"id": "high-duty-C27-4", "name": "4层高位货架-L2.7xD1.0xH4.5", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 4500, "levels": 4, "pair": False, "prebuilt": False},
    {"id": "high-duty-C27-5", "name": "5层高位货架-L2.7xD1.0xH6.0", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 6000, "levels": 5, "pair": False, "prebuilt": False},
    {"id": "high-duty-C27-6", "name": "6层高位货架-L2.7xD1.0xH7.5", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 7500, "levels": 6, "pair": False, "prebuilt": False},
    {"id": "high-duty-C27-3-pair", "name": "3层高位货架-L2.7xD1.0xH3.2-配组", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 3200, "levels": 3, "pair": True, "prebuilt": False},
    {"id": "high-duty-C27-4-pair", "name": "4层高位货架-L2.7xD1.0xH4.5-配组", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 4500, "levels": 4, "pair": True, "prebuilt": False},
    {"id": "high-duty-C27-5-pair", "name": "5层高位货架-L2.7xD1.0xH6.0-配组", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 6000, "levels": 5, "pair": True, "prebuilt": False},
    {"id": "high-duty-C27-6-pair", "name": "6层高位货架-L2.7xD1.0xH7.5-配组", "category": "high-shelf",
     "length": 2700, "depth": 1000, "height": 7500, "levels": 6, "pair": True, "prebuilt": False},
]


def generate_shelf_model(spec):
    """根据规格生成单个货架模型"""
    
    # 确定货架类型和参数
    if spec["category"] == "light-shelf":
        colors = LIGHT_SHELF_COLORS
        sizes = LIGHT_SHELF_SIZES
        层载重 = 500
        标准层高 = 600
    elif spec["category"] == "medium-shelf":
        colors = MEDIUM_SHELF_COLORS
        sizes = MEDIUM_SHELF_SIZES
        层载重 = 800
        标准层高 = 600
    else:  # high-shelf
        colors = HIGH_SHELF_COLORS
        sizes = HIGH_SHELF_SIZES
        层载重 = 1500
        标准层高 = 1350 if spec["height"] <= 3200 else 1500
    
    # 确定顶层挡板高度
    if spec["category"] == "high-shelf":
        顶层挡板高度 = 300 if spec["height"] <= 4500 else 500
    else:
        顶层挡板高度 = 50
    
    # 确定侧拉梁参数（只有高位货架需要）
    生成侧拉梁 = spec["category"] == "high-shelf"
    侧拉梁尺寸 = (40, 25) if 生成侧拉梁 else (40, 25)
    侧拉梁位置 = (0.2, 0.8)
    
    # 配组参数
    背靠背间距 = 200 if spec["category"] == "high-shelf" else 0
    
    print(f"生成: {spec['name']} ({spec['id']})")
    
    if spec["pair"]:
        # 生成配组货架
        scene, metadata = generate_pair_shelf(
            generate_light_duty_shelf,
            spacing=背靠背间距,
            长度=spec["length"],
            深度=spec["depth"],
            高度=spec["height"],
            层数=spec["levels"],
            层载重=层载重,
            标准层高=标准层高,
            层板厚度=sizes['deck_thickness'],
            立柱颜色=colors['upright'],
            横梁颜色=colors['beam'],
            层板颜色=colors['deck'],
            顶层挡板高度=顶层挡板高度,
            立柱尺寸=sizes['upright'],
            横梁尺寸=sizes['beam'],
            侧拉梁尺寸=侧拉梁尺寸,
            侧拉梁位置=侧拉梁位置,
            生成侧拉梁=生成侧拉梁,
            背靠背侧拉梁=True,
            背靠背间距=背靠背间距
        )
        # 修改元数据
        metadata['id'] = spec['id']
        metadata['name'] = spec['name']
        metadata['category'] = spec['category']
        metadata['prebuilt'] = spec['prebuilt']
    else:
        # 生成单组货架
        scene, metadata = generate_light_duty_shelf(
            长度=spec["length"],
            深度=spec["depth"],
            高度=spec["height"],
            层数=spec["levels"],
            层载重=层载重,
            标准层高=标准层高,
            层板厚度=sizes['deck_thickness'],
            立柱颜色=colors['upright'],
            横梁颜色=colors['beam'],
            层板颜色=colors['deck'],
            顶层挡板高度=顶层挡板高度,
            立柱尺寸=sizes['upright'],
            横梁尺寸=sizes['beam'],
            侧拉梁尺寸=侧拉梁尺寸,
            侧拉梁位置=侧拉梁位置,
            生成侧拉梁=生成侧拉梁,
            背靠背侧拉梁=False
        )
        # 修改元数据
        metadata['id'] = spec['id']
        metadata['name'] = spec['name']
        metadata['category'] = spec['category']
        metadata['prebuilt'] = spec['prebuilt']
    
    return scene, metadata


def main():
    """主函数：生成所有40个货架模型"""
    
    output_dir = "../frontend/public/assets/models"
    
    print("=" * 60)
    print("仓酷家 40个货架模型批量生成")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, spec in enumerate(SHELF_SPECS, 1):
        print(f"\n[{i}/40] ", end="")
        
        try:
            # 生成模型
            scene, metadata = generate_shelf_model(spec)
            
            # 导出GLB
            output_path = f"{output_dir}/{spec['id']}.glb"
            if export_glb(scene, output_path, metadata):
                print(f"✓ 成功 -> {output_path}")
                success_count += 1
            else:
                print(f"✗ 导出失败")
                failed_count += 1
                
        except Exception as e:
            print(f"✗ 错误: {e}")
            failed_count += 1
    
    print("\n" + "=" * 60)
    print(f"生成完成: 成功 {success_count} 个, 失败 {failed_count} 个")
    print("=" * 60)


if __name__ == "__main__":
    main()
