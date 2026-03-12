#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Organizer - 智能文件整理工具
"""

import os
import sys
import hashlib
import shutil
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import argparse

# 文件类型分类规则
FILE_CATEGORIES = {
    '文档': ['.pdf', '.doc', '.docx', '.txt', '.md', '.xls', '.xlsx', '.ppt', '.pptx', 
             '.csv', '.rtf', '.odt', '.ods', '.odp'],
    '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', 
             '.tif', '.raw', '.heic', '.heif'],
    '视频': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', 
             '.mpeg', '.3gp', '.ts'],
    '音频': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.wma'],
    '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz', '.tbz', '.lz'],
    '代码': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.go', '.rs', '.ts', 
             '.json', '.xml', '.yaml', '.yml', '.php', '.rb', '.swift', '.kt', '.sql'],
    '可执行': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.appimage', '.bat', '.sh'],
}

# 获取文件分类
def get_file_category(extension: str) -> str:
    ext_lower = extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext_lower in extensions:
            return category
    return '其他'

# 计算文件 MD5
def get_file_hash(filepath: Path) -> str:
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

# 获取文件信息
def get_file_info(filepath: Path) -> dict:
    stat = filepath.stat()
    return {
        'path': filepath,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'extension': filepath.suffix,
        'category': get_file_category(filepath.suffix)
    }

# 扫描文件夹
def scan_directory(path: Path, recursive: bool = True) -> List[dict]:
    files = []
    try:
        if recursive:
            for filepath in path.rglob('*'):
                if filepath.is_file() and not filepath.name.startswith('.'):
                    files.append(get_file_info(filepath))
        else:
            for filepath in path.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    files.append(get_file_info(filepath))
    except Exception as e:
        print(f"扫描出错: {e}")
    return files

# 分析文件夹结构
def analyze_directory(path: Path) -> dict:
    print(f"🔍 正在分析: {path}")
    files = scan_directory(path)
    
    if not files:
        return {'total_files': 0, 'message': '文件夹为空或无法访问'}
    
    # 统计信息
    total_size = sum(f['size'] for f in files)
    categories = defaultdict(list)
    extensions = defaultdict(int)
    
    for f in files:
        categories[f['category']].append(f)
        extensions[f['extension']] += 1
    
    # 混乱度评分 (0-100)
    # 基于: 文件分布均匀度、根目录文件数量、文件类型数量
    root_files = len([f for f in files if f['path'].parent == path])
    category_count = len(categories)
    
    chaos_score = min(100, int(
        (root_files / max(len(files), 1)) * 30 +  # 根目录文件占比
        (category_count * 10) +  # 类型多样性
        (len(extensions) / max(len(files), 1)) * 20  # 扩展名多样性
    ))
    
    result = {
        'total_files': len(files),
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024*1024), 2),
        'categories': {k: len(v) for k, v in categories.items()},
        'top_extensions': sorted(extensions.items(), key=lambda x: -x[1])[:10],
        'chaos_score': chaos_score,
        'root_file_count': root_files
    }
    
    return result

# 显示分析结果
def show_analysis(result: dict, path: Path):
    print(f"\n{'='*50}")
    print(f"📊 文件夹分析报告: {path}")
    print(f"{'='*50}")
    
    if result['total_files'] == 0:
        print("文件夹为空")
        return
    
    print(f"\n📁 文件总数: {result['total_files']}")
    print(f"💾 总大小: {result['total_size_mb']} MB")
    print(f"📂 根目录文件数: {result['root_file_count']}")
    print(f"⚠️  混乱度评分: {result['chaos_score']}/100")
    
    if result['chaos_score'] < 30:
        print("   └─ ✅ 整理程度良好")
    elif result['chaos_score'] < 60:
        print("   └─ ⚠️  建议整理")
    else:
        print("   └─ 🔴 急需整理")
    
    print(f"\n📑 文件分类统计:")
    for cat, count in sorted(result['categories'].items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} 个文件")
    
    print(f"\n📎 常见扩展名:")
    for ext, count in result['top_extensions'][:5]:
        print(f"   {ext or '(无扩展名)'}: {count} 个文件")
    
    print(f"\n💡 建议:")
    if result['root_file_count'] > 20:
        print("   • 根目录文件过多，建议按类型或日期整理")
    if len(result['categories']) > 5:
        print("   • 文件类型较杂，建议分类存放")
    if result['chaos_score'] > 50:
        print("   • 建议使用 `auto` 模式进行自动整理")

# 按类型整理
def organize_by_type(path: Path, execute: bool = False) -> dict:
    print(f"{'='*50}")
    print(f"📂 按类型整理: {path}")
    print(f"{'='*50}")
    
    files = scan_directory(path, recursive=False)
    
    if not files:
        print("没有需要整理的文件")
        return {'moved': 0}
    
    # 分组
    groups = defaultdict(list)
    for f in files:
        groups[f['category']].append(f)
    
    print(f"\n📋 整理计划:")
    total_move = 0
    for category, file_list in groups.items():
        if len(file_list) > 0 and category != '其他':
            print(f"   📁 {category}/: {len(file_list)} 个文件")
            total_move += len(file_list)
    
    if total_move == 0:
        print("没有需要移动的文件")
        return {'moved': 0}
    
    print(f"\n   总计: {total_move} 个文件将被移动")
    
    if not execute:
        print("\n⚠️  这是预览模式，加 --execute 才真正执行")
        return {'moved': 0, 'preview': total_move}
    
    # 执行移动
    moved = 0
    for category, file_list in groups.items():
        if category == '其他' or len(file_list) == 0:
            continue
            
        target_dir = path / category
        target_dir.mkdir(exist_ok=True)
        
        for f in file_list:
            try:
                target = target_dir / f['path'].name
                # 处理重名
                counter = 1
                while target.exists():
                    stem = f['path'].stem
                    suffix = f['path'].suffix
                    target = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                shutil.move(str(f['path']), str(target))
                moved += 1
                print(f"   ✓ {f['path'].name} → {category}/")
            except Exception as e:
                print(f"   ✗ {f['path'].name}: {e}")
    
    print(f"\n✅ 成功移动 {moved} 个文件")
    return {'moved': moved}

# 按日期整理
def organize_by_date(path: Path, execute: bool = False) -> dict:
    print(f"{'='*50}")
    print(f"📅 按日期整理: {path}")
    print(f"{'='*50}")
    
    files = scan_directory(path, recursive=False)
    
    if not files:
        print("没有需要整理的文件")
        return {'moved': 0}
    
    # 按年月分组
    groups = defaultdict(list)
    for f in files:
        key = f['modified'].strftime('%Y-%m')
        groups[key].append(f)
    
    print(f"\n📋 整理计划:")
    for date_key, file_list in sorted(groups.items()):
        print(f"   📁 {date_key}/: {len(file_list)} 个文件")
    
    if not execute:
        print("\n⚠️  这是预览模式，加 --execute 才真正执行")
        return {'moved': 0, 'preview': len(files)}
    
    # 执行移动
    moved = 0
    for date_key, file_list in groups.items():
        target_dir = path / date_key
        target_dir.mkdir(exist_ok=True)
        
        for f in file_list:
            try:
                target = target_dir / f['path'].name
                counter = 1
                while target.exists():
                    stem = f['path'].stem
                    suffix = f['path'].suffix
                    target = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                shutil.move(str(f['path']), str(target))
                moved += 1
            except Exception as e:
                print(f"   ✗ {f['path'].name}: {e}")
    
    print(f"\n✅ 成功移动 {moved} 个文件")
    return {'moved': moved}

# 查找重复文件
def find_duplicates(path: Path, delete: bool = False) -> dict:
    print(f"{'='*50}")
    print(f"🔍 查找重复文件: {path}")
    print(f"{'='*50}")
    
    files = scan_directory(path)
    
    if not files:
        print("没有找到文件")
        return {'duplicates': 0}
    
    print(f"正在计算 {len(files)} 个文件的哈希值...")
    
    # 按大小分组（优化：先比较大小）
    size_groups = defaultdict(list)
    for f in files:
        size_groups[f['size']].append(f)
    
    # 只计算大小相同的文件的 MD5
    hash_groups = defaultdict(list)
    for size, file_list in size_groups.items():
        if len(file_list) > 1:  # 只有大小相同才可能是重复
            for f in file_list:
                file_hash = get_file_hash(f['path'])
                if file_hash:
                    hash_groups[file_hash].append(f)
    
    # 筛选出真正的重复
    duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}
    
    if not duplicates:
        print("\n✅ 没有发现重复文件")
        return {'duplicates': 0}
    
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_waste = sum(
        files[0]['size'] * (len(files) - 1) 
        for files in duplicates.values()
    )
    
    print(f"\n⚠️  发现 {len(duplicates)} 组重复文件")
    print(f"   涉及 {total_duplicates} 个重复项")
    print(f"   浪费空间: {round(total_waste / (1024*1024), 2)} MB")
    
    print(f"\n📋 重复文件列表:")
    for i, (file_hash, file_list) in enumerate(duplicates.items(), 1):
        print(f"\n   组 {i} ({file_list[0]['size']} bytes):")
        for j, f in enumerate(file_list):
            marker = " [保留]" if j == 0 else " [可删]"
            print(f"      {j+1}. {f['path'].relative_to(path)}{marker}")
    
    if delete:
        print(f"\n⚠️  将删除重复文件（保留每组第一个）")
        confirm = input("   确认删除? (yes/no): ")
        
        if confirm.lower() == 'yes':
            deleted = 0
            freed = 0
            for file_list in duplicates.values():
                for f in file_list[1:]:  # 跳过第一个
                    try:
                        freed += f['size']
                        f['path'].unlink()
                        deleted += 1
                        print(f"   ✓ 已删除: {f['path'].name}")
                    except Exception as e:
                        print(f"   ✗ 删除失败: {e}")
            
            print(f"\n✅ 已删除 {deleted} 个文件，释放 {round(freed/(1024*1024), 2)} MB")
            return {'deleted': deleted, 'freed_mb': round(freed/(1024*1024), 2)}
    
    return {'duplicates': total_duplicates, 'waste_mb': round(total_waste/(1024*1024), 2)}

# 自动整理
def auto_organize(path: Path, execute: bool = False) -> dict:
    print(f"{'='*50}")
    print(f"🤖 自动整理模式: {path}")
    print(f"{'='*50}")
    
    # 先分析
    result = analyze_directory(path)
    show_analysis(result, path)
    
    if result['total_files'] == 0:
        return
    
    print(f"\n{'='*50}")
    print("🎯 开始自动整理...")
    print(f"{'='*50}")
    
    # 策略选择
    if result['chaos_score'] < 30:
        print("\n✅ 文件夹已经很整洁，无需整理")
        return
    
    # 1. 先查重复
    dup_result = find_duplicates(path, delete=False)
    
    # 2. 按类型整理
    if result['root_file_count'] > 10:
        print("\n📂 执行按类型整理...")
        organize_by_type(path, execute=execute)
    
    print(f"\n{'='*50}")
    print("🎉 自动整理完成")
    print(f"{'='*50}")
    
    if not execute:
        print("\n💡 以上都是预览，加 --execute 才真正执行")

def main():
    parser = argparse.ArgumentParser(description='文件整理助手')
    parser.add_argument('command', choices=[
        'analyze', 'organize-by-type', 'organize-by-date', 
        'find-duplicates', 'auto'
    ], help='命令')
    parser.add_argument('path', help='目标文件夹路径')
    parser.add_argument('--execute', action='store_true', 
                       help='真正执行操作（默认仅预览）')
    parser.add_argument('--delete', action='store_true',
                       help='删除重复文件（用于 find-duplicates）')
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"❌ 路径不存在: {path}")
        sys.exit(1)
    
    if not path.is_dir():
        print(f"❌ 不是文件夹: {path}")
        sys.exit(1)
    
    # 执行命令
    if args.command == 'analyze':
        result = analyze_directory(path)
        show_analysis(result, path)
    
    elif args.command == 'organize-by-type':
        organize_by_type(path, execute=args.execute)
    
    elif args.command == 'organize-by-date':
        organize_by_date(path, execute=args.execute)
    
    elif args.command == 'find-duplicates':
        find_duplicates(path, delete=args.delete)
    
    elif args.command == 'auto':
        auto_organize(path, execute=args.execute)

if __name__ == '__main__':
    main()
