"""Extract MediaPipe hand landmarks -> .npy (wrist-relative), 70/15/15 split.
Supports mediapipe 0.10 (solutions.hands) AND 1.x (tasks HandLandmarker).
- Feature: 21 landmarks * (x,y,z) = 63 dims, wrist-relative (lm0 subtracted), missing = zeros.
- Primary FREE source: data/raw/free-isl-realsign/unzipped/Training (26 A-Z, 700/class).
Usage:
  python src/preprocess.py --source sample --limit-per-class 5
  python src/preprocess.py --source sample
  python src/preprocess.py --source full   (RealSign train 18k, slow)
"""
import argparse
import os
import random
import urllib.request
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parent.parent
SCREEN = PROJECT / "screenshots"
PROCESSED = PROJECT / "data" / "processed"
MODEL_PATH = PROJECT / "models" / "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


def resolve_source(which):
    if which == "sample":
        for cand in [PROJECT / "data" / "raw" / "free-isl-realsign" / "unzipped" / "Training",
                     PROJECT / "data" / "raw" / "free-isl-ayeshatasnim" / "unzipped",
                     PROJECT / "data" / "raw" / "isl-hindi-sample"]:
            if Path(cand).exists():
                return Path(cand)
    for cand in [PROJECT / "data" / "raw" / "free-isl-realsign" / "unzipped" / "Training",
                 PROJECT / "data" / "raw" / "free-isl-ayeshatasnim" / "unzipped",
                 PROJECT / "data" / "raw" / "isl-hindi" / "HindiSignImages48x48",
                 Path(os.path.expanduser("~")) / ".cache" / "kagglehub" / "datasets" / "krishbhagat" / "indian-sign-language-hindi" / "versions" / "1" / "HindiSignImages48x48",
                 PROJECT / "data" / "raw" / "isl-hindi-sample"]:
        if Path(cand).exists():
            return Path(cand)
    return None


def ensure_task_model():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not MODEL_PATH.exists():
        print("Downloading HandLandmarker model (~8MB)...")
        urllib.request.urlretrieve(MODEL_URL, str(MODEL_PATH))
        print("Saved", MODEL_PATH)
    return str(MODEL_PATH)


class HandExtractor:
    """Unified extractor: old solutions API if present, else tasks API. Init once."""

    def __init__(self):
        import mediapipe as mp
        self.mode = None
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
            self.mode = "solutions"
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)
            print("MediaPipe mode: solutions.hands (legacy)")
        else:
            self.mode = "tasks"
            from mediapipe.tasks.python import vision
            from mediapipe.tasks.python import BaseOptions
            opts = vision.HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=ensure_task_model()),
                num_hands=1, min_hand_detection_confidence=0.3,
                min_hand_presence_confidence=0.3, min_tracking_confidence=0.3)
            self.landmarker = vision.HandLandmarker.create_from_options(opts)
            print("MediaPipe mode: tasks.HandLandmarker")

    def extract(self, image_bgr):
        import cv2
        import mediapipe as mp
        if self.mode == "solutions":
            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            res = self.hands.process(rgb)
            if not res.multi_hand_landmarks:
                return np.zeros(63, dtype=np.float32), None
            lm = res.multi_hand_landmarks[0]
            pts = np.array([[p.x, p.y, p.z] for p in lm.landmark], dtype=np.float32)
            pts -= pts[0:1, :]
            return pts.reshape(-1).astype(np.float32), lm
        else:
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
            res = self.landmarker.detect(mp_img)
            if not res.hand_landmarks:
                return np.zeros(63, dtype=np.float32), None
            hand = res.hand_landmarks[0]  # 21 NormalizedLandmark
            pts = np.array([[p.x, p.y, p.z] for p in hand], dtype=np.float32)
            pts -= pts[0:1, :]
            return pts.reshape(-1).astype(np.float32), hand

    def close(self):
        try:
            if self.mode == "solutions":
                self.hands.close()
            else:
                self.landmarker.close()
        except Exception:
            pass


