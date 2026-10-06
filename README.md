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

## Phase 1 — Datasets (NO synthetic data, real only — FREE first)

| # | Dataset | Source | Classes / Size | Download |
|---|---------|--------|----------------|----------|
| 0 FREE | RealSign ISL A-Z (primary, same type) | GitHub `RealSign62/RealSign-Indian-Sign-Language-Dataset` (CC0-1.0, 4 signers) | 26 classes; Train 26×700 (18,198) + Test 26×200 (5,200) + Val 26×100 (2,579) | `python src/download_data.py --free` or https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset → `data/raw/free-isl-realsign/` |
| 0 FREE | Ayeshatasnim ISL A-Z (same type) | GitHub `ayeshatasnim-h/Indian-Sign-Language-dataset` (Apache-2.0) | 26 classes × ~486 = 12,637 images | `python src/download_data.py --free` or https://github.com/ayeshatasnim-h/Indian-Sign-Language-dataset → `data/raw/free-isl-ayeshatasnim/` |
| 0 FREE | HF Indian SL (parquet, same type) | HuggingFace `Hemg/Indian_sign_language_dataset` (42.7k rows, 292MB) / `akritRihal/Indian_Sign_Language_dataset` (10.8k) | image+label | `huggingface_hub` or https://huggingface.co/datasets/Hemg/Indian_sign_language_dataset |
| 0 FREE | ISLTranslate / iSign (sentence-level) | `exploration-lab/isltranslate` (31k pairs) / https://exploration-lab.github.io/iSign/ (118k) | sentence-level | open links, Colab-scale |
| 1 | ISL Fingerspelling Image Dataset (optional) | IEEE DataPort `isl-fingerspelling-image-dataset` | 35 classes, ~14k, 3 signers | https://ieee-dataport.org/documents/isl-fingerspelling-image-dataset — login required. Free sets above already cover A-Z. |
| 2 | ISL-Hindi Character Dataset | Kaggle `krishbhagat/indian-sign-language-hindi` (48,000 imgs, 40 ×1200) | 40 classes | `python src/download_data.py --hindi` |
| 3 | ISL-CSLTR sentence-level | Kaggle `drblack00/isl-csltr-indian-sign-language-dataset` (700 videos, 8.29GB) | sentence-level | Colab only: `python src/download_data.py --csltr` |

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
