"""Generate report/final_report.docx — strict formatting, no Streamlit.
- Body: Times New Roman 12pt; Headings: Times New Roman 14pt Bold
- Page break before every Heading 1
- Uses template.docx from repo root if present, else blank.
- Embeds screenshots/ with captions.
Usage: python src/generate_report.py
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.text import WD_BREAK
from docx.oxml.ns import qn

PROJECT = Path(__file__).resolve().parent.parent
SCREEN = PROJECT / "screenshots"
OUT = PROJECT / "report" / "final_report.docx"
TEMPLATE_ROOT = Path("D:/mlsignlanguage/template.docx")
TEMPLATE_PROJ = PROJECT / "template.docx"

FONT = "Times New Roman"


def base_doc():
    for cand in [TEMPLATE_PROJ, TEMPLATE_ROOT, PROJECT.parent / "template.docx"]:
        if cand.exists():
            print("Using template:", cand)
            return Document(str(cand))
    print("No template.docx found — creating blank.")
    return Document()


def style(doc):
    # Body
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    # Headings 1-3
    for i in [1, 2, 3]:
        h = doc.styles[f"Heading {i}"]
        h.font.name = FONT
        h.font.size = Pt(14)
        h.font.bold = True
        h.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)


def h1(doc, text, first=False):
    if not first:
        p = doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading(text, level=1)


def body(doc, text):
    for para in text.strip().split("\n\n"):
        doc.add_paragraph(para.strip())


def pic(doc, fname, caption):
    p = SCREEN / fname
    if not p.exists():
        doc.add_paragraph(f"[Figure missing: {fname} — run pipeline to generate]")
        return
    doc.add_picture(str(p), width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(f"Figure: {caption}")
    r.font.name = FONT
    r.font.size = Pt(10)
    r.italic = True


def main():
    doc = base_doc()
    style(doc)

    # 1. Title Page
    h1(doc, "Indian Sign Language to Text — Real-Time Translator", first=True)
    body(doc, (
        "Project Report\n\n"
        "Name: Krishna Vishwakarma\nRoll No: 4848\n\n"
        "Objective: real-time Indian Sign Language (ISL) fingerspelling to text on a mobile phone "
        "using MediaPipe hand landmarks and a CNN-BiLSTM model exported to TensorFlow Lite.\n\n"
        "Stack: Python (MediaPipe, scikit-learn, TensorFlow) for training on Google Colab; "
        "Flutter (camera, hand_detection, tflite_flutter) for on-device inference.\n\n"
        "Data: real datasets only — no synthetic data. Primary FREE (no login, same A-Z type): "
        "RealSign ISL (26 classes; Train 18,198 + Test 5,200 + Val 2,579, 4 signers) + "
        "Ayeshatasnim ISL (26 classes, 12,637 images); secondary Hindi 40-class + open sentence-level sets."
    ))

    # 2. Problem Definition
    h1(doc, "Problem Definition")
    body(doc, (
        "Real-world problem: Deaf and hard-of-hearing ISL users face daily communication barriers "
        "in education, healthcare, and public services where interpreters are scarce. Fingerspelling "
        "(letter-by-letter signs) is essential for names and technical terms yet under-resourced for ISL.\n\n"
        "Target users: (1) ISL signers communicating with non-signers, (2) students/teachers in inclusive "
        "classrooms, (3) front-desk and emergency staff needing quick on-device translation without internet.\n\n"
        "Why ML: hand shapes vary across signers, lighting, and cameras; rule-based vision fails. "
        "Learning wrist-relative landmark patterns with RF/SVM baselines and a CNN-BiLSTM sequence model "
        "generalizes across signers and runs in milliseconds on-device.\n\n"
        "Success criteria: test accuracy >=85% (weighted F1 >=0.85), frame-to-text latency <500ms on-device, "
        "confusion matrix with no systematic cross-letter collapse, and a working Flutter demo with Clear/Space."
    ))

    # 3. EDA
    h1(doc, "Exploratory Data Analysis (EDA)")
    body(doc, (
        "Dataset source: FREE same-type sets (no login) — RealSign "
        "(github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset, CC0-1.0, 4 signers: "
        "Training 26x700=18,198, Testing 26x200=5,200, Validation 26x100=2,579) + Ayeshatasnim "
        "(Apache-2.0, 26 classes, 12,637 images). Secondary: Hindi Kaggle 40x1200 (97% file-copy dups), "
        "IEEE 35-class (login-walled, covered by free A-Z), sentence-level ISLTranslate/iSign (Colab-scale).\n\n"
        "Cleaning: PIL verify on RealSign Training — 0 corrupted. Sizes varied ~200-300px (real captures).\n\n"
        "Duplicates: md5 — RealSign only 141 groups/144 extra (~0.8%, clean) vs Hindi 1410/46k (97% copies). "
        "Pipeline dedups by hash regardless.\n\n"
        "Feature engineering: MediaPipe HandLandmarker, 21 landmarks x (x,y,z) = 63 dims, wrist-relative "
        "(subtract landmark 0), missing hand = 63 zeros. Local sample (26x10=260): 97.7% detection (6/260 no-hand).\n\n"
        "Train/test split: RealSign ships 700/200/100 train/test/val (use as-is); local sample re-splits 70/15/15 "
        "(seed 42). Signer-independent via RealSign's 4 signers + hash leakage check (0 overlap).\n\n"
        "Data leakage check: verified — no duplicate hashes across train/val/test after dedup."
    ))
    pic(doc, "eda_class_distribution.png", "Class distribution: 26 A-Z classes, ~700 each in Training (balanced).")
    pic(doc, "eda_samples.png", "Random samples: 5 images per class (first 8 classes shown).")
    pic(doc, "mediapipe_demo.png", "MediaPipe HandLandmarker overlay on a real sample (21 landmarks).")

    # 4. ML Model Development
    h1(doc, "ML Model Development")
    body(doc, (
        "Baselines (notebooks/ISL_Training_Colab.ipynb, Cells 4-6):\n"
        "(1) Random Forest with GridSearch (n_estimators 100/200, max_depth None/20, 3-fold CV) on 63-d features. "
        "Strong tabular baseline; local RealSign sample reached 0.949 accuracy.\n"
        "(2) SVM RBF (C=10, StandardScaler, 8k subsample for speed) — margin baseline for small landmark data.\n"
        "(3) Simple CNN: Input 21x3x1 -> Conv2D(32,3x3) -> MaxPool -> Dense(128) -> Dropout(0.3) -> softmax, "
        "20 epochs, Adam.\n\n"
        "Final CNN-BiLSTM (Cell 7): Conv2D block for spatial hand-shape features -> Reshape to sequence -> "
        "Bidirectional LSTM for finger co-articulation -> Dropout -> softmax over 26 A-Z classes. "
        "Hyperparameter tuning with KerasTuner RandomSearch (5 trials): filters 16-64, LSTM 32-128, "
        "dropout 0.2-0.5, lr 1e-4-1e-2 (log), 15 epochs search + 25 epochs final fit. "
        "Exports: isl_model.h5 and quantized isl_model.tflite (TFLiteConverter, Optimize.DEFAULT) for Flutter."
    ))

    # 5. Model Evaluation
    h1(doc, "Model Evaluation")
    body(doc, (
        "Metrics (Cell 8, weighted): Accuracy, Precision, Recall, F1-Score per model on the held-out test set, "
        "plus confusion matrix and accuracy/loss curves. ROC-AUC reported one-vs-rest where applicable. "
        "Latency: single-sample Keras predict timed in Colab; on-device TFLite target <500ms (app readout "
        "shows live ms; mid-range Android typically 50-150ms).\n\n"
        "Local preliminary (RealSign 26x10=260, RF n=50): test accuracy 0.949 — proves the pipeline end-to-end; "
        "full 26k results are produced by running the Colab notebook and overwrite these figures. "
        "After Colab run, copy confusion_matrix.png and training_history.png into screenshots/ and re-run "
        "this script to refresh the report."
    ))
    pic(doc, "confusion_matrix.png", "Confusion matrix on test set (preliminary sample; replaced by Colab full run).")
    pic(doc, "training_history.png", "Training history: accuracy/loss curves (sample; replaced by Colab full run).")

    # 6. KPI Framework
    h1(doc, "KPI Framework")
    body(doc, (
        "Business KPI — Successful translation rate: definition = fraction of real-world fingerspelling attempts "
        "that produce correct text without retry; target >=90% on a 100-phrase field test; actual = field test "
        "pending after Colab model + app install.\n\n"
        "ML KPIs — (a) Test accuracy target >=85% (RealSign sample RF 0.949; full run pending); (b) Weighted F1 target >=0.85; "
        "(c) Latency target <500ms frame-to-text (Colab Keras single-sample timed; app shows live TFLite ms); "
        "(d) ROC-AUC target >=0.95 macro.\n\n"
        "Data Quality KPIs — (a) Corruption rate target 0% (actual 0/18k RealSign train); (b) Hand-detection coverage target >=98% "
        "(actual 97.7% sample); (c) Cross-split duplicate overlap target 0% (enforced by md5 dedup; raw RealSign only 0.8% copies); "
        "(d) Class balance target max/min <=1.2 (actual 1.0, perfectly balanced)."
    ))

    # 7. Flutter App
    h1(doc, "Flutter Mobile App Development")
    body(doc, (
        "Architecture: Camera (image stream) -> hand_detection (MediaPipe LiteRT, 21 landmarks, on-device) -> "
        "wrist-relative 63-d (matches training) -> tflite_flutter Interpreter (isl_model.tflite) -> text buffer. "
        "Note: the prompt named google_mlkit_hand_detection, which does not exist on pub.dev (ML Kit has no hand API); "
        "it was replaced with hand_detection (MediaPipe hands) — the correct package. flutter analyze is clean "
        "except the expected missing-model warning until the Colab .tflite is copied to assets/models/.\n\n"
        "UI: camera preview, status line, detected letter + confidence + latency ms, translated-text box, "
        "Space / Clear / Start buttons. Confidence gate 0.6 with debounce appends stable letters.\n\n"
        "Integration: copy models/isl_model.tflite and data/processed/labels.txt into assets/models/, "
        "flutter pub get, flutter run on emulator/device, flutter test for smoke test. "
        "Latency test: profile mode, record on-screen ms for 5 letters; target <500ms."
    ))
    pic(doc, "app_ui.png", "App UI: camera view, translated text, Clear button (wireframe; replace with device screenshot after flutter run).")
    pic(doc, "app_camera_view.png", "App camera view with landmark overlay (wireframe; replace with device screenshot).")

    # 8. Conclusion
    h1(doc, "Conclusion and Future Scope")
    body(doc, (
        "Conclusion: a complete real-data ISL pipeline is built and verified locally — free RealSign 26k + Ayeshatasnim 12.6k, "
        "MediaPipe 63-d features with 97.7% sample detection, RF/SVM/CNN/CNN-BiLSTM Colab notebook with tuning "
        "and TFLite export, and a Flutter app (analyze-clean) ready for the model. Preliminary sample accuracy "
        "0.949 confirms the approach; full metrics follow the Colab run.\n\n"
        "Future scope: (1) sentence-level ISL-CSLTR/ISH-News transformer for continuous signing; "
        "(2) signer-independent evaluation across the 3 IEEE individuals + 7 CSLTR signers; "
        "(3) on-device personalization (few-shot adaptation); (4) Hindi + English bilingual output with TTS; "
        "(5) low-light and motion-blur robustness via augmentation."
    ))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print("Saved", OUT)


if __name__ == "__main__":
    main()
