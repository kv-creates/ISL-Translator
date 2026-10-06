# EDA Findings & Preprocessing Summary (Phase 2) — FREE datasets (no login)

Primary (same A-Z fingerspelling type, verified 2026-10-06):
- **RealSign** `RealSign62/RealSign-Indian-Sign-Language-Dataset` (CC0-1.0, 4 signers):
  Training 18,198 (26 classes A-Z, A=700) + Testing 5,200 (26x200) + Validation 2,579 (26x~100).
  `data/raw/free-isl-realsign/unzipped/{Training,Testing,Validation}/`
- **Ayeshatasnim** `ayeshatasnim-h/Indian-Sign-Language-dataset` (Apache-2.0):
  26 classes (a-z), 12,637 images (~486/class). `data/raw/free-isl-ayeshatasnim/unzipped/a..z/`
- Secondary: ISL-Hindi Kaggle 40x1200=48k (heavy dups); sentence-level ISLTranslate (31k) / iSign (118k) for Colab.

## EDA (src/eda.py, default base = RealSign Training)
- **Classes:** 26 (A-Z), ~700 each in Training. Balanced.
- **Plot:** `screenshots/eda_class_distribution.png` — 26 bars ~700.
- **Samples:** `screenshots/eda_samples.png` — 5 random x first 8 classes.
- **Corrupted:** 0. **Sizes:** varied ~200-300px (real captures, not uniform).
- **Duplicates:** 141 groups / 144 extra (~0.8%) — far cleaner than Hindi set (97% copies). Still dedups by md5.
- IEEE set (35 classes, login-walled) replaced by these free same-type sets.

## Preprocessing (src/preprocess.py, default source = RealSign Training)
- MediaPipe HandLandmarker (tasks API, `models/hand_landmarker.task`; legacy solutions fallback in Colab).
  21 x (x,y,z) = 63 dims, wrist-relative, missing = zeros.
- Local verification (26x10=260): feature (260,63), no-hand 6/260 (2.3%), splits 182/39/39 (labels A-Z).
  Sample RF accuracy 0.949 (vs 0.90 on Hindi sample — cleaner data).
- Full (Colab): RealSign ships 700/200/100 train/test/val — use as-is (signer-diverse) or 70/15/15 re-split;
  signer-independent via 4 signers; hash leakage check (0 overlap).
- Outputs: `data/processed/{X_train,X_val,X_test,y_train,y_val,y_test}.npy`, `labels.txt` (A-Z), `meta.txt`.
- Screenshot: `screenshots/mediapipe_demo.png` from `Training/A/0.jpg`.
- Run: `python src/eda.py` then `python src/preprocess.py --source sample` (quick) or `--source full`.
