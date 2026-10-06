// ISL Translator smoke test — verifies app builds (camera mocked as empty list).
import 'package:flutter_test/flutter_test.dart';
import 'package:isl_translator_app/main.dart';

void main() {
  testWidgets('ISL app builds', (WidgetTester tester) async {
    await tester.pumpWidget(const ISLApp(cameras: []));
    expect(find.textContaining('ISL Translator'), findsOneWidget);
  });
}
