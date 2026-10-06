"""Verify data/raw structure + class counts. Works with manually unzipped or kagglehub cache."""
import os
from pathlib import Path
from collections import Counter

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VID_EXTS = {".mp4", ".avi", ".mov", ".mkv"}


def scan_dataset(name: str, folder: Path):
    if not folder.exists():
        print(f"[{name}] MISSING: {folder} (manual download needed)")
        return
    # class = immediate subdir; count images/videos recursively per class
    subdirs = [d for d in folder.iterdir() if d.is_dir()]
    if not subdirs:
        # flat or kagglehub cache layout — count all files
        files = [p for p in folder.rglob("*") if p.is_file()]
        imgs = sum(1 for p in files if p.suffix.lower() in IMG_EXTS)
        vids = sum(1 for p in files if p.suffix.lower() in VID_EXTS)
        print(f"[{name}] flat layout: {len(files)} files ({imgs} imgs, {vids} vids) in {folder}")
        for p in list(files)[:5]:
            print(f"   e.g. {p.relative_to(folder)}")
        return
    total = 0
    dist = {}
    for d in sorted(subdirs):
        files = [p for p in d.rglob("*") if p.is_file() and p.suffix.lower() in IMG_EXTS | VID_EXTS]
        # if no media, count all files
        if not files:
            files = [p for p in d.rglob("*") if p.is_file()]
        dist[d.name] = len(files)
        total += len(files)
    print(f"[{name}] {len(dist)} classes, {total} files in {folder}")
    for k in sorted(dist)[:10]:
        print(f"   {k}: {dist[k]}")
    if len(dist) > 20:
        print(f"   ... ({len(dist)-20} more classes, showing first 10 + last 10)")
        for k in sorted(dist)[-10:]:
            print(f"   {k}: {dist[k]}")
    elif len(dist) > 10:
        for k in sorted(dist)[10:]:
            print(f"   {k}: {dist[k]}")


def main():
    print("RAW:", RAW)
    if not RAW.exists():
        print("No data/raw found.")
        return
    print("Contents:", [p.name for p in RAW.iterdir()])
    for sub in sorted(RAW.iterdir()):
        if sub.is_dir():
            scan_dataset(sub.name, sub)
            print()
    # also check kagglehub cache
    try:
        import kagglehub
        from pathlib import Path as P
        cache = P(os.path.expanduser("~")) / ".cache" / "kagglehub"
        if cache.exists():
            print("kagglehub cache:", cache)
            for ds in cache.rglob("*.jpg"):
                pass
    except Exception:
        pass
    print("Done. If all show MISSING, manually unzip zips into data/raw/<name>/.")


if __name__ == "__main__":
    main()
