import 'package:flutter_test/flutter_test.dart';
import 'package:bixolon_printer/bixolon_printer.dart';
import 'package:bixolon_printer/bixolon_printer_platform_interface.dart';
import 'package:bixolon_printer/bixolon_printer_method_channel.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';

class MockBixolonPrinterPlatform
    with MockPlatformInterfaceMixin
    implements BixolonPrinterPlatform {
  @override
  Future<List<Object?>> findBluetoothPrinter() {
    throw UnimplementedError();
  }
}

void main() {
  final BixolonPrinterPlatform initialPlatform =
      BixolonPrinterPlatform.instance;

  test('$MethodChannelBixolonPrinter is the default instance', () {
    expect(initialPlatform, isInstanceOf<MethodChannelBixolonPrinter>());
  });
}
