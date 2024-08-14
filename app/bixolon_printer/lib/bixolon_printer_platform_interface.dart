import 'package:plugin_platform_interface/plugin_platform_interface.dart';

import 'bixolon_printer_method_channel.dart';

abstract class BixolonPrinterPlatform extends PlatformInterface {
  /// Constructs a BixolonPrinterPlatform.
  BixolonPrinterPlatform() : super(token: _token);

  static final Object _token = Object();

  static BixolonPrinterPlatform _instance = MethodChannelBixolonPrinter();

  /// The default instance of [BixolonPrinterPlatform] to use.
  ///
  /// Defaults to [MethodChannelBixolonPrinter].
  static BixolonPrinterPlatform get instance => _instance;

  /// Platform-specific implementations should set this with their own
  /// platform-specific class that extends [BixolonPrinterPlatform] when
  /// they register themselves.
  static set instance(BixolonPrinterPlatform instance) {
    PlatformInterface.verifyToken(instance, _token);
    _instance = instance;
  }

  Future<List<Object?>> findBluetoothPrinter();

  Future<bool> connectPrinter(String address);

  Future<bool> printQr(
    String image,
    bool isTransparent,
    int x,
    int y,
    int width,
    int threshold,
    int ditheringType,
    int compressType,
    int rotation,
  );
}
