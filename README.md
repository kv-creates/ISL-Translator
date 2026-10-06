# ISL Translator Project — Indian Sign Language to Text Real-Time Translator

**Author:** Krishna Vishwakarma, Roll No: 4848  
**Goal:** Real-time ISL fingerspelling → text using MediaPipe landmarks + CNN-BiLSTM, deployed in Flutter.

## Project Structure
```
ISL_Translator_Project/
├── data/
│   ├── raw/          # real downloaded datasets (not committed if > GitHub limit)
│   └── processed/    # .npy MediaPipe features (70/15/15 split)
├── notebooks/
│   └── ISL_Training_Colab.ipynb  # training on Google Colab
├── src/
│   ├── download_data.py
│   ├── verify_data.py
│   ├── eda.py
│   ├── preprocess.py
│   └── generate_report.py
├── models/           # isl_model.h5 + isl_model.tflite (from Colab)
├── app/              # Flutter app isl_translator_app
├── report/
│   └── final_report.docx
└── screenshots/      # EDA plots, confusion matrix, app UI
```

## Phase 1 — Datasets (NO synthetic data, real only)

| # | Dataset | Source | Classes / Size | Download |
|---|---------|--------|----------------|----------|
| 1 | ISL Fingerspelling Image Dataset | IEEE DataPort `isl-fingerspelling-image-dataset` | 35 classes (A-Z + 1-9), ~400/class, >14,000 images, 3 signers | https://ieee-dataport.org/documents/isl-fingerspelling-image-dataset — requires IEEE DataPort login/subscription. Manual download → place in `data/raw/isl-fingerspelling/` |
| 2 | ISL-Hindi Character Dataset | Kaggle `krishbhagat/indian-sign-language-hindi` (= `krish09bha/isl-hindi-character-dataset` alias, 48,000 imgs, 40 Hindi chars ×1200, 48×48) + HF mirror `KRISH09bha/Hindi-Indian-Sign-language-dataset-ISL` | 40 classes, 1200/class | `python src/download_data.py` or manual from https://www.kaggle.com/datasets/krishbhagat/indian-sign-language-hindi |
| 3 | Sentence-level ISL (ISH-News derived) | Kaggle `drblack00/isl-csltr-indian-sign-language-dataset` (ISL-CSLTR: 700 videos, 100 sentences, 7 signers, 18863 frames) + Continuous Fingerspelling `https://kirandevraj.github.io/ISL-Fingerspelling/` (1308 segs, 499 videos) | sentence-level | `python src/download_data.py` |
| Alt | Indian Sign Language (A-Z, MediaPipe) | Kaggle `prekshapalva/indian-sign-language` (26 dirs, ~2000/class, 3.85GB) / `prathumarikeri/indian-sign-language-isl` | 26 classes | fallback if above fails |

### Quick download (Git Bash / PowerShell)
```bash
cd ISL_Translator_Project
pip install -r requirements.txt
python src/download_data.py
python src/verify_data.py
```

Kaggle public datasets work via `kagglehub` without `kaggle.json`. IEEE DataPort requires manual login.
If `kagglehub` fails (no internet/auth), manually download zips and unzip into `data/raw/`:
- `data/raw/isl-fingerspelling/`
- `data/raw/isl-hindi/`
- `data/raw/isl-csltr/`

Then run `python src/verify_data.py` to print class counts.

## Phase 2 — EDA & Preprocessing
```bash
python src/eda.py
python src/preprocess.py
```
Outputs `.npy` in `data/processed/`, plots in `screenshots/`.

## Phase 3 — Colab Training
1. Upload `notebooks/ISL_Training_Colab.ipynb` to https://colab.research.google.com
2. Upload `data/processed/*.npy` (or mount Drive)
3. Runtime → Run all. Trains RF, SVM, CNN, CNN-BiLSTM + tuning.
4. Download `isl_model.tflite` + `isl_model.h5` → place in `models/`.

## Phase 4 — Flutter App
```bash
cd app
flutter create isl_translator_app
flutter pub get
flutter run
```

## Phase 5 — Report
```bash
python src/generate_report.py
# → report/final_report.docx (Times New Roman 12pt body / 14pt headings, page break per H1, no Streamlit)
```

## Phase 6 — GitHub
```bash
git add .
git commit -m "Complete ISL Translator Project: Datasets, Training, Flutter App, and Report"
# create repo ISL-Translator on GitHub, then:
git remote add origin <MY_GITHUB_REPO_URL>
git push -u origin main
```
