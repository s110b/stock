#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量重命名图片（下划线命名版）：
- 把中文/特殊符号转成英文 slug（小写、下划线）
- 自动去掉空格、括号、特殊符号
- 文件名过长自动截断 + 附短哈希避免冲突
- 扩展名保持但统一小写
- 支持 --seq 顺序命名、--dir 指定目录、-n/--dry-run 预览
"""

import argparse
import hashlib
import os
import re
import sys
import unicodedata

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".heic"}

def ascii_slug(s: str) -> str:
    """转换为纯 ASCII 下划线格式"""
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)  # 全部改为下划线
    s = s.strip("_")
    s = re.sub(r"_+", "_", s)  # 折叠多下划线
    return s or "img"

def short_hash(s: str) -> str:
    """生成短哈希"""
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:6]

def iter_images(folder):
    """遍历所有图片文件"""
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if not os.path.isfile(p):
            continue
        root, ext = os.path.splitext(name)
        if ext.lower() in IMG_EXTS:
            yield name, root, ext

def unique_name(dst_path):
    """如果重名则自动加序号"""
    if not os.path.exists(dst_path):
        return dst_path
    base, ext = os.path.splitext(dst_path)
    i = 1
    while True:
        cand = f"{base}_{i}{ext}"
        if not os.path.exists(cand):
            return cand
        i += 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="目标目录（默认当前目录）")
    ap.add_argument("--seq", action="store_true", help="按顺序命名 img_0001.ext")
    ap.add_argument("-n", "--dry-run", action="store_true", help="仅预览，不改名")
    args = ap.parse_args()

    folder = os.path.abspath(args.dir)
    files = sorted(list(iter_images(folder)))

    if not files:
        print("❌ 未找到图片文件（支持扩展名：", ", ".join(sorted(IMG_EXTS)), ")")
        return

    if args.seq:
        width = max(4, len(str(len(files))))
        for idx, (name, _root, ext) in enumerate(files, 1):
            newname = f"img_{idx:0{width}d}{ext.lower()}"
            src = os.path.join(folder, name)
            dst = os.path.join(folder, newname)
            dst = unique_name(dst)
            if args.dry_run:
                print(f"[DRY] {name} → {os.path.basename(dst)}")
            else:
                os.rename(src, dst)
                print(f"{name} → {os.path.basename(dst)}")
        return

    for name, root, ext in files:
        slug = ascii_slug(root)
        if len(slug) > 30:
            slug = slug[:30]
        slug = f"{slug}_{short_hash(name)}"
        newname = f"{slug}{ext.lower()}"

        src = os.path.join(folder, name)
        dst = os.path.join(folder, newname)
        dst = unique_name(dst)

        if args.dry_run:
            print(f"[DRY] {name} → {os.path.basename(dst)}")
        else:
            os.rename(src, dst)
            print(f"{name} → {os.path.basename(dst)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

