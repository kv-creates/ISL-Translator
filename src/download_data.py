"""
Download REAL ISL datasets into data/raw/ - no synthetic data.
FREE first (no login): GitHub RealSign + Ayeshatasnim (same A-Z fingerspelling type),
then Kaggle public via kagglehub (no kaggle.json), then open sentence-level links.
IEEE DataPort listed last (requires login - optional, free sets already cover A-Z).

Usage:
    python src/download_data.py [--all | --free | --hindi | --csltr | --isl-az]
"""
import argparse
import os
import urllib.request
import zipfile

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
RAW = os.path.abspath(RAW)
os.makedirs(RAW, exist_ok=True)

# FREE, no-login, same-type (ISL fingerspelling A-Z images)
FREE_GITHUB = {
    "free-isl-realsign": {
        "url": "https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset/raw/main/Dataset.zip",
        "desc": "RealSign ISL A-Z (CC0-1.0, 4 signers): Training 26x700 + Testing 26x200 + Validation 26x100 = ~26k",
    },
    "free-isl-ayeshatasnim": {
        "url": "https://github.com/ayeshatasnim-h/Indian-Sign-Language-dataset/raw/main/dataset_ISL.zip",
        "desc": "Ayeshatasnim ISL A-Z (Apache-2.0): 26 classes x ~486 = 12,637 images",
    },
}

DATASETS = {
    "isl-hindi": "krishbhagat/indian-sign-language-hindi",  # 48k, 40 Hindi chars (kagglehub, free, no login)
    "isl-csltr": "drblack00/isl-csltr-indian-sign-language-dataset",  # sentence-level, 700 videos (8GB, Colab)
    "isl-az": "prathumarikeri/indian-sign-language-isl",  # char-level A-Z fallback
}

IEEE_URL = "https://ieee-dataport.org/documents/isl-fingerspelling-image-dataset"
ISH_FINGERSPELLING_SITE = "https://kirandevraj.github.io/ISL-Fingerspelling/"
ISLTRANSLATE = "https://github.com/exploration-lab/isltranslate"  # 31k pairs, open
ISIGN = "https://exploration-lab.github.io/iSign/"  # 118k pairs benchmark, open


def dl_free(name, info):
    dest = os.path.join(RAW, name)
    os.makedirs(dest, exist_ok=True)
    zpath = os.path.join(dest, os.path.basename(info["url"]))
    if os.path.exists(os.path.join(dest, "unzipped")):
        print(f"[free] {name} already unzipped, skipping.")
        return True
    print(f"\n[free download] {name}: {info['desc']}\n  {info['url']}\n  -> {zpath}")
    try:
        urllib.request.urlretrieve(info["url"], zpath)
        print("  unzipping...")
        with zipfile.ZipFile(zpath, "r") as z:
            z.extractall(os.path.join(dest, "unzipped"))
        print(f"  OK -> {dest}/unzipped")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def dl_kaggle(slug: str, dest_sub: str):
    dest = os.path.join(RAW, dest_sub)
    os.makedirs(dest, exist_ok=True)
    print(f"\n[download] {slug} -> {dest}")
    try:
        import kagglehub
        path = kagglehub.dataset_download(slug)
        print(f"[kagglehub] cached at: {path}")
        import shutil
        count = 0
        for root, _, files in os.walk(path):
            count += len(files)
        print(f"[kagglehub] total files in cache: {count}")
        print("  NOTE: cache reused. Set COPY=1 to copy into repo.")
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
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--free", action="store_true", help="free GitHub sets only (default)")
    ap.add_argument("--hindi", action="store_true")
    ap.add_argument("--csltr", action="store_true")
    ap.add_argument("--isl-az", action="store_true")
    args = ap.parse_args()

    if not any([args.all, args.free, args.hindi, args.csltr, args.isl_az]):
        args.free = True

    print("RAW dir:", RAW)
    print("\n=== FREE (no login, same A-Z fingerspelling type) ===")
    for n, i in FREE_GITHUB.items():
        print(f"  {n}: {i['desc']}\n    {i['url']}")
    print(f"\n=== OPEN sentence-level ===\n  ISLTranslate (31k): {ISLTRANSLATE}\n  iSign (118k): {ISIGN}\n  Continuous fingerspelling: {ISH_FINGERSPELLING_SITE}")
    print(f"\n=== IEEE (optional, login required) ===\n  {IEEE_URL}")

    ok = {}
    if args.all or args.free:
        for n, i in FREE_GITHUB.items():
            ok[n] = dl_free(n, i)
    if args.all or args.hindi:
        ok["isl-hindi"] = dl_kaggle(DATASETS["isl-hindi"], "isl-hindi")
    if args.all or args.csltr:
        ok["isl-csltr"] = dl_kaggle(DATASETS["isl-csltr"], "isl-csltr")
    if args.isl_az:
        ok["isl-az"] = dl_kaggle(DATASETS["isl-az"], "isl-az")

    print("\n=== SUMMARY ===")
    for k, v in ok.items():
        print(f"  {k}: {'OK' if v else 'NEEDS MANUAL DOWNLOAD'}")
    print("\nNext: python src/verify_data.py")


if __name__ == "__main__":
    main()
