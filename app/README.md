# ISL Translator App (Flutter)

Real-time ISL fingerspelling → text. `lib/main.dart` verified with `flutter analyze`
(1 expected warning: `isl_model.tflite` pending from Colab).

## Deps (pubspec.yaml)
- `camera` (live feed), `hand_detection` (MediaPipe 21 landmarks on-device;
  substituted for non-existent `google_mlkit_hand_detection`), `tflite_flutter`
  (inference), `path_provider`.

## Install working APK (built 2026-10-07, debug, ~508MB with OpenCV natives)
APK (too large for GitHub, kept locally): `app/isl_translator_app/build/app/outputs/flutter-apk/app-debug.apk`
1. Copy it to your Android phone (USB / Drive / `adb install app-debug.apk`).
2. On phone: allow Install unknown apps → open APK → Install.
3. Open **ISL Translator** → allow Camera → show A-Z hand signs → text + confidence + ms.
4. Needs Android 8+ (minSdk per Flutter) and the bundled `isl_model.tflite` (already in assets).
Build fixes applied: `tensorflow-lite-select-tf-ops` dep (BiLSTM Flex ops), JVM 17 alignment
across plugin modules, `tflite_flutter ^0.12.0`. Rebuild: `flutter build apk --debug`
(requires ANDROID_HOME + cmake 3.22 + ninja on PATH; first build ~40min for OpenCV natives).
## Latency test (<500ms target)
App shows per-frame ms (capture→text) under the camera. Steps:
1. `flutter run --profile`, open DevTools.
2. Show 5 letters, record the Latency readout (TFLite, expect 50–150ms on mid-range Android).
3. Replace `screenshots/app_ui.png` + `app_camera_view.png` (currently wireframes) with real screenshots.