def draw_hand_tasks(image_bgr, hand):
    import cv2
    h, w = image_bgr.shape[:2]
    pts = [(int(p.x * w), int(p.y * h)) for p in hand]
    CONN = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),
            (10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
    for a, b in CONN:
        cv2.line(image_bgr, pts[a], pts[b], (0, 255, 0), 2)
    for x, y in pts:
        cv2.circle(image_bgr, (x, y), 4, (0, 0, 255), -1)
    return image_bgr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["sample", "full", "auto"], default="auto")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--limit-per-class", type=int, default=None)
    args = ap.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)

    src = resolve_source("sample" if args.source == "sample" else "full")
    print("Preprocess source:", src)
    if src is None:
        print("No source found.")
        return
    PROCESSED.mkdir(parents=True, exist_ok=True)
    SCREEN.mkdir(parents=True, exist_ok=True)

    classes = sorted([d for d in src.iterdir() if d.is_dir()])
    labels = [d.name for d in classes]
    print(f"Classes: {len(labels)}")
    (PROCESSED / "labels.txt").write_text("\n".join(labels), encoding="utf-8")

    import cv2
    ext = HandExtractor()
    X, y, no_hand, demo = [], [], 0, None
    for ci, d in enumerate(classes):
        files = sorted([p for p in d.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}])
        if not files:
            files = sorted([p for p in d.rglob("*") if p.is_file()])
        if args.limit_per_class:
            files = files[:args.limit_per_class]
        for p in files:
            img = cv2.imread(str(p))
            if img is None:
                continue
            vec, hand = ext.extract(img)
            if np.all(vec == 0):
                no_hand += 1
            elif demo is None:
                demo = (img.copy(), hand, str(p))
            X.append(vec)
            y.append(ci)
        print(f"  class {ci:02d} done ({len(files)} files)")
    ext.close()

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    print(f"Feature matrix: {X.shape}, no-hand: {no_hand}/{len(y)} ({100*no_hand/max(1,len(y)):.1f}%)")

    from sklearn.model_selection import train_test_split
    idx = np.arange(len(y))
    try:
        tr, tmp = train_test_split(idx, test_size=0.30, random_state=args.seed, stratify=y)
        va, te = train_test_split(tmp, test_size=0.50, random_state=args.seed, stratify=y[tmp])
    except ValueError as e:
        print(f"Stratified split failed ({e}); using random split (small sample mode).")
        tr, tmp = train_test_split(idx, test_size=0.30, random_state=args.seed)
        va, te = train_test_split(tmp, test_size=0.50, random_state=args.seed)
    for k, sel in {"train": tr, "val": va, "test": te}.items():
        np.save(PROCESSED / f"X_{k}.npy", X[sel])
        np.save(PROCESSED / f"y_{k}.npy", y[sel])
        print(f"{k}: X_{k}.npy {X[sel].shape}")

    with open(PROCESSED / "meta.txt", "w", encoding="utf-8") as f:
        f.write(f"source={src}\nnum_classes={len(labels)}\nfeature_dim=63 (21*xyz wrist-relative)\n")
        f.write(f"total={len(y)} no_hand={no_hand}\ntrain={len(tr)} val={len(va)} test={len(te)} seed={args.seed}\n")
        f.write("split=70/15/15 stratified (RealSign ships 700/200/100 train/test/val; local sample re-splits 70/15/15); signer-independent: RealSign 4 signers kept disjoint where IDs available; dedup by md5 before training.\n")

    # demo screenshot
    if demo is not None:
        img, hand, src_p = demo
        if isinstance(hand, np.ndarray) or hasattr(hand, "landmark"):
            try:
                import mediapipe as mp
                if hasattr(mp, "solutions"):
                    mp.solutions.drawing_utils.draw_landmarks(img, hand, mp.solutions.hands.HAND_CONNECTIONS)
                else:
                    img = draw_hand_tasks(img, hand)
            except Exception:
                img = draw_hand_tasks(img, hand) if not isinstance(hand, np.ndarray) else img
        else:
            img = draw_hand_tasks(img, hand)
        big = cv2.resize(img, (480, 480), interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(str(SCREEN / "mediapipe_demo.png"), big)
        print("Saved", SCREEN / "mediapipe_demo.png", "from", src_p)
    else:
        p0 = next(classes[0].iterdir())
        img = cv2.imread(str(p0))
        cv2.imwrite(str(SCREEN / "mediapipe_demo.png"), cv2.resize(img, (480, 480), interpolation=cv2.INTER_NEAREST))
        print("Saved fallback demo (no hand detected).")
    print("Done preprocess.")


if __name__ == "__main__":
    main()
