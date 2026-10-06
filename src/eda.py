"""EDA for real ISL datasets. Saves plots to screenshots/.
- Class distribution bar chart
- 5 random samples per class (grid, first 8 classes to keep figure readable + full in separate)
- Corrupted / missing / duplicate checks
Usage: python src/eda.py [--base data/raw/isl-hindi-sample | kagglehub cache] [--max-per-class 200]
"""
import argparse
import hashlib
import os
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
SCREEN = PROJECT / "screenshots"
SCREEN.mkdir(exist_ok=True)
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_base(explicit=None):
    if explicit and Path(explicit).exists():
        return Path(explicit)
    # prefer local sample, else kagglehub cache
    for cand in [PROJECT/"data"/"raw"/"isl-hindi-sample",
                 PROJECT/"data"/"raw"/"isl-hindi"/"HindiSignImages48x48"]:
        if cand.exists():
            return cand
    # kagglehub cache
    cache = Path(os.path.expanduser("~"))/".cache"/"kagglehub"/"datasets"/"krishbhagat"/"indian-sign-language-hindi"/"versions"/"1"/"HindiSignImages48x48"
    if cache.exists():
        return cache
    return None


def file_hash(p: Path, n=8192):
    h = hashlib.md5()
    with open(p, "rb") as f:
        while True:
            b = f.read(65536)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    base = find_base(args.base)
    print("EDA base:", base)
    if base is None or not base.exists():
        print("No dataset found. Run download step first.")
        return

    classes = sorted([d for d in base.iterdir() if d.is_dir()])
    print(f"Classes: {len(classes)}")
    counts, corrupt, dups, sizes = {}, [], {}, []
    seen_hash = {}
    for d in classes:
        files = [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS]
        if not files:
            files = [p for p in d.rglob("*") if p.is_file()]
        counts[d.name] = len(files)
        for p in files:
            try:
                with Image.open(p) as im:
                    im.verify()
                with Image.open(p) as im:
                    sizes.append(im.size)
            except Exception:
                corrupt.append(str(p))
            h = file_hash(p)
            if h in seen_hash:
                dups[h] = dups.get(h, [seen_hash[h]]) + [str(p)]
            else:
                seen_hash[h] = str(p)

    total = sum(counts.values())
    print(f"Total files: {total}")
    print("Per-class (first 10):")
    for k in list(counts)[:10]:
        print(f"  {k}: {counts[k]}")
    print(f"Corrupted: {len(corrupt)}")
    for c in corrupt[:5]:
        print("  CORRUPT:", c)
    ndup_groups = len(dups)
    ndup_files = sum(len(v)-1 for v in dups.values())
    print(f"Duplicate groups: {ndup_groups}, extra files: {ndup_files}")
    if sizes:
        from collections import Counter
        print("Top image sizes:", Counter(sizes).most_common(5))

    # 1. class distribution bar chart
    plt.figure(figsize=(14, 5))
    names = [f"C{i}" for i in range(len(classes))]
    plt.bar(names, [counts[c.name] for c in classes])
    plt.title("ISL-Hindi: images per class (40 classes, balanced 1200/class full; sample=5/class)")
    plt.xlabel("Class index (see EDA_FINDINGS.md for Devanagari mapping)")
    plt.ylabel("Count")
    plt.tight_layout()
    out1 = SCREEN / "eda_class_distribution.png"
    plt.savefig(out1, dpi=150)
    plt.close()
    print("Saved", out1)

    # 2. sample grid: 5 random images for first 8 classes (8x5)
    show = classes[:8]
    fig, axes = plt.subplots(len(show), 5, figsize=(10, 2*len(show)))
    for i, d in enumerate(show):
        files = [p for p in d.iterdir() if p.suffix.lower() in IMG_EXTS]
        samp = random.sample(files, min(5, len(files)))
        for j in range(5):
            ax = axes[i][j] if len(show) > 1 else axes[j]
            ax.axis("off")
            if j < len(samp):
                try:
                    ax.imshow(plt.imread(samp[j]))
                    if j == 0:
                        ax.set_title(f"class {i}", fontsize=9, loc="left")
                except Exception:
                    ax.set_title("unreadable")
    plt.suptitle("Random samples (5 per class, first 8 classes)")
    plt.tight_layout()
    out2 = SCREEN / "eda_samples.png"
    plt.savefig(out2, dpi=150)
    plt.close()
    print("Saved", out2)

    # 3. summary txt
    with open(SCREEN / "eda_summary.txt", "w", encoding="utf-8") as f:
        f.write(f"classes={len(classes)}\ntotal={total}\ncorrupt={len(corrupt)}\ndup_groups={ndup_groups}\ndup_extra={ndup_files}\n")
    print("Done EDA.")


if __name__ == "__main__":
    main()
