# EDA Findings & Preprocessing Summary (Phase 2)

Source: real ISL-Hindi Character Dataset (`krishbhagat/indian-sign-language-hindi`, 48000 files).
Cache: `~/.cache/kagglehub/datasets/krishbhagat/indian-sign-language-hindi/versions/1/HindiSignImages48x48`
Sample: `data/raw/isl-hindi-sample/` (200 files, 5/class) for quick local runs.

## EDA (src/eda.py)
- **Classes:** 40 (Devanagari: अ आ इ ई उ ए ऐ ओ क क्ष ख ग घ च छ ज ज्ञ झ ट ठ ड ढ ण त थ द ध न प फ ब भ म य र ल व श स ह + variants) × **1200 images/class = 48000 total**. Balanced.
- **Plot:** `screenshots/eda_class_distribution.png` — flat 1200/class bar chart.
- **Samples:** `screenshots/eda_samples.png` — 5 random images × 8 classes.
- **Missing values:** none (folder structure complete, no empty class).
- **Corrupted images:** 0/48000 (PIL verify passed).
- **Image size:** 128×128 actual (dataset advertises 48×48 — mismatch documented).
- **Duplicates (critical):** 1410 hash groups, 46584 extra files (~97% duplicates, filenames contain "Copy"). Dataset appears augmented by file-copy, not independent captures. **Action:** md5 dedup before train/val/test split in Colab; otherwise leakage inflates accuracy. Sample subset: 41 groups / 159 extra.
- **Other sets:** IEEE ISL Fingerspelling (35 classes, ~14k, manual download, `data/raw/isl-fingerspelling/WHERE_IS_DATA.txt`); ISL-CSLTR sentence-level 700 videos/100 sentences (8.29GB, Colab-only, `data/raw/isl-csltr/WHERE_IS_DATA.txt`); continuous fingerspelling https://kirandevraj.github.io/ISL-Fingerspelling/ (1308 segs).

## Preprocessing (src/preprocess.py)
- **Method:** MediaPipe HandLandmarker (tasks API, `models/hand_landmarker.task` auto-downloaded; legacy `solutions.hands` fallback in Colab with `mediapipe==0.10.14`). 21 landmarks × (x,y,z) = 63 dims, wrist-relative (minus lm0), missing hand = 63 zeros.
- **Local verification (sample, 200 files):** feature matrix (200,63), no-hand 0/200 (100% detection on 128px). Splits: train 140 / val 30 / test 30 (random fallback; stratified needs ≥6/class).
- **Full (Colab):** dedup → ~1400 unique + augment → 70/15/15 stratified; signer-independent: Hindi set lacks signer IDs, so use contributor-held-out when available (ISL-CSLTR has 7 signers; fingerspelling has 3 individuals) + hash-level leakage check (no md5 overlap across splits).
- **Outputs:** `data/processed/{X_train,X_val,X_test,y_train,y_val,y_test}.npy`, `labels.txt`, `meta.txt`.
- **Screenshot:** `screenshots/mediapipe_demo.png` — landmark overlay verified on real sample.
- Run: `python src/eda.py` then `python src/preprocess.py --source sample` (quick) or `--source full` (Colab/overnight).

## Leakage & Quality KPIs
- Data Quality KPI: 0% corrupt, 100% hand-detection, duplicates removed (target <1% cross-split overlap).
- Next: `notebooks/ISL_Training_Colab.ipynb` trains RF/SVM/CNN/CNN-BiLSTM on deduped `.npy`.
