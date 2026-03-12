#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物流仓库规划图文件搜索工具
扫描指定盘符，找出与仓库规划、物流布局相关的文件
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse

# 关键词配置 - 与物流仓库规划相关的词汇
KEYWORDS = {
    '规划相关': [
        '仓库规划', '仓储规划', '物流规划', '库区规划', '库位规划',
        '仓库设计', '仓储设计', '物流设计', '布局设计', '动线设计',
        'warehouse plan', 'warehouse design', 'layout plan', 'layout design',
        '仓储布局', '仓库布局', '物流布局', '库区布局', '库位布局',
        '仓库方案', '仓储方案', '物流方案', '规划方案', '设计方案',
    ],
    '图纸相关': [
        '仓库图纸', '仓储图纸', '规划图纸', '布局图纸', '平面图',
        '立体图', '鸟瞰图', '流程图', '动线图', '货架图',
        'warehouse drawing', 'layout drawing', 'floor plan', 'blueprint',
        'CAD', 'DWG', '平面图', '布置图', '示意图', '规划图',
    ],
    '类型相关': [
        '立体仓库', '自动化仓库', '智能仓库', 'ASRS', '分拣中心',
        '配送中心', '物流中心', '仓储中心', '冷库', '常温库',
        'automated warehouse', 'distribution center', 'fulfillment center',
        '智能仓储', '自动化仓储', '密集存储', '货架系统', '输送系统',
    ],
    '案例相关': [
        '京东', '阿里', '菜鸟', '顺丰', '苏宁', '国美', '唯品会',
        '案例', '项目', '实施', '交付', '运营', '总结',
        'JD', ' Alibaba', ' Cainiao', ' SF', ' case study', ' project',
    ]
}

# 关注的文件扩展名
TARGET_EXTENSIONS = {
    # 图纸文件
    '.dwg', '.dxf', '.dwf',  # AutoCAD
    '.pdf',  # PDF图纸
    '.vsd', '.vsdx',  # Visio
    '.ai', '.eps',  # Illustrator
    '.skp',  # SketchUp
    
    # 图片文件
    '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp',
    
    # 文档文件
    '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
    '.txt', '.md', '.rtf',
    
    # 其他可能包含图纸的文件
    '.zip', '.rar', '.7z',  # 压缩包可能包含图纸
}

# 排除的目录（跳过系统目录和缓存）
EXCLUDE_DIRS = {
    '$RECYCLE.BIN', 'System Volume Information', 'Windows', 
    'Program Files', 'Program Files (x86)', 'ProgramData',
    'AppData', 'Temp', 'tmp', 'cache', 'node_modules',
    '.git', '.svn', '.hg', '__pycache__', '.idea', '.vscode',
    'Tencent', 'WeChat Files', 'QQ', '360', 'Baidu',
}

