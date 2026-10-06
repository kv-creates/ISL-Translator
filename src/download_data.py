"""
Download REAL ISL datasets into data/raw/ — no synthetic data.
- Uses kagglehub for public Kaggle datasets (no kaggle.json needed).
- IEEE DataPort ISL Fingerspelling requires manual login → instructions printed.
- ISH-News continuous fingerspelling is openly hosted → direct download if available.

Usage:
    python src/download_data.py [--all | --hindi | --csltr | --isl-az]
"""
import argparse
import os
import sys
import zipfile
import urllib.request

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
RAW = os.path.abspath(RAW)
os.makedirs(RAW, exist_ok=True)

DATASETS = {
    "isl-hindi": "krishbhagat/indian-sign-language-hindi",  # alias of krish09bha/isl-hindi-character-dataset (48k, 40 Hindi chars)
    "isl-csltr": "drblack00/isl-csltr-indian-sign-language-dataset",  # sentence-level ISL, 700 videos, 100 sentences
    "isl-az": "prathumarikeri/indian-sign-language-isl",  # char-level ISL A-Z fallback
    "isl-az-mediapipe": "prekshapalva/indian-sign-language",  # 26 dirs ~2000/class, 3.85GB (large!)
}

IEEE_URL = "https://ieee-dataport.org/documents/isl-fingerspelling-image-dataset"
ISH_FINGERSPELLING_SITE = "https://kirandevraj.github.io/ISL-Fingerspelling/"


def dl_kaggle(slug: str, dest_sub: str):
    dest = os.path.join(RAW, dest_sub)
    os.makedirs(dest, exist_ok=True)
    print(f"\n[download] {slug} -> {dest}")
    try:
        import kagglehub
        path = kagglehub.dataset_download(slug)
        print(f"[kagglehub] cached at: {path}")
        # copy/list into dest; kagglehub returns cache dir, we symlink info
        import shutil
        # list files
        count = 0
        for root, _, files in os.walk(path):
            for f in files[:5]:
                print("  sample:", os.path.join(root, f))
            count += len(files)
        print(f"[kagglehub] total files in cache: {count}")
        print(f"  NOTE: kagglehub cache is reused. Copy manually if needed, or point verify script at cache.")
        print(f"  To copy into repo (may be GBs), set COPY=1 env. Skipping auto-copy to save disk.")
        if os.environ.get("COPY") == "1":
            for root, _, files in os.walk(path):
                for f in files:
                    src = os.path.join(root, f)
                    rel = os.path.relpath(src, path)
                    dst = os.path.join(dest, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
            print(f"[copy] done -> {dest}")
        return True
    except Exception as e:
        print(f"[ERROR] kagglehub failed for {slug}: {e}")
        print(f"  Manual: https://www.kaggle.com/datasets/{slug} -> unzip into {dest}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="download all kaggle sets")
    ap.add_argument("--hindi", action="store_true")
    ap.add_argument("--csltr", action="store_true")
    ap.add_argument("--isl-az", action="store_true")
    args = ap.parse_args()

    if not any([args.all, args.hindi, args.csltr, args.isl_az]):
        args.all = True  # default

    print("RAW dir:", RAW)
    print("\n=== IEEE DataPort (MANUAL, requires login) ===")
    print(f"1. ISL Fingerspelling Image Dataset (35 classes, ~14k images, 3 signers):\n   {IEEE_URL}")
    print("   Steps: login/subscribe -> Download -> unzip into data/raw/isl-fingerspelling/")
    print("\n=== ISH-News Continuous Fingerspelling (OPEN) ===")
    print(f"   {ISH_FINGERSPELLING_SITE} -> 1308 segs, 499 videos. Follow site instructions.")

    ok = {}
    if args.all or args.hindi:
        ok["isl-hindi"] = dl_kaggle(DATASETS["isl-hindi"], "isl-hindi")
    if args.all or args.csltr:
        ok["isl-csltr"] = dl_kaggle(DATASETS["isl-csltr"], "isl-csltr")
    if args.isl_az:
        ok["isl-az"] = dl_kaggle(DATASETS["isl-az"], "isl-az")

    print("\n=== SUMMARY ===")
    for k, v in ok.items():
        print(f"  {k}: {'OK (cache)' if v else 'NEEDS MANUAL DOWNLOAD'}")
    print("\nNext: python src/verify_data.py")


if __name__ == "__main__":
    main()
