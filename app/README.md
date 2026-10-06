# ISL Translator App (Flutter)

Real-time ISL fingerspelling → text. `lib/main.dart` verified with `flutter analyze`
(1 expected warning: `isl_model.tflite` pending from Colab).

## Deps (pubspec.yaml)
- `camera` (live feed), `hand_detection` (MediaPipe 21 landmarks on-device;
  substituted for non-existent `google_mlkit_hand_detection`), `tflite_flutter`
  (inference), `path_provider`.

## Run
```bash
cd app/isl_translator_app
flutter pub get
# 1. Copy Colab outputs:
#    models/isl_model.tflite -> assets/models/isl_model.tflite
#    data/processed/labels.txt -> assets/models/labels.txt
flutter run   # emulator or device
flutter test  # smoke test
```
## Latency test (<500ms target)
App shows per-frame ms (capture→text) under the camera. Steps:
1. `flutter run --profile`, open DevTools.
2. Show 5 letters, record the Latency readout (TFLite, expect 50–150ms on mid-range Android).
3. Replace `screenshots/app_ui.png` + `app_camera_view.png` (currently wireframes) with real screenshots.