class WarehouseFileFinder:
    def __init__(self, drives):
        self.drives = drives if isinstance(drives, list) else [drives]
        self.results = defaultdict(list)
        self.stats = {
            'scanned_dirs': 0,
            'scanned_files': 0,
            'matched_files': 0,
            'errors': []
        }
    
    def contains_keyword(self, filepath: Path) -> tuple:
        """检查文件名和路径是否包含关键词"""
        full_path = str(filepath).lower()
        filename = filepath.name.lower()
        stem = filepath.stem.lower()
        
        matched_keywords = []
        
        for category, keywords in KEYWORDS.items():
            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in filename or kw_lower in stem or kw_lower in full_path:
                    matched_keywords.append((category, kw))
        
        return len(matched_keywords) > 0, matched_keywords
    
    def is_target_file(self, filepath: Path) -> bool:
        """判断是否是目标文件类型"""
        ext = filepath.suffix.lower()
        return ext in TARGET_EXTENSIONS
    
    def should_skip_dir(self, dirname: str) -> bool:
        """判断是否跳过该目录"""
        return dirname in EXCLUDE_DIRS or dirname.startswith('.')
    
    def scan_drive(self, drive):
        """扫描单个盘符"""
        drive_path = Path(drive)
        if not drive_path.exists():
            print(f"❌ 盘符不存在: {drive}")
            return
        
        print(f"\n🔍 正在扫描: {drive}")
        print(f"   关键词类别: {len(KEYWORDS)} 类, 共 {sum(len(v) for v in KEYWORDS.values())} 个关键词")
        print(f"   目标文件类型: {len(TARGET_EXTENSIONS)} 种")
        
        try:
            for root, dirs, files in os.walk(drive_path):
                # 过滤目录
                dirs[:] = [d for d in dirs if not self.should_skip_dir(d)]
                
                self.stats['scanned_dirs'] += 1
                
                # 显示进度
                if self.stats['scanned_dirs'] % 1000 == 0:
                    print(f"   已扫描 {self.stats['scanned_dirs']} 个目录, 找到 {self.stats['matched_files']} 个匹配文件...", end='\r')
                
                for filename in files:
                    filepath = Path(root) / filename
                    self.stats['scanned_files'] += 1
                    
                    try:
                        # 检查是否是目标文件类型
                        if not self.is_target_file(filepath):
                            continue
                        
                        # 检查是否包含关键词
                        is_match, keywords = self.contains_keyword(filepath)
                        
                        if is_match:
                            # 获取文件信息
                            try:
                                stat = filepath.stat()
                                file_info = {
                                    'path': filepath,
                                    'size': stat.st_size,
                                    'modified': datetime.fromtimestamp(stat.st_mtime),
                                    'keywords': keywords,
                                    'extension': filepath.suffix.lower()
                                }
                                
                                # 按类别分组
                                for cat, kw in keywords:
                                    self.results[cat].append(file_info)
                                
                                self.stats['matched_files'] += 1
                            except Exception:
                                pass
                    
                    except Exception as e:
                        pass  # 跳过无法访问的文件
        
        except Exception as e:
            self.stats['errors'].append(f"{drive}: {str(e)}")
    
    def run(self):
        """执行扫描"""
        print(f"{'='*60}")
        print("📦 物流仓库规划图文件搜索工具")
        print(f"{'='*60}")
        print(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标盘符: {', '.join(self.drives)}")
        
        for drive in self.drives:
            self.scan_drive(drive)
        
        print(f"\n{'='*60}")
        print("📊 扫描完成")
        print(f"{'='*60}")
        print(f"扫描目录数: {self.stats['scanned_dirs']}")
        print(f"扫描文件数: {self.stats['scanned_files']}")
        print(f"匹配文件数: {self.stats['matched_files']}")
        
        if self.stats['errors']:
            print(f"\n⚠️ 错误: {len(self.stats['errors'])} 个")
    
    def generate_report(self, output_file: str = None):
        """生成报告"""
        if output_file is None:
            output_file = f"仓库规划文件清单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        lines = []
        lines.append("# 物流仓库规划图文件清单")
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"搜索盘符: {', '.join(self.drives)}")
        lines.append(f"\n## 统计摘要")
        lines.append(f"- 扫描目录: {self.stats['scanned_dirs']:,} 个")
        lines.append(f"- 扫描文件: {self.stats['scanned_files']:,} 个")
        lines.append(f"- 匹配文件: {self.stats['matched_files']:,} 个")
        
        # 按类别统计
        lines.append(f"\n## 按类别统计")
        for category in ['规划相关', '图纸相关', '类型相关', '案例相关']:
            files = self.results.get(category, [])
            unique_files = {f['path']: f for f in files}  # 去重
            lines.append(f"- {category}: {len(unique_files)} 个文件")
        
        # 详细清单
        lines.append(f"\n---\n")
        lines.append(f"## 详细文件清单\n")
        
        # 去重并排序
        all_files = {}
        for category, files in self.results.items():
            for f in files:
                path_str = str(f['path'])
                if path_str not in all_files:
                    all_files[path_str] = f
                    all_files[path_str]['categories'] = set()
                all_files[path_str]['categories'].add(category)
        
        # 按修改时间倒序排列
        sorted_files = sorted(all_files.values(), key=lambda x: x['modified'], reverse=True)
        
        for i, f in enumerate(sorted_files, 1):
            size_mb = f['size'] / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{f['size']:,} bytes"
            
            lines.append(f"### {i}. {f['path'].name}")
            lines.append(f"- **完整路径**: `{f['path']}`")
            lines.append(f"- **文件类型**: {f['extension']}")
            lines.append(f"- **文件大小**: {size_str}")
            lines.append(f"- **修改时间**: {f['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"- **匹配类别**: {', '.join(f['categories'])}")
            
            # 列出匹配的关键词
            kw_list = [kw for cat, kw in f['keywords']]
            lines.append(f"- **匹配关键词**: {', '.join(set(kw_list))}")
            lines.append("")
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"\n✅ 报告已保存: {output_file}")
        print(f"   共 {len(sorted_files)} 个匹配文件")
        
        return output_file
    
    def print_summary(self):
        """打印简要结果"""
        print(f"\n{'='*60}")
        print("📋 搜索结果摘要")
        print(f"{'='*60}")
        
        # 去重
        all_files = {}
        for category, files in self.results.items():
            for f in files:
                path_str = str(f['path'])
                if path_str not in all_files:
                    all_files[path_str] = f
                    all_files[path_str]['categories'] = set()
                all_files[path_str]['categories'].add(category)
        
        if not all_files:
            print("\n😔 没有找到匹配的文件")
            return
        
        sorted_files = sorted(all_files.values(), key=lambda x: x['modified'], reverse=True)
        
        print(f"\n找到 {len(sorted_files)} 个相关文件:\n")
        
        for i, f in enumerate(sorted_files[:20], 1):  # 只显示前20个
            size_mb = f['size'] / (1024 * 1024)
            size_str = f"{size_mb:.1f}MB" if size_mb >= 1 else f"{f['size']//1024}KB"
            cats = ', '.join(f['categories'])
            print(f"  {i}. [{f['extension']}] {f['path'].name}")
            print(f"     📁 {f['path'].parent}")
            print(f"     🏷️  {cats} | {size_str} | {f['modified'].strftime('%Y-%m-%d')}")
            print()
        
        if len(sorted_files) > 20:
            print(f"   ... 还有 {len(sorted_files) - 20} 个文件，详见完整报告")

def main():
    parser = argparse.ArgumentParser(description='物流仓库规划图文件搜索工具')
    parser.add_argument('--drives', nargs='+', default=['E:\\', 'F:\\'],
                       help='要扫描的盘符，默认 E:\ F:')
    parser.add_argument('--output', default=None,
                       help='输出报告文件名')
    
    args = parser.parse_args()
    
    print("物流仓库规划图文件搜索工具")
    print("=" * 60)
    print("搜索关键词包括:")
    for cat, kws in KEYWORDS.items():
        print(f"  • {cat}: {', '.join(kws[:5])}...")
    print()
    
    finder = WarehouseFileFinder(args.drives)
    finder.run()
    finder.print_summary()
    
    if finder.stats['matched_files'] > 0:
        report_file = finder.generate_report(args.output)
        print(f"\n📄 完整报告: {report_file}")
    else:
        print("\n💡 建议:")
        print("   1. 检查文件是否使用了不同的命名方式")
        print("   2. 尝试手动浏览 E:\ 和 F:\ 的主要文件夹")
        print("   3. 确认文件扩展名是否在支持列表中")

if __name__ == '__main__':
    main()
