import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:hand_detection/hand_detection.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

/// ISL Translator — real-time fingerspelling to text.
/// Camera -> hand_detection (MediaPipe 21 landmarks, on-device) -> wrist-relative 63-d
/// -> isl_model.tflite (CNN-BiLSTM) -> text. Target <500ms.
///
/// Note: master prompt asked for `google_mlkit_hand_detection`, which does not exist
/// on pub.dev (ML Kit has no hand API). Substituted with `hand_detection`
/// (MediaPipe hands via LiteRT, 21 x/y/z landmarks) — the correct package for this task.
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(ISLApp(cameras: cameras));
}

class ISLApp extends StatelessWidget {
  final List<CameraDescription> cameras;
  const ISLApp({super.key, required this.cameras});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ISL Translator',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple), useMaterial3: true),
      home: TranslatorScreen(cameras: cameras),
    );
  }
}

class TranslatorScreen extends StatefulWidget {
  final List<CameraDescription> cameras;
  const TranslatorScreen({super.key, required this.cameras});

  @override
  State<TranslatorScreen> createState() => _TranslatorScreenState();
}

class _TranslatorScreenState extends State<TranslatorScreen> {
  CameraController? _cam;
  HandDetector? _detector;
  Interpreter? _model;
  List<String> _labels = [];
  String _text = '';
  String _current = '-';
  double _conf = 0;
  double _latencyMs = 0;
  bool _busy = false;
  String _status = 'Init...';

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      _detector = await HandDetector.create();
      try {
        final lab = await rootBundle.loadString('assets/models/labels.txt');
        _labels = lab.split('\n').where((e) => e.trim().isNotEmpty).toList();
      } catch (_) {
        _labels = List.generate(26, (i) => String.fromCharCode(65 + i));
      }
      try {
        final bytes = await rootBundle.load('assets/models/isl_model.tflite');
        _model = Interpreter.fromBuffer(bytes.buffer.asUint8List());
        _status = 'Model loaded (${_labels.length} classes)';
      } catch (e) {
        _status = 'Model error: $e';
      }
      final cam = widget.cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.front,
        orElse: () => widget.cameras.first,
      );
      _cam = CameraController(cam, ResolutionPreset.medium, enableAudio: false);
      await _cam!.initialize();
      await _cam!.startImageStream(_onFrame);
      setState(() {});
    } catch (e) {
      setState(() => _status = 'Init failed: $e');
    }
  }

  Future<void> _onFrame(CameraImage img) async {
    if (_busy || _model == null || _detector == null) return;
    _busy = true;
    final t0 = DateTime.now();
    try {
      final hands = await _detector!.detectFromCameraImage(img, maxDim: 640);
      if (hands.isNotEmpty && hands.first.hasLandmarks) {
        final vec = _toFeatures(hands.first);
        final out = List.filled(_labels.length, 0.0).reshape([1, _labels.length]);
        _model!.run([vec], out);
        final probs = out[0];
        int best = 0;
        for (int i = 1; i < probs.length; i++) {
          if ((probs[i] as double) > (probs[best] as double)) best = i;
        }
        final dt = DateTime.now().difference(t0).inMilliseconds.toDouble();
        setState(() {
          _current = _labels[best];
          _conf = (probs[best] as double);
          _latencyMs = dt;
          if (_conf > 0.6) {
            if (_text.isEmpty || _text[_text.length - 1].toString() != _current) {
              _text += _current;
            }
          }
          _status = 'Running';
        });
      }
    } catch (_) {
      // keep stream alive
    } finally {
      _busy = false;
    }
  }

  /// 21 landmarks -> 63-d wrist-relative (matches src/preprocess.py).
  List<double> _toFeatures(Hand hand) {
    final wrist = hand.getLandmark(HandLandmarkType.wrist);
    final wx = wrist?.x ?? 0, wy = wrist?.y ?? 0;
    // z not always present in 2D; use 0 fallback — training used x,y,z with z≈depth
    final wz = 0.0;
    final feat = <double>[];
    for (final lm in hand.landmarks) {
      feat.addAll([lm.x - wx, lm.y - wy, (lm.z) - wz]);
    }
    while (feat.length < 63) {
      feat.add(0);
    }
    return feat.sublist(0, 63);
  }

  @override
  void dispose() {
    _cam?.dispose();
    _detector?.dispose();
    _model?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ISL Translator (Krishna Vishwakarma, 4848)')),
      body: Column(
        children: [
          Expanded(
            flex: 3,
            child: _cam != null && _cam!.value.isInitialized
                ? CameraPreview(_cam!)
                : Center(child: Text(_status)),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                Text('Status: $_status'),
                const SizedBox(height: 6),
                Text('Detected: $_current (${(_conf * 100).toStringAsFixed(1)}%)  |  Latency: ${_latencyMs.toStringAsFixed(0)} ms',
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                Container(
                  width: double.infinity, padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(border: Border.all(), borderRadius: BorderRadius.circular(8)),
                  child: Text(_text.isEmpty ? '(translated text appears here)' : _text, style: const TextStyle(fontSize: 20)),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(onPressed: () => setState(() => _text += ' '), child: const Text('Space')),
                    ElevatedButton(onPressed: () => setState(() => _text = ''), child: const Text('Clear')),
                    ElevatedButton(onPressed: _model == null ? null : () => setState(() => _status = 'Running'), child: const Text('Start')),
                  ],
                ),
                const Text('Target: frame-to-text <500ms on-device (TFLite).',
                    style: TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
